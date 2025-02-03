# YAART - Yet Another AI Resume Tool

Python package that leverages AI to automatically tailor your resume to specific job descriptions, optimizing your resume content to highlight relevant skills and experiences.

[![lint](https://github.com/jflick58/wasm_exec/actions/workflows/lint.yml/badge.svg)](https://github.com/jflick58/yaart/actions/workflows/lint.yml)
[![test](https://github.com/jflick58/yaart/actions/workflows/test.yml/badge.svg)](https://github.com/jflick58/wasm_exec/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/Jflick58/yaart/graph/badge.svg?token=2Q7NWW2F1U)](https://codecov.io/gh/Jflick58/yaart)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

### Features: 
- Generates editable Markdown files so you can modify the AI-optimized resume. 
- LLM-powered scraper for pulling job descriptions. 
- Supports custom CSS styles when generating a PDF resume. 
- Stores all jobs in a sqllite database so you can track your applications. 
- Leverages Pydantic output parsing for consistent generation. 
- Intended to be plug-and-play with different models - succesfully tested with o1-preview, gpt-4o, and claude-3-5-sonnet-20241022

**Note: I built this for my own use - sharing in case it is useful to others.**

## Installation

```bash
pip install yaart
```

## Quick Start

1. Create `base_resume.md` following the `sample.md` template in the `Markdown` folder

2. 
```python
import asyncio
import os
from pathlib import Path
from langchain_openai import ChatOpenAI
from yaart import optimize_resume

# Job description text (optional if providing URL)
jd_text = """
Optional text in case the scraper fails...
"""

async def main():
    # Initialize LLM (GPT-4 Optimized)
    llm = ChatOpenAI(
        model="gpt-4o",  # GPT-4 Optimized is default
        temperature=0.2,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    result = await optimize_resume(
        llm=llm,
        company="ExampleCorp",
        jd_url="https://example.com/job-posting",
        base_resume_path="path/to/base_resume.md",
        jd_string=jd_text,  # Optional, will scrape from URL if not provided
        output_dir=Path("output")  # Optional, defaults to current directory
    )
    
    print(f"Generated files:")
    print(f"Markdown: {result['markdown_path']}")
    print(f"PDF: {result['pdf_path']}")
    print(f"Role: {result['role']}")

if __name__ == "__main__":
    asyncio.run(main())
```

3. (Optional) If you want to modify your generated markdown resume, find it in the generated `Markdown` directory. Once you would like to generate a PDF from it, run the following: 

```python 
from md2pdf.core import md2pdf

if __name__ == "__main__":
    md2pdf("PDF/sample.pdf",
        md_file_path="Markdown/sample.md",
        css_file_path="styles.css",
    )
```

## Prerequisites  

- Python 3.8+
- LangChain compatible LLM (OpenAI, Anthropic, etc.)
- Base resume in markdown format

## How It Works

1. **Job Description Analysis**: 
   - Extracts key requirements, skills, and responsibilities
   - Structures information into standardized format
   - Caches parsed results in local SQLite database

2. **Resume Optimization**:
   - Matches skills and experience with job requirements
   - Prioritizes relevant achievements
   - Incorporates key technical terms and phrases
   - Maintains professional tone and factual accuracy

3. **Output Generation**:
   - Creates tailored Markdown version
   - Generates styled PDF using custom CSS
   - Preserves original resume structure

## License

MIT

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.


