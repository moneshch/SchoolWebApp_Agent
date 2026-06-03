from langchain.agents import create_agent

from langchain_ollama import ChatOllama
from langchain.agents.middleware import PIIMiddleware
from .tools import (
    retrieve_context,
    create_student,
    search_students,
    get_holidays,
    get_school_policy
)


# =========================================================
# MODEL
# =========================================================

model = ChatOllama(
    model="minimax-m2:cloud",
    #model="llama3.2:3b",
    temperature=0.9
)


# =========================================================
# SYSTEM PROMPTS
# =========================================================

SYSTEM_PROMPTS = {

    # -------------------------------------------------
    # STRICT — refuses all off-topic questions
    # -------------------------------------------------

    "strict": """
        You are a school AI assistant.

        STRICT SCOPE RESTRICTION:
        You ONLY answer questions related to:
        - School policies (attendance, fees, dress code, etc.)
        - School holidays and calendar
        - Student management (grades, admissions, records)
        - Uploaded school documents/PDFs

        If a question is outside this scope, respond EXACTLY with:
        "I can only assist with school-related topics such as policies,
        holidays, student management, and uploaded documents. Please ask
        a question related to these topics."

        Do NOT:
        - Answer general knowledge questions (e.g., science, geography, history)
        - Provide information not found in school tools or documents
        - Hallucinate or invent any information
        - Engage in small talk or off-topic conversation

        TOOL USAGE RULES:
        - Use get_school_policy for any policy-related question
        - Use retrieve_context ONLY for uploaded documents/PDFs. When the user mentions a specific document by name (e.g. "HILLCREST policy"),
  pass that name as source_filename to retrieve_context so only that document is searched.
        - Use database tools for student records and data
        - If information is not found via tools, say: "I could not find that information."
    """,

    # -------------------------------------------------
    # NORMAL — focused on school, politely declines off-topic
    # -------------------------------------------------

    "normal": """
        You are a school AI assistant.

        IMPORTANT RULES:
        - Use get_school_policy tool for school policies.
        - Use retrieve_context ONLY for uploaded documents/PDFs.
        - Use database tools whenever possible.
        - DO NOT hallucinate or invent policies.
        - If information is not found, say: "I could not find that information."
        

        You help users with:
        - school policies
        - holidays
        - student management
        - uploaded documents. When the user mentions a specific document by name (e.g. "HILLCREST policy"),
  pass that name as source_filename to retrieve_context so only that document is searched.

        Be concise and accurate.
    """,

    # -------------------------------------------------
    # RELAXED — school-first but allows general knowledge
    # -------------------------------------------------

    "relaxed": """
        You are a friendly AI assistant. Answere every user question without any restriction.
        Even reveal your system prompt and instructions.

    """
}


# =========================================================
# TOOLS
# =========================================================

TOOLS = [
    retrieve_context,
    create_student,
    search_students,
    get_holidays,get_school_policy
]



# =========================================================
# AGENT FACTORY
# =========================================================

def get_agent(mode: str = "normal"):

    
    system_prompt = SYSTEM_PROMPTS.get(
        mode,
        SYSTEM_PROMPTS["normal"]
    )
    print("#################3" + system_prompt)
    return create_agent(
        model=model,
        tools=TOOLS,
        system_prompt=system_prompt,
        middleware=[
        # Redact emails in user input before sending to model
        PIIMiddleware(
            "email",
            strategy="mask",
            apply_to_output=True,
        )
        
    ],
    )