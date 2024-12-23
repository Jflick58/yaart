# tests/test_optimizer.py
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from yaart import ResumeOptimizer
from yaart.models import TailoredResume, JobDescription
import json

class TestResumeOptimizer:
    @pytest.mark.asyncio
    async def test_optimize_resume_with_url(self, mock_llm, mock_db, mock_scraper, tmp_path, sample_resume, sample_resume_dict):
        """Test resume optimization with job URL"""
        
        # Set up test files
        resume_path = tmp_path / "resume.md"
        resume_path.write_text(sample_resume)
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "Markdown").mkdir()
        (output_dir / "PDF").mkdir()

        # Create a mock chain that returns the parsed resume
        mock_chain = Mock()
        mock_response = Mock()
        mock_response.content = json.dumps(sample_resume_dict)
        mock_chain.invoke = Mock(return_value=mock_response)
        mock_llm.__or__ = Mock(return_value=mock_chain)

        # Mock the resume parser in ResumeAssistant
        with patch('yaart.llm.PydanticOutputParser') as mock_parser_cls:
            mock_parser = Mock()
            mock_parser.parse = Mock(return_value=TailoredResume(**sample_resume_dict))
            mock_parser.get_format_instructions = Mock(return_value="")
            mock_parser_cls.return_value = mock_parser

            # Create optimizer with mocks
            optimizer = ResumeOptimizer(llm=mock_llm)
            optimizer.db = mock_db
            optimizer.scraper = mock_scraper
            optimizer.assistant.resume_parser = mock_parser
            
            # Mock md2pdf
            with patch('yaart.optimizer.md2pdf'):
                result = await optimizer.optimize_resume(
                    company="test-co",
                    jd_url="https://example.com/job",
                    base_resume_path=resume_path,
                    output_dir=output_dir
                )

            assert "test-co.md" in result["markdown_path"]
            assert "Resume_test-co.pdf" in result["pdf_path"]
            mock_db.save_job_description.assert_called_once()