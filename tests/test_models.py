import pytest
from yaart.models import (
    JobRequirements,
    JobDescription,
    Education,
    Experience,
    Skill,
    Publication,
    OpenSourceProject,
    TailoredResume
)

def test_job_requirements():
    req = JobRequirements(
        skills=["Python", "AWS"],
        experience=["5+ years"],
        education=["BS in Computer Science"]
    )
    assert req.skills == ["Python", "AWS"]
    assert req.experience == ["5+ years"]
    assert req.education == ["BS in Computer Science"]

def test_job_description():
    jd = JobDescription(
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
    
    assert jd.url == "https://example.com/job"
    assert jd.role == "Software Engineer"
    assert isinstance(jd.requirements, JobRequirements)
    assert jd.salary == "$100k-$150k"

def test_education():
    edu = Education(
        degree="BS Computer Science",
        institution="Test University",
        dates="08/2015 - 05/2019",
        location="San Francisco, CA"
    )
    
    assert edu.degree == "BS Computer Science"
    assert edu.institution == "Test University"
    assert edu.dates == "08/2015 - 05/2019"
    assert edu.location == "San Francisco, CA"

def test_experience():
    exp = Experience(
        title="Software Engineer",
        company="Tech Corp",
        location="San Francisco, CA",
        dates="06/2019 - Present",
        bullets=["Developed Python applications"],
        company_description="Leading tech company"
    )
    
    assert exp.title == "Software Engineer"
    assert exp.company == "Tech Corp"
    assert len(exp.bullets) == 1
    assert exp.company_description == "Leading tech company"

def test_skill():
    skill = Skill(
        category="Programming Languages",
        skills=["Python", "JavaScript", "Java"]
    )
    
    assert skill.category == "Programming Languages"
    assert len(skill.skills) == 3
    assert "Python" in skill.skills

def test_publication():
    pub = Publication(
        journal="Test Journal",
        title="Test Publication",
        date="January 2024"
    )
    
    assert pub.journal == "Test Journal"
    assert pub.title == "Test Publication"
    assert pub.date == "January 2024"

def test_open_source_project():
    proj = OpenSourceProject(
        name="Test Project",
        description="A test open source project"
    )
    
    assert proj.name == "Test Project"
    assert proj.description == "A test open source project"

def test_tailored_resume():
    resume = TailoredResume(
        name="John Doe",
        title="Software Engineer",
        location="San Francisco, CA",
        phone="1234567890",
        email="john@example.com",
        github="github.com/johndoe",
        linkedin="linkedin.com/in/johndoe",
        summary="Software Engineer with 5+ years of experience...",
        education=[
            Education(
                degree="BS Computer Science",
                institution="Test University",
                dates="08/2015 - 05/2019",
                location="San Francisco, CA"
            )
        ],
        skills=[
            Skill(
                category="Programming Languages",
                skills=["Python", "JavaScript"]
            )
        ],
        experience=[
            Experience(
                title="Software Engineer",
                company="Tech Corp",
                location="San Francisco, CA",
                dates="06/2019 - Present",
                bullets=["Developed Python applications"]
            )
        ]
    )
    
    assert resume.name == "John Doe"
    assert len(resume.education) == 1
    assert len(resume.skills) == 1
    assert len(resume.experience) == 1
    
    # Test markdown generation
    markdown = resume.to_markdown()
    assert "John Doe" in markdown
    assert "Software Engineer" in markdown
    assert "Test University" in markdown
    assert "Tech Corp" in markdown

def test_tailored_resume_optional_fields():
    # Test resume with optional publications and open source projects
    resume = TailoredResume(
        name="John Doe",
        title="Software Engineer",
        location="San Francisco, CA",
        phone="1234567890",
        email="john@example.com",
        github="github.com/johndoe",
        linkedin="linkedin.com/in/johndoe",
        summary="Summary...",
        education=[
            Education(
                degree="BS Computer Science",
                institution="Test University",
                dates="08/2015 - 05/2019"
            )
        ],
        skills=[
            Skill(
                category="Programming Languages",
                skills=["Python"]
            )
        ],
        experience=[
            Experience(
                title="Software Engineer",
                company="Tech Corp",
                location="Remote",
                dates="06/2019 - Present",
                bullets=["Test"]
            )
        ],
        publications=[
            Publication(
                journal="Test Journal",
                title="Test Publication",
                date="January 2024"
            )
        ],
        open_source=[
            OpenSourceProject(
                name="Test Project",
                description="Description"
            )
        ]
    )
    
    markdown = resume.to_markdown()
    assert "Publications" in markdown
    assert "Open-Source Contributions" in markdown
    assert "Test Journal" in markdown
    assert "Test Project" in markdown
