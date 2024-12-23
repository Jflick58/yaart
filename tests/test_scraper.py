# tests/test_scraper.py
import pytest
from unittest.mock import Mock, patch
from yaart.scraper import JobScraper
from yaart.llm import ResumeAssistant
from yaart.models import JobDescription

@pytest.mark.asyncio
class TestJobScraper:
    async def test_scrape_job_description(self, mock_llm, sample_jd_dict):
        """Test job description scraping"""
        with patch('httpx.AsyncClient') as mock_client:
            # Mock HTTP response
            mock_response = Mock()
            mock_response.text = "<html>Software Engineer job...</html>"
            mock_response.raise_for_status = Mock()
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Create a mock chain that returns the proper result
            mock_chain = Mock()
            mock_chain.invoke = Mock(return_value=JobDescription(**sample_jd_dict))
            
            # Mock the LLM to return our mock chain when combined with parser
            mock_llm.__or__ = Mock(return_value=mock_chain)
            
            with patch('yaart.llm.PydanticOutputParser') as mock_parser_cls:
                assistant = ResumeAssistant(llm=mock_llm)
                scraper = JobScraper(assistant)
                
                result = await scraper.scrape_job_description("https://example.com/job")
                
                assert isinstance(result, JobDescription)
                assert result.url == "https://example.com/job"

    async def test_scrape_invalid_url(self, mock_llm):
        """Test error handling for invalid URLs"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = ValueError("Invalid URL")
            
            scraper = JobScraper(ResumeAssistant(llm=mock_llm))
            with pytest.raises(ValueError):
                await scraper.scrape_job_description("invalid-url")