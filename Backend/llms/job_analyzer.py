from langchain.prompts import PromptTemplate
from llms.groq_client import llm

template = """
Extract the following information from the job description.

Job Description:
{job}

Return JSON with:

job_title
company
skills
experience
"""

prompt =  PromptTemplate(
    input_variables=["job"],
    template=template
)

chain = prompt | llm


def analyze_job(job_text):

    result = chain.invoke({
        "job": job_text
    })

    return result.content