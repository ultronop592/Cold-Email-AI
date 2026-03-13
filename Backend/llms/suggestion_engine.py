
from langchain_core.prompts import PromptTemplate
from llms.groq_client import llm

template = """
Compare the job requirements with the candidate profile.

Job:
{job}

Resume:
{resume}

Provide:

1. Match score
2. Missing skills
3. Suggestions to improve the profile
"""

prompt = PromptTemplate(
    input_variables=["job","resume"],
    template=template
)

chain = prompt | llm


def generate_suggestions(job,resume):

    result = chain.invoke({
        "job":job,
        "resume":resume
    })

    return result.content