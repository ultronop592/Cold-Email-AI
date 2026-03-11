from langchain.prompts import PromptTemplate
from llm.groq_client import llm

template = """
Extract information from this resume.

Resume:
{resume}

Return:

skills
projects
experience
technologies
"""

prompt = PromptTemplate(
    input_variables=["resume"],
    template=template
)

chain = prompt | llm


def analyze_resume(resume_text):

    result = chain.invoke({
        "resume": resume_text
    })

    return result.content