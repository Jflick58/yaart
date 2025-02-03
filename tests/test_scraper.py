import pytest
from unittest.mock import AsyncMock, patch
import httpx
from yaart.scraper import JobScraper
from yaart.models import JobDescription, JobRequirements

@pytest.fixture
def mock_job_description():
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
def mock_assistant():
    with patch('yaart.scraper.ResumeAssistant') as mock:
        return mock

@pytest.mark.asyncio
async def test_scrape_job_description_html_parsing(mock_assistant):
    """Test HTML content parsing"""
    # Create scraper with mock assistant
    scraper = JobScraper(assistant=mock_assistant)
    
    # Mock response with HTML content
    mock_response = AsyncMock()
    mock_response.text = """
        <html>
            <head>
                <script>var x = 'should be removed';</script>
                <style>body { color: red; }</style>
            </head>
            <body>
                <div>Software Engineer Position</div>
                <script>var y = 'also removed';</script>
            </body>
        </html>
    """
    mock_response.raise_for_status = AsyncMock()
    
    # Setup mock client
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response
    
    # Configure assistant mock
    mock_job_description = JobDescription(
        url="https://example.com/job",
        role="Software Engineer",
        company="TestCo",
        location="Remote",
        responsibilities=["Code"],
        requirements=JobRequirements(
            skills=["Python"],
            experience=["5+ years"],
            education=["BS in Computer Science"]
        ),
        salary=None,
        benefits=[],
        other_information={}
    )
    mock_assistant.parse_jd.return_value = mock_job_description
    
    # Execute test
    with patch('httpx.AsyncClient', return_value=mock_client):
        result = await scraper.scrape_job_description("https://example.com/job")
    
    # Verify results
    assert result == mock_job_description
    # Verify that script and style content was removed
    assert "should be removed" not in mock_assistant.parse_jd.call_args[0][0]
    assert "also removed" not in mock_assistant.parse_jd.call_args[0][0]
    assert "Software Engineer Position" in mock_assistant.parse_jd.call_args[0][0]


@pytest.mark.asyncio
async def test_scrape_job_description_http_error(mock_assistant):
    # Setup mock client to raise HTTPError
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.get.side_effect = httpx.HTTPError("Failed to fetch")
    
    # Create scraper instance
    scraper = JobScraper(assistant=mock_assistant)
    
    # Execute test
    with patch('httpx.AsyncClient', return_value=mock_client), \
         pytest.raises(ValueError) as exc_info:
        await scraper.scrape_job_description("https://example.com/job")
    
    assert "Failed to fetch job description" in str(exc_info.value)

@pytest.mark.asyncio
async def test_scrape_job_description_parsing_error(mock_assistant):
    # Setup mock response
    mock_response = AsyncMock()
    mock_response.text = "<html>Invalid job description</html>"
    mock_response.raise_for_status = AsyncMock()
    await mock_response.raise_for_status()  # Properly await the mock
    
    # Setup mock client
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.get.return_value = mock_response
    
    # Setup assistant mock to raise error
    mock_assistant.parse_jd.side_effect = ValueError("Failed to parse")
    
    # Create scraper instance
    scraper = JobScraper(assistant=mock_assistant)
    
    # Execute test
    with patch('httpx.AsyncClient', return_value=mock_client), \
         pytest.raises(ValueError) as exc_info:
        await scraper.scrape_job_description("https://example.com/job")
    
    assert "Failed to process job description" in str(exc_info.value)
