from typing import Optional
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.base_language import BaseLanguageModel
from pydantic import SecretStr
from yaart.models import JobDescription, TailoredResume
from yaart.prompts import PARSE_JD_PROMPT, TAILOR_RESUME_PROMPT
import json

class ResumeAssistant:
    def __init__(self, llm: Optional[BaseLanguageModel] = None, 
                 api_key: Optional[SecretStr] = None):
        if llm:
            self.llm = llm
        elif api_key:
            self.llm = ChatOpenAI(temperature=0.2, model="gpt-4o", api_key=api_key)
        else:
            raise ValueError("Either llm or api_key must be provided")
        self.jd_parser = PydanticOutputParser(pydantic_object=JobDescription)
        self.resume_parser = PydanticOutputParser(pydantic_object=TailoredResume)

    def parse_jd(self, text: str, url: str) -> JobDescription:
        """Parse job description text into structured format"""
        prompt = PromptTemplate(
            template=PARSE_JD_PROMPT,
            input_variables=["text"],
            partial_variables={
                "format_instructions": self.jd_parser.get_format_instructions()
                }
        )

        try:
            chain = prompt | self.llm | self.jd_parser
            result = chain.invoke({"text": text})
            if isinstance(result, dict) and "text" in result:
                result = self.jd_parser.invoke(result["text"])
            if not isinstance(result, JobDescription):
                raise ValueError("Parser did not return a JobDescription object")
            result.url = url
            return result
        except Exception as e:
            raise ValueError(f"Failed to parse job description: {str(e)}")

    def tailor_resume(self, resume_content: str, 
                      job_description: JobDescription) -> str:
        """Tailor resume content to match job description"""
        prompt = PromptTemplate(
            template=TAILOR_RESUME_PROMPT,
            input_variables=["resume", "job_description"],
            partial_variables={
                "format_instructions": self.resume_parser.get_format_instructions()
                }
        )

        try:
            chain = prompt | self.llm
            result = chain.invoke({
                "resume": resume_content,
                "job_description": job_description.model_dump_json(),
            })
            
            print("\n=== Debug: LLM Output ===")
            content = result.get("text", "{}")
            print(json.dumps(content, indent=2))
            print("=======================\n")
            
            tailored_resume = self.resume_parser.parse(content)
            
            print("\n=== Debug: Parsed Resume Structure ===")
            print(json.dumps(tailored_resume.model_dump(), indent=2))
            print("================================\n")
            
            return tailored_resume.to_markdown()
        except Exception as e:
            print("\n=== Debug: Error Details ===")
            print(f"Error type: {type(e)}")
            print(f"Error message: {str(e)}")
            if hasattr(e, '__cause__'):
                print(f"Caused by: {e.__cause__}")
            print("========================\n")
            raise ValueError(f"Failed to tailor resume: {str(e)}")