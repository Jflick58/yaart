from pathlib import Path
from typing import Optional, Dict
from md2pdf.core import md2pdf
from yaart.llm import ResumeAssistant
from yaart.scraper import JobScraper
from yaart.db import JobDatabase
from yaart.models import JobDescription
from langchain.base_language import BaseLanguageModel

class ResumeOptimizer:
    def __init__(self, llm: Optional[BaseLanguageModel] = None, api_key: Optional[str] = None):
        self.assistant = ResumeAssistant(llm=llm, api_key=api_key)
        self.scraper = JobScraper(assistant=self.assistant)
        self.db = JobDatabase()
        
        # Ensure output directories exist
        Path("Markdown").mkdir(exist_ok=True)
        Path("PDF").mkdir(exist_ok=True)

    async def optimize_resume(
        self,
        company: str,
        jd_url: str,
        base_resume_path: Path,
        output_dir: Path = Path("."),
        jd_string: Optional[str] = None,
        css_path: Optional[Path] = Path("styles.css")
    ) -> Dict:
        """
        Optimize resume for a specific job description.
        
        Args:
            company: Company name for file naming
            jd_url: URL of the job description
            base_resume_path: Path to the base resume markdown file
            output_dir: Directory for output files
            jd_string: Optional raw job description text if URL scraping fails
            css_path: Path to CSS file for PDF styling
        
        Returns:
            Dict containing optimization results
        """
        # Read base resume
        if not base_resume_path.exists():
            raise FileNotFoundError(f"Resume file not found: {base_resume_path}")
        
        resume_content = base_resume_path.read_text()

        # Get job description
        try:
            if jd_string:
                # Parse raw job description string
                job_description = self.assistant.parse_jd(jd_string, jd_url)
                self.db.save_job_description(job_description)
            else:
                # Try to get from database first
                job_description = self.db.get_job_description(jd_url)
                if not job_description:
                    # Scrape and parse if not in database
                    job_description = await self.scraper.scrape_job_description(jd_url)
                    self.db.save_job_description(job_description)
        except Exception as e:
            raise ValueError(f"Failed to process job description: {str(e)}")

        # Tailor resume
        try:
            tailored_resume = self.assistant.tailor_resume(
                resume_content,
                job_description
            )
        except Exception as e:
            raise ValueError(f"Failed to tailor resume: {str(e)}")

        # Save markdown version
        markdown_path = output_dir / "Markdown" / f"{company}.md"
        markdown_path.write_text(tailored_resume)

        # Generate PDF
        try:
            pdf_path = output_dir / "PDF" / f"Resume_{company}.pdf"
            if css_path.exists():
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
        except Exception as e:
            raise ValueError(f"Failed to generate PDF: {str(e)}")

        return {
            "company": company,
            "role": job_description.role,
            "markdown_path": str(markdown_path),
            "pdf_path": str(pdf_path),
            "job_description": job_description.model_dump()
        }