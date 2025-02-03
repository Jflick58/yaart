PARSE_JD_PROMPT = """
Extract the key information from the following job description into a structured format.
Focus on accurately identifying:

1. Role/title
2. Company name
3. Location
4. Key responsibilities (as a list)
5. Required skills, experience, and education requirements
6. Salary information (if available)
7. Benefits offered
8. Any other relevant information

Job Description:
{text}

{format_instructions}
"""

TAILOR_RESUME_PROMPT = """
Analyze the provided resume and job description to create a tailored version of the resume.
Follow these specific guidelines:

1. Summary Section:
   - Modify the summary to follow this template: "[Title] with [N-years] of experience in [industry if relevant]. Some career highlights include: [Projects/accomplishments relevant to JD's responsibilities]. I would like to leverage my experience to [outcome the role is looking for] at [company name and its goal/product type]" 
   - Explicitly mention the company name in a meaningful way
   - Focus on achievements that directly relate to the job requirements
   - Highlight the most relevant technical skills from your experience

2. Skills Section:
   - Reorganize skills to prioritize those mentioned in the job description
   - Add any relevant skills from your experience that match the job requirements
   - Ensure all technical skills mentioned in your experience bullets are listed here
   - Group skills by categories that align with the job requirements

3. Experience Section:
   - Limit to maximum 8 bullet points per role, focusing on most relevant achievements.
   - Integrate specific technical skills into bullet points (e.g., change "Implemented a website" to "Implemented a React-based website with Node.js backend")
   - Prioritize experiences that demonstrate:
     * Required technical skills
     * Similar responsibilities
     * Relevant industry experience
     * Leadership or project management (if required)
   - Quantify achievements where possible (%, $, time saved, etc.)
   - Use action verbs that match the job description's language
   - Include specific tools, technologies, and methodologies mentioned in the job requirements

4. Education Section:
   - Highlight relevant coursework or projects that align with the job requirements
   - Emphasize technical certifications or specialized training that match the role

5. Language and Keywords:
   - Use similar terminology as the job description
   - Include specific technical terms, tools, and methodologies mentioned
   - Maintain professional language while incorporating industry-specific terms

Important:
1. Include ALL experience entries from the original resume, even if they're older
3. You may prioritize and tailor the content, but do not omit entire jobs
4. Maintain the original structure while tailoring content to the job requirements

Resume:
{resume}

Job Description:
{job_description}

{format_instructions}

Remember to:
- Keep all information truthful and accurate
- Maintain chronological order
- Ensure technical terms are used accurately and in context
- Focus on accomplishments rather than just responsibilities
- Demonstrate impact and results

Return the tailored resume information in the specified JSON structure.
""" # noqa: E501