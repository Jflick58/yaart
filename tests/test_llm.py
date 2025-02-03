import pytest
from unittest.mock import Mock, patch, MagicMock
from yaart.llm import ResumeAssistant
from yaart.models import JobDescription, JobRequirements, TailoredResume
from langchain.schema import HumanMessage, AIMessage
from langchain_core.outputs import LLMResult
from langchain.schema.runnable import RunnableParallel
from langchain.output_parsers import PydanticOutputParser
import json

@pytest.fixture
def mock_llm():
    mock = MagicMock()
    mock.__or__ = lambda self, other: other
    return mock

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
def sample_tailored_resume_dict():
    return {
        "name": "John Doe",
        "title": "Software Engineer",
        "location": "San Francisco, CA",
        "phone": "1234567890", 
        "email": "john@example.com",
        "github": "github.com/johndoe",
        "linkedin": "linkedin.com/in/johndoe",
        "summary": "Software Engineer with 5+ years of experience...",
        "education": [{
            "degree": "BS Computer Science",
            "institution": "Test University", 
            "dates": "08/2015 - 05/2019",
            "location": "San Francisco, CA"
        }],
        "skills": [{
            "category": "Programming Languages",
            "skills": ["Python", "JavaScript"]
        }],
        "experience": [{
            "title": "Software Engineer",
            "company": "Tech Corp",
            "location": "San Francisco, CA", 
            "dates": "06/2019 - Present",
            "bullets": ["Developed Python applications"]
        }]
    }

def test_resume_assistant_init_no_args():
    """Test ResumeAssistant initialization with no arguments"""
    with pytest.raises(ValueError) as exc_info:
        ResumeAssistant()  
    assert "Either llm or api_key must be provided" in str(exc_info.value)

def test_resume_assistant_initialization():
    with pytest.raises(ValueError):
        ResumeAssistant()  
    assistant = ResumeAssistant(api_key="test-key")
    assert assistant.llm is not None
    
    mock_llm = Mock()
    assistant = ResumeAssistant(llm=mock_llm)
    assert assistant.llm == mock_llm

def test_resume_assistant_init_with_api_key():
    """Test ResumeAssistant initialization with API key"""
    assistant = ResumeAssistant(api_key="test-key")
    assert assistant.llm is not None
    assert isinstance(assistant.jd_parser, PydanticOutputParser)
    assert isinstance(assistant.resume_parser, PydanticOutputParser)

@patch('yaart.llm.PydanticOutputParser')
@patch('yaart.llm.PromptTemplate')
def test_parse_jd_success(mock_prompt, mock_parser, mock_llm, sample_job_description):
    mock_prompt_instance = MagicMock()
    mock_prompt_instance.__or__ = lambda self, other: other
    mock_prompt.return_value = mock_prompt_instance
    
    mock_parser_instance = MagicMock()
    mock_parser_instance.get_format_instructions.return_value = "format instructions"
    mock_parser_instance.parse.return_value = sample_job_description
    mock_parser_instance.invoke = MagicMock(return_value=sample_job_description)
    mock_parser.return_value = mock_parser_instance
    
    mock_llm.__or__ = lambda self, other: other
    mock_llm.invoke.return_value = { "text": sample_job_description.model_dump_json() }
    
    assistant = ResumeAssistant(llm=mock_llm)
    assistant.jd_parser = mock_parser_instance
    
    result = assistant.parse_jd("Sample job description text", "https://example.com/job")
    
    assert isinstance(result, JobDescription)
    assert result.url == "https://example.com/job"
    assert result.role == "Software Engineer"
    
    mock_parser_instance.invoke.assert_called_once()

def test_parse_jd_chain_error(mock_llm):
    mock_llm.invoke.side_effect = Exception("Chain execution failed")

    assistant = ResumeAssistant(llm=mock_llm)
    with pytest.raises(ValueError) as exc_info:
        assistant.parse_jd("Invalid text", "https://example.com/job")
    
    assert "Failed to parse job description" in str(exc_info.value)

def test_parse_jd_invalid_response(mock_llm):
    mock_response = {"text": "Invalid response"}
    mock_llm.invoke.return_value = mock_response

    assistant = ResumeAssistant(llm=mock_llm)
    
    mock_parser = MagicMock()
    mock_parser.parse.side_effect = ValueError("Invalid format")
    mock_parser.get_format_instructions.return_value = "format instructions"
    assistant.jd_parser = mock_parser

    with pytest.raises(ValueError) as exc_info:
        assistant.parse_jd("Sample text", "https://example.com/job")
    
    assert "Failed to parse job description" in str(exc_info.value)

@patch('yaart.llm.PydanticOutputParser')
@patch('yaart.llm.PromptTemplate')
def test_tailor_resume_success(mock_prompt, mock_parser, mock_llm, sample_job_description, sample_tailored_resume_dict):
    mock_tailored_resume = MagicMock()
    mock_tailored_resume.to_markdown.return_value = "# Tailored Resume"
    mock_tailored_resume.model_dump.return_value = sample_tailored_resume_dict
    
    mock_prompt_instance = MagicMock()
    mock_prompt_instance.__or__ = lambda self, other: other
    mock_prompt.return_value = mock_prompt_instance
    
    mock_parser_instance = MagicMock()
    mock_parser_instance.get_format_instructions.return_value = "format instructions"
    mock_parser_instance.parse.return_value = mock_tailored_resume
    mock_parser.return_value = mock_parser_instance
    
    mock_llm.__or__ = lambda self, other: other
    mock_llm.invoke.return_value = {"text": json.dumps(sample_tailored_resume_dict)}
    
    assistant = ResumeAssistant(llm=mock_llm)
    assistant.resume_parser = mock_parser_instance
    result = assistant.tailor_resume(
            "Original resume content",
            sample_job_description
        )
    
    assert isinstance(result, str)
    assert "Tailored Resume" in result
    assert mock_llm.invoke.called

def test_tailor_resume_failure(mock_llm, sample_job_description):
    mock_llm.invoke.side_effect = Exception("Tailoring failed")
    
    assistant = ResumeAssistant(llm=mock_llm)
    with pytest.raises(ValueError) as exc_info:
        assistant.tailor_resume(
            "Original resume content",
            sample_job_description
        )
    
    assert "Failed to tailor resume" in str(exc_info.value)
