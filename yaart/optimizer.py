from pathlib import Path
from typing import Optional, Dict, Tuple
from md2pdf.core import md2pdf # type: ignore
from yaart.llm import ResumeAssistant
from yaart.scraper import JobScraper
from yaart.db import JobDatabase
from yaart.models import JobDescription
from langchain.base_language import BaseLanguageModel
from pydantic import SecretStr

class ResumeOptimizer:
    def __init__(self, llm: Optional[BaseLanguageModel] = None, 
                 api_key: Optional[SecretStr] = None):
        self.assistant = ResumeAssistant(llm=llm, api_key=api_key)
        self.scraper = JobScraper(assistant=self.assistant)
        self.db = JobDatabase()

    def validate_paths(
        self, 
        base_resume_path: Path,
        output_dir: Path
    ) -> Tuple[Path, Path]:
        """Validate input and output paths exist"""
        if not base_resume_path.exists():
            raise FileNotFoundError(f"Resume file not found: {base_resume_path}")

        markdown_dir = output_dir / "Markdown"
        pdf_dir = output_dir / "PDF"
        
        if not all(d.exists() for d in [output_dir, markdown_dir, pdf_dir]):
            raise ValueError(
                "Output directory structure invalid. Ensure directories exist: "
                f"{output_dir}, {markdown_dir}, {pdf_dir}"
            )
            
        return markdown_dir, pdf_dir

    async def get_job_description(
        self,
        jd_url: str,
        jd_string: Optional[str] = None
    ) -> JobDescription:
        """Get job description from string, database, or by scraping"""
        try:
            if jd_string:
                job_description = self.assistant.parse_jd(jd_string, jd_url)
                self.db.save_job_description(job_description)
                return job_description

            # Try database first
            job_description = self.db.get_job_description(jd_url) # type: ignore
            if job_description is not None:
                return job_description

            # Scrape if not in database
            job_description = await self.scraper.scrape_job_description(jd_url)
            if not job_description:
                raise ValueError("Failed to scrape job description")
            
            self.db.save_job_description(job_description)
            return job_description

        except Exception as e:
            raise ValueError(f"Failed to process job description: {str(e)}")

    def generate_documents(
        self,
        tailored_resume: str,
        company: str,
        markdown_dir: Path,
        pdf_dir: Path,
        css_path: Optional[Path] = None
    ) -> Tuple[Path, Path]:
        """Generate markdown and PDF versions of the resume"""
        # Save markdown version
        markdown_path = markdown_dir / f"{company}.md"
        markdown_path.write_text(tailored_resume)

        # Generate PDF
        try:
            pdf_path = pdf_dir / f"Resume_{company}.pdf"
            if css_path and css_path.exists():
                md2pdf(
                    str(pdf_path),
                    md_content=tailored_resume,
                    css_file_path=str(css_path),
                )
            else:
                md2pdf(
                    str(pdf_path),
                    md_content=tailored_resume,
                )
            return markdown_path, pdf_path
        except Exception as e:
            raise ValueError(f"Failed to generate PDF: {str(e)}")

    async def optimize_resume(
        self,
        company: str,
        jd_url: str,
        base_resume_path: Path,
        output_dir: Path = Path("."),
        jd_string: Optional[str] = None,
        css_path: Optional[Path] = None
    ) -> Dict:
        """
        Optimize resume for a specific job description.
        
        Args:
            company: Company name for file naming
            jd_url: URL of the job description
            base_resume_path: Path to the base resume markdown file
            output_dir: Directory for output files
            jd_string: Optional raw job description text
            css_path: Optional path to CSS file for PDF styling
        
        Returns:
            Dict containing optimization results
        """
        # Validate paths
        markdown_dir, pdf_dir = self.validate_paths(base_resume_path, output_dir)
        
        # Read base resume
        resume_content = base_resume_path.read_text()

        # Get job description
        job_description = await self.get_job_description(jd_url, jd_string)

        # Tailor resume
        try:
            tailored_resume = self.assistant.tailor_resume(
                resume_content,
                job_description
            )
        except Exception as e:
            raise ValueError(f"Failed to tailor resume: {str(e)}")

        # Generate output files
        markdown_path, pdf_path = self.generate_documents(
            tailored_resume,
            company,
            markdown_dir,
            pdf_dir,
            css_path
        )

        return {
            "company": company,
            "role": job_description.role,
            "markdown_path": str(markdown_path),
            "pdf_path": str(pdf_path),
            "job_description": job_description.model_dump()
        }
