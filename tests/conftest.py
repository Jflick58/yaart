# tests/conftest.py
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from yaart.models import JobDescription, JobRequirements, TailoredResume
from yaart.db import JobDatabase
from yaart.scraper import JobScraper
import json

@pytest.fixture
def sample_resume():
    return """# John Doe
**Software Engineer**
San Francisco, CA | 123-456-7890 | john@email.com | github.com/john | linkedin.com/in/john

## Summary
Software Engineer with 5 years experience...

## Skills
Python, JavaScript, SQL

## Experience
**Software Engineer**
Previous Company | 2020-Present
- Built scalable systems
- Wrote clean code
"""

@pytest.fixture
def sample_jd():
    return JobDescription(
        url="https://example.com/job",
        role="Software Engineer",
        company="Test Company",
        location="Remote",
        responsibilities=["Build scalable systems", "Write clean code"],
        requirements=JobRequirements(
            skills=["Python", "SQL"],
            experience=["3+ years software development"],
            education=["Bachelor's in CS or related"]
        ),
        salary="$120k-150k",
        benefits=["Health insurance", "401k"],
        other_information={"culture": "Fast-paced startup"}
    )

@pytest.fixture
def sample_jd_dict():
    return {
        "url": "https://example.com/job",
        "role": "Software Engineer",
        "company": "Test Company",
        "location": "Remote",
        "responsibilities": ["Build scalable systems"],
        "requirements": {
            "skills": ["Python"],
            "experience": ["3+ years"],
            "education": ["BS in CS"]
        },
        "salary": "120k",
        "benefits": ["Health"],
        "other_information": {}
    }

@pytest.fixture
def sample_resume_dict():
    return {
        "name": "John Doe",
        "title": "Software Engineer",
        "location": "San Francisco, CA",
        "phone": "1234567890",
        "email": "john@email.com",
        "github": "github.com/john",
        "linkedin": "linkedin.com/in/john",
        "summary": "Software Engineer with 5 years...",
        "education": [],
        "skills": [{"category": "Programming", "skills": ["Python"]}],
        "experience": [{
            "title": "Software Engineer",
            "company": "Test Co",
            "location": "SF",
            "dates": "2020-Present",
            "bullets": ["Built systems"]
        }]
    }

@pytest.fixture
def mock_llm(sample_jd_dict, sample_resume_dict):
    mock = Mock()
    
    # Create mock responses
    jd_response = MagicMock()
    jd_response.content = json.dumps(sample_jd_dict)
    
    resume_response = MagicMock()
    resume_response.content = json.dumps(sample_resume_dict)

    def mock_invoke(inputs):
        if "text" in inputs:  # parse_jd
            return jd_response
        else:  # tailor_resume
            return resume_response

    mock.invoke = Mock(side_effect=mock_invoke)
    mock.__or__ = Mock(return_value=mock)
    
    return mock

@pytest.fixture
def mock_db():
    db = Mock(spec=JobDatabase)
    db.get_job_description = Mock(return_value=None)
    db.save_job_description = Mock()
    return db

@pytest.fixture
def mock_scraper(sample_jd):
    scraper = Mock(spec=JobScraper)
    scraper.scrape_job_description = AsyncMock(return_value=sample_jd)
    return scraper