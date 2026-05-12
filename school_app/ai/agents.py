from langchain.agents import create_agent

from langchain_ollama import ChatOllama

from .tools import (
    retrieve_context,
    create_student,
    search_students,
    get_holidays,get_school_policy
)


model = ChatOllama(
    model="qwen3:8b",
    temperature=0
)


agent = create_agent(
    model=model,
    tools=[
        retrieve_context,
        create_student,
        search_students,
        get_holidays,
        get_school_policy
    ],
    system_prompt="""
                You are a school AI assistant.

                IMPORTANT RULES:

                - Use get_school_policy tool for school policies.
                - Use retrieve_context ONLY for uploaded documents/PDFs.
                - Use database tools whenever possible.
                - DO NOT hallucinate or invent policies.
                - If information is not found, say:
                "I could not find that information."

                You help users with:
                - school policies
                - holidays
                - student management
                - uploaded documents

                Be concise and accurate.
                """
)