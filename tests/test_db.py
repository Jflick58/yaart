import pytest
import sqlite3
import json
from yaart.db import JobDatabase
from yaart.models import JobDescription, JobRequirements

@pytest.fixture
def sample_job_description():
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
def db():
    # Use in-memory database for testing
    with sqlite3.connect(':memory:') as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Create schema
        cursor.execute('''
            CREATE TABLE descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                role TEXT,
                company TEXT,
                location TEXT,
                responsibilities TEXT,
                skills_requirements TEXT,
                salary TEXT,
                benefits TEXT,
                other_information TEXT
            )
        ''')
        conn.commit()
        
        yield JobDatabase()

def test_save_and_get_job_description(db, sample_job_description):
    # Save job description
    db.save_job_description(sample_job_description)
    
    # Retrieve and verify
    result = db.get_job_description(sample_job_description.url)
    
    assert result is not None
    assert result.url == sample_job_description.url
    assert result.role == sample_job_description.role
    assert result.company == sample_job_description.company
    assert result.requirements.skills == sample_job_description.requirements.skills

def test_get_nonexistent_job_description(db):
    result = db.get_job_description("https://nonexistent.com/job")
    assert result is None

def test_update_existing_job_description(db, sample_job_description):
    # Save initial version
    db.save_job_description(sample_job_description)
    
    # Update job description
    updated_jd = sample_job_description.model_copy()
    updated_jd.role = "Senior Software Engineer"
    db.save_job_description(updated_jd)
    
    # Verify update
    result = db.get_job_description(sample_job_description.url)
    assert result.role == "Senior Software Engineer"
