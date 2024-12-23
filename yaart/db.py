import sqlite3
from contextlib import contextmanager
from typing import Optional
import json
from yaart.models import JobDescription

@contextmanager 
def get_db_connection():
    conn = sqlite3.connect('jobs.db')
    try:
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        conn.close()

class JobDatabase:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        """Initialize the database schema if it doesn't exist"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS descriptions (
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

    def save_job_description(self, job_description: JobDescription):
        """Save job description to database"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO descriptions (
                    url, role, company, location, responsibilities,
                    skills_requirements, salary, benefits, other_information
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_description.url,
                job_description.role,
                job_description.company,
                job_description.location,
                json.dumps(job_description.responsibilities),
                json.dumps(job_description.requirements.model_dump()),
                job_description.salary,
                json.dumps(job_description.benefits),
                json.dumps(job_description.other_information)
            ))
            conn.commit()

    def get_job_description(self, url: str) -> Optional[JobDescription]:
        """Retrieve job description from database"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT * FROM descriptions WHERE url = ?''',
                (url,)
            )
            row = cursor.fetchone()
            
            if row:
                return JobDescription(
                    url=row['url'],
                    role=row['role'],
                    company=row['company'], 
                    location=row['location'],
                    responsibilities=json.loads(row['responsibilities']),
                    requirements=json.loads(row['skills_requirements']),
                    salary=row['salary'],
                    benefits=json.loads(row['benefits']),
                    other_information=json.loads(row['other_information'])
                )
            return None