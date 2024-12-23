# tests/test_assistant.py
import pytest
from unittest.mock import Mock, patch
from yaart.llm import ResumeAssistant
from yaart.models import JobDescription, TailoredResume, JobRequirements
import json

class TestResumeAssistant:
    def test_parse_jd(self, mock_llm, sample_jd_dict):
        """Test job description parsing"""
        with patch('yaart.llm.PydanticOutputParser') as mock_parser_cls:
            # Create a mock chain that returns the proper result
            mock_chain = Mock()
            mock_chain.invoke = Mock(return_value=JobDescription(**sample_jd_dict))
            
            # Mock the LLM to return our mock chain when combined with parser
            mock_llm.__or__ = Mock(return_value=mock_chain)
            
            assistant = ResumeAssistant(llm=mock_llm)
            result = assistant.parse_jd(
                "Software Engineer job...",
                "https://example.com/job"
            )
            
            assert isinstance(result, JobDescription)
            assert result.url == "https://example.com/job"
            assert result.role == "Software Engineer"

    def test_tailor_resume(self, mock_llm, sample_resume, sample_jd, sample_resume_dict):
        """Test resume tailoring"""
        with patch('yaart.llm.PydanticOutputParser') as mock_parser_cls:
            # Create a mock chain that returns the parsed resume
            mock_chain = Mock()
            mock_response = Mock()
            mock_response.content = json.dumps(sample_resume_dict)
            mock_chain.invoke = Mock(return_value=mock_response)
            
            # Mock the LLM to return our mock chain
            mock_llm.__or__ = Mock(return_value=mock_chain)
            
            # Mock the resume parser
            mock_parser = Mock()
            mock_parser.parse = Mock(return_value=TailoredResume(**sample_resume_dict))
            mock_parser.get_format_instructions = Mock(return_value="")
            mock_parser_cls.return_value = mock_parser
            
            assistant = ResumeAssistant(llm=mock_llm)
            assistant.resume_parser = mock_parser
            
            result = assistant.tailor_resume(sample_resume, sample_jd)
            
            assert isinstance(result, str)
            assert "John Doe" in result
            assert "Software Engineer" in result