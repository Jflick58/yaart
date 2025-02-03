import httpx
from typing import Optional
from bs4 import BeautifulSoup
from yaart.models import JobDescription
from yaart.llm import ResumeAssistant

class JobScraper:
    def __init__(self, assistant: Optional[ResumeAssistant] = None):
        self.assistant = assistant or ResumeAssistant()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' \
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def scrape_job_description(self, url: str) -> JobDescription:
        """Scrape and parse job description from URL"""
        try:
            async with httpx.AsyncClient(
                headers=self.headers, follow_redirects=True) as client:
                response = await client.get(url)
                await response.aread()
                
                # Parse HTML and extract main content
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Extract text content
                text = soup.get_text()
                
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  ")) # noqa: E501
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                return self.assistant.parse_jd(text, url)
                
        except httpx.HTTPError as e:
            raise ValueError(f"Failed to fetch job description: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to process job description: {str(e)}")