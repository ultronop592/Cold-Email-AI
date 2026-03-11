from langchain import PromptTemplate
from llm.groq_client import llm

template = open("Backend/prompts/email_generation.txt").read()

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