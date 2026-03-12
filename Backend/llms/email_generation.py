from pathlib import Path

from langchain.prompts import PromptTemplate

from llms.groq_client import llm

template_path = Path(__file__).resolve().parent.parent / "prompts" / "email_client.txt"
template = template_path.read_text(encoding="utf-8")

prompt  =  PromptTemplate(
    input_variables=["job_description", "resume"],
    template=template

)

chain = prompt | llm

def generate_email(job, resume):
    
    response = chain.invoke({
        "job_description": job,
        "resume": resume
    })
    
    return response.content