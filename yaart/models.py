from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class JobRequirements(BaseModel):
    skills: List[str] = Field(
        description="Required technical skills and competencies, including programming"\
             "languages, tools, and technologies"
    )
    experience: List[str] = Field(
        description="Required years and types of experience, including specific " \
        "domains or roles"
    )
    education: List[str] = Field(
        description="Required education qualifications, including degrees," \
        " certifications, and specific fields of study"
    )


class JobDescription(BaseModel):
    url: str = Field(description="URL of the job posting for reference")
    role: str = Field(description="Job title/role as listed in the posting")
    company: str = Field(description="Company name offering the position")
    location: str = Field(
        description="Job location, including city, state, or remote status"
    )
    responsibilities: List[str] = Field(
        description="Key job responsibilities and duties listed in the posting"
    )
    requirements: JobRequirements = Field(
        description="Structured job requirements including skills, experience, and" \
        "education"
    )
    salary: Optional[str] = Field(
        description="Salary information or range if provided in the posting",
        default=None,
    )
    benefits: List[str] = Field(
        description="Company benefits and perks offered with the position"
    )
    other_information: Dict[str, str] = Field(
        description="Additional relevant information about the role or company"
    )


class Education(BaseModel):
    degree: str = Field(
        description="Full degree title including any concentration or specialization"
    )
    institution: str = Field(description="Name of the educational institution")
    dates: str = Field(
        description="Date range of attendance in MM/YYYY - MM/YYYY format"
    )
    location: Optional[str] = Field(
        description="Location of the institution (optional)", default=None
    )


class Experience(BaseModel):
    title: str = Field(description="Job title or position held")
    company: str = Field(description="Name of the company or organization")
    company_description: Optional[str] = Field(
        description="Brief description of the company, e.g., 'Fortune 500 Tech " \
        "Company' or 'Leading AI Startup'",
        default=None,
    )
    location: str = Field(description="Location of the job (city, state or 'Remote')")
    dates: str = Field(
        description="Employment duration in MM/YYYY - MM/YYYY format or 'Present' for "\
        "current positions"
    )
    bullets: List[str] = Field(
        description="""List of accomplishments and responsibilities, where each bullet:
        - Starts with an action verb
        - Includes specific technologies used
        - Quantifies impact where possible (%, $, time saved)
        - Demonstrates relevant skills from job description
        - Limited to 6 most relevant points"""
    )


class Skill(BaseModel):
    category: str = Field(
        description="Skill category/group name (e.g., 'Programming Languages', 'Cloud "\
        "Technologies')"
    )
    skills: List[str] = Field(
        description="List of specific skills within this category, prioritized based " \
        "on job requirements"
    )


class Publication(BaseModel):
    journal: str = Field(description="Name of the journal or publication venue")
    title: str = Field(description="Title of the published work")
    date: str = Field(description="Publication date in 'Month YYYY' format")


class OpenSourceProject(BaseModel):
    name: str = Field(description="Name of the open source project or repository")
    description: str = Field(
        description="Description of the project and your specific contributions"
    )


class TailoredResume(BaseModel):
    name: str = Field(description="Full name as it should appear on the resume")
    title: str = Field(description="Professional title aligned with the target role")
    location: str = Field(description="Current location (City, State)")
    phone: str = Field(description="Contact phone number in format: ##########")
    email: str = Field(description="Professional email address")
    github: str = Field(description="GitHub profile URL or username")
    linkedin: str = Field(description="LinkedIn profile URL or username")
    summary: str = Field(
        description="""Professional summary that follows this template:
        '[Title] with [N-years] of experience in [industry if relevant].
        Career highlights include: [2-3 major achievements relevant to job requirements]
        I would like to leverage my experience in [key skills] to [outcome the role is 
        looking for] at [company name and its goal/product type]'"""
    )
    education: List[Education] = Field(
        description="List of educational qualifications in reverse chronological order"
    )
    skills: List[Skill] = Field(
        description="""Grouped technical and professional skills where:
        - Skills are grouped into relevant categories
        - Skills mentioned in job description are prioritized
        - Each category contains related skills in order of relevance
        - Categories are ordered by importance to the role"""
    )
    experience: List[Experience] = Field(
        description="""Professional experience in reverse chronological order where:
        - Each role has maximum 6 bullet points
        - Bullets highlight achievements relevant to job requirements
        - Technical terms from job description are incorporated
        - Impact is quantified where possible
        - Company descriptions provide context about company size/type"""
    )
    publications: Optional[List[Publication]] = Field(
        description="Optional list of relevant publications", default=None
    )
    open_source: Optional[List[OpenSourceProject]] = Field(
        description="Optional list of relevant open source contributions", default=None
    )

    def to_markdown(self) -> str:
        """Convert the resume to markdown format"""
        md = f"""<h1 style="text-align:center;">{self.name}</h1>

<p style="text-align:center;font-weight:bold;">{self.title}</p>

<p style="text-align:center;">{self.location} | {self.phone} | {self.email} | {self.github} | {self.linkedin}</p>  

## Summary
{self.summary}

## Education
""" # noqa: E501
        # Education section
        for edu in self.education:
            md += f"**{edu.degree}**  \n_{edu.institution} | {edu.dates}_\n\n"

        # Skills section
        md += "## Skills\n"
        for skill in self.skills:
            md += f"**{skill.category}:** {', '.join(skill.skills)}\n\n"

        # Experience section
        md += "## Professional Experience\n"
        for exp in self.experience:
            company_desc = (
                f" _{exp.company_description} |" if exp.company_description else ""
            )
            md += f"**{exp.title}**  \n"
            md += f"**{exp.company}**{company_desc} {exp.location} | {exp.dates}_\n\n"
            for bullet in exp.bullets:
                md += f"- {bullet}\n"
            md += "\n"

        # Publications section (if any)
        if self.publications:
            md += "## Publications\n"
            for pub in self.publications:
                md += f"**{pub.journal}:** _{pub.title}_ ({pub.date})\n\n"

        # Open Source section (if any)
        if self.open_source:
            md += "## Open-Source Contributions\n"
            for project in self.open_source:
                md += f"**{project.name}:** {project.description}\n\n"

        return md.strip()
