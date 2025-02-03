import pytest
from pathlib import Path
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from yaart.optimizer import ResumeOptimizer
from yaart.models import JobDescription, JobRequirements
from yaart.scraper import JobScraper
from yaart.db import JobDatabase

@pytest.fixture
def mock_job_description():
    return JobDescription(
        url="https://example.com/job",
        role="Software Engineer",
        company="TestCo",
        location="Remote",
        responsibilities=["Code", "Test"],
        requirements=JobRequirements(
            skills=["Python", "AWS"],
            experience=["5+ years"],
            education=["BS in Computer Science"]
        ),
        salary="$100k-$150k",
        benefits=["Health", "401k"],
        other_information={"culture": "Great"}
    )

@pytest.fixture
def mock_optimizer():
    with patch('yaart.optimizer.ResumeAssistant') as mock_assistant, \
         patch('yaart.optimizer.JobScraper') as mock_scraper, \
         patch('yaart.optimizer.JobDatabase') as mock_db, \
         patch('yaart.optimizer.md2pdf') as mock_md2pdf:
        
        optimizer = ResumeOptimizer(api_key="test-key")
        optimizer.assistant = mock_assistant
        optimizer.scraper = mock_scraper
        optimizer.db = mock_db
        return optimizer

def test_resume_optimizer_init_with_llm():
    mock_llm = MagicMock()
    optimizer = ResumeOptimizer(llm=mock_llm)
    
    assert optimizer.assistant.llm == mock_llm
    assert isinstance(optimizer.scraper, JobScraper)
    assert isinstance(optimizer.db, JobDatabase)

def test_resume_optimizer_init_with_api_key():
    api_key = "test-key"
    optimizer = ResumeOptimizer(api_key=api_key)
    
    assert optimizer.assistant is not None
    assert isinstance(optimizer.scraper, JobScraper)
    assert isinstance(optimizer.db, JobDatabase)

def test_validate_paths_partial_structure(mock_optimizer, tmp_path):
    base_resume = tmp_path / "base_resume.md"
    base_resume.write_text("# Test Resume")
    
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    (output_dir / "Markdown").mkdir()
    with pytest.raises(ValueError) as exc_info:
        mock_optimizer.validate_paths(base_resume, output_dir)
    
    assert "Output directory structure invalid" in str(exc_info.value)
    assert "PDF" in str(exc_info.value)
@pytest.mark.asyncio
async def test_optimize_resume_output_dir_creation(tmp_path):
    mock_llm = MagicMock()
    optimizer = ResumeOptimizer(llm=mock_llm)
    base_resume = tmp_path / "base_resume.md"
    base_resume.write_text("# Test Resume")
    
    output_dir = tmp_path / "output" 
    output_dir.mkdir()
    
    with pytest.raises(ValueError) as exc_info:
        await optimizer.optimize_resume(
        company="TestCo",
        jd_url="https://example.com/job",
        base_resume_path=base_resume,
        output_dir=output_dir
    )
    
    assert "Output directory structure invalid" in str(exc_info.value)
@pytest.mark.asyncio
async def test_get_job_description_scraping_failure(mock_optimizer):
    mock_optimizer.db.get_job_description.return_value = None
    mock_optimizer.scraper.scrape_job_description = AsyncMock(return_value=None)
    with pytest.raises(ValueError) as exc_info:
        await mock_optimizer.get_job_description("https://example.com/job")
    assert "Failed to scrape job description" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_job_description_parsing_error(mock_optimizer):
    mock_optimizer.db.get_job_description.return_value = None
    mock_optimizer.scraper.scrape_job_description = AsyncMock(
        side_effect=Exception("Parsing failed")
        )
    
    with pytest.raises(ValueError) as exc_info:
        await mock_optimizer.get_job_description("https://example.com/job")
    assert "Failed to process job description" in str(exc_info.value)

def test_generate_documents_with_css(mock_optimizer, tmp_path):
    markdown_dir = tmp_path / "Markdown"
    pdf_dir = tmp_path / "PDF"
    markdown_dir.mkdir()
    pdf_dir.mkdir()
    
    css_path = tmp_path / "styles.css"
    css_path.write_text("body { font-family: Arial; }")
    
    markdown_path, pdf_path = mock_optimizer.generate_documents(
        "# Test Resume",
        "TestCo",
        markdown_dir,
        pdf_dir,
        css_path
    )
    
    assert markdown_path.exists()
    assert pdf_path.exists()
    assert markdown_path.read_text() == "# Test Resume"

def test_generate_documents_pdf_error(mock_optimizer, tmp_path):
    markdown_dir = tmp_path / "Markdown"
    pdf_dir = tmp_path / "PDF"
    markdown_dir.mkdir()
    pdf_dir.mkdir()
    
    with patch('yaart.optimizer.md2pdf', side_effect=Exception("PDF generation failed")):
        with pytest.raises(ValueError) as exc_info:
            mock_optimizer.generate_documents(
                "# Test Resume",
                "TestCo",
                markdown_dir,
                pdf_dir
            )
    assert "Failed to generate PDF" in str(exc_info.value)

@pytest.mark.asyncio
async def test_optimize_resume_tailor_error(mock_optimizer, mock_job_description, tmp_path):
    base_resume = tmp_path / "base_resume.md"
    base_resume.write_text("# Test Resume")
    
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "Markdown").mkdir()
    (output_dir / "PDF").mkdir()
    
    mock_optimizer.get_job_description = AsyncMock(return_value=mock_job_description)
    mock_optimizer.assistant.tailor_resume.side_effect = Exception("Tailoring failed")
    
    with pytest.raises(ValueError) as exc_info:
        await mock_optimizer.optimize_resume(
            company="TestCo",
            jd_url="https://example.com/job",
            base_resume_path=base_resume,
            output_dir=output_dir
        )
    assert "Failed to tailor resume" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_job_description_from_scraper(mock_optimizer, mock_job_description):
    mock_optimizer.db.get_job_description.return_value = None
    mock_optimizer.scraper.scrape_job_description = AsyncMock(return_value=mock_job_description)
    
    result = await mock_optimizer.get_job_description("https://example.com/job")
    
    assert result == mock_job_description
    assert mock_optimizer.scraper.scrape_job_description.called
    assert mock_optimizer.db.save_job_description.called

def test_generate_documents(mock_optimizer, tmp_path):
    markdown_dir = tmp_path / "Markdown"
    pdf_dir = tmp_path / "PDF"
    markdown_dir.mkdir()
    pdf_dir.mkdir()
    
    markdown_path, pdf_path = mock_optimizer.generate_documents(
        "# Test Resume",
        "TestCo",
        markdown_dir,
        pdf_dir
    )
    
    assert markdown_path.exists()
    assert pdf_path.exists()
    assert markdown_path.read_text() == "# Test Resume"

@pytest.mark.asyncio
async def test_optimize_resume_with_new_jd(mock_optimizer, mock_job_description, tmp_path):
    base_resume = tmp_path / "base_resume.md"
    base_resume.write_text("# Test Resume")
    
    output_dir = tmp_path / "output" 
    output_dir.mkdir()
    (output_dir / "Markdown").mkdir()
    (output_dir / "PDF").mkdir()
    
    mock_optimizer.db.get_job_description.side_effect = [None, mock_job_description]
    mock_optimizer.scraper.scrape_job_description = AsyncMock(return_value=mock_job_description)
    mock_optimizer.assistant.tailor_resume.return_value = "# Tailored Resume"
    
    result = await mock_optimizer.optimize_resume(
        company="TestCo",
        jd_url="https://example.com/job",
        base_resume_path=base_resume,
        output_dir=output_dir
    )
    
    assert result["company"] == "TestCo"
    assert result["role"] == "Software Engineer"
    assert mock_optimizer.scraper.scrape_job_description.called
    assert mock_optimizer.db.save_job_description.called
    
    markdown_path = output_dir / "Markdown" / "TestCo.md"
    assert markdown_path.exists()
    assert markdown_path.read_text() == "# Tailored Resume"

@pytest.mark.asyncio
async def test_optimize_resume_file_not_found(mock_optimizer):
    with pytest.raises(FileNotFoundError):
        await mock_optimizer.optimize_resume(
            company="TestCo",
            jd_url="https://example.com/job",
            base_resume_path=Path("nonexistent.md"),
            output_dir=Path(".")
        )