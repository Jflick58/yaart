# tests/test_db.py
import pytest
from yaart.db import JobDatabase

class TestJobDatabase:
    def test_save_and_get_job(self, sample_jd):
        """Test saving and retrieving job descriptions"""
        db = JobDatabase()
        
        # Save job
        db.save_job_description(sample_jd)
        
        # Retrieve job
        retrieved = db.get_job_description(sample_jd.url)
        
        assert retrieved is not None
        assert retrieved.role == sample_jd.role
        assert retrieved.company == sample_jd.company

    def test_get_nonexistent_job(self):
        """Test retrieving non-existent job"""
        db = JobDatabase()
        result = db.get_job_description("https://notfound.com")
        assert result is None