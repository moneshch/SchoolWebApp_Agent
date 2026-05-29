from langchain.tools import tool

from school_app.models import (
    Student,
    Grade,
    Holiday
)

from .rag import load_vectorstore
from school_app.models import SchoolPolicy
from django.db.models import Q, Case, When, IntegerField, Value
# =========================================
# SCHOOL POLICY TOOL
# =========================================



@tool
def get_school_policy_bkp_correctHaiYeh(query: str) -> str:
    """
    Retrieve school policy information from database.
    ONLY use this tool for school policies/rules.
    Works with natural language like 'policy for using computer lab'.
    """

    # Stop words to ignore
    STOP_WORDS = {
        "i", "a", "an", "the", "is", "it", "in", "on", "at", "to",
        "for", "of", "and", "or", "what", "how", "when", "where",
        "need", "get", "tell", "me", "about", "using", "use",
        "please", "can", "do", "give", "show", "find", "policy"
    }

    # Extract meaningful keywords
    keywords = [
        word.strip()
        for word in query.lower().split()
        if word.strip() not in STOP_WORDS and len(word.strip()) > 2
    ]

    if not keywords:
        return "Please provide more specific keywords to search for a policy."

    # ── Step 1: Full phrase match (highest priority) ──────────────
    policies = SchoolPolicy.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query)
    )

    # ── Step 2: ALL keywords must match (AND logic) ───────────────
    if not policies.exists():
        combined_q = Q()
        for kw in keywords:
            combined_q &= (
                Q(title__icontains=kw) | Q(content__icontains=kw)
            )
        policies = SchoolPolicy.objects.filter(combined_q)

    # ── Step 3: ANY keyword matches, ranked by relevance ─────────
    if not policies.exists():
        any_q = Q()
        for kw in keywords:
            any_q |= (
                Q(title__icontains=kw) | Q(content__icontains=kw)
            )

        # Score each policy by how many keywords it matches
        score_cases = [
            When(
                Q(title__icontains=kw) | Q(content__icontains=kw),
                then=Value(1)
            )
            for kw in keywords
        ]

        policies = (
            SchoolPolicy.objects
            .filter(any_q)
            .annotate(
                relevance=sum(
                    Case(when, default=Value(0), output_field=IntegerField())
                    for when in score_cases
                )
            )
            .order_by("-relevance")
        )

    if not policies.exists():
        return (
            f"No school policy found for '{query}'.\n"
            f"Keywords searched: {', '.join(keywords)}"
        )

    result = []
    for policy in policies[:5]:
        result.append(
            f"Title       : {policy.title}\n"
            f"Policy Type : {policy.policy_type}\n\n"
            f"{policy.content.strip()}"
        )

    return ("\n" + "-" * 60 + "\n").join(result)
@tool
def get_school_policy(query: str) -> str:
    """
    Retrieve school policy information from the database.
    Works for any natural language query about school rules,
    procedures, or policies (e.g. 'computer lab usage', 'fee payment').
    """
    import sqlite3

    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()

    # Split query into keywords for flexible LIKE matching
    keywords = [kw.strip() for kw in query.lower().split() if len(kw.strip()) > 2]

    # Build WHERE clause: each keyword checked against title AND content
    conditions = " OR ".join(
        [f"(LOWER(title) LIKE ? OR LOWER(content) LIKE ?)" for _ in keywords]
    )
    params = []
    for kw in keywords:
        params.extend([f"%{kw}%", f"%{kw}%"])

    sql = f"""
        SELECT title, policy_type, content
        FROM school_app_schoolpolicy
        WHERE {conditions}
        LIMIT 5
    """

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return f"No school policy found for '{query}'."

    result = []
    for title, policy_type, content in rows:
        result.append(
            f"Title       : {title}\n"
            f"Policy Type : {policy_type}\n\n"
            f"{content.strip()}"
        )

    return ("\n" + "-" * 60 + "\n").join(result)

# =========================================
# RAG TOOL
# =========================================

# tools.py

@tool(response_format="content_and_artifact")
def retrieve_context(query: str, source_filename: str = ""):
    """
    Retrieve information from uploaded school documents/PDFs.
    If the user mentions a specific document name, pass it as source_filename
    (e.g. source_filename='HILLCREST_school_policy.pdf').
    """
    vectorstore = load_vectorstore()

    search_kwargs = {"k": 5}

    # =================================================
    # CHROMA FILTER: use $eq for exact match or loop
    # for partial filename match (Chroma has no $contains)
    # =================================================

    if source_filename:

        # Try exact match first
        docs = vectorstore.similarity_search(
            query,
            k=5,
            filter={"source": {"$eq": source_filename}}
        )

        # If exact match returns nothing, try case-insensitive
        # partial match by fetching more and filtering in Python
        if not docs:
            all_docs = vectorstore.similarity_search(query, k=20)
            docs = [
                doc for doc in all_docs
                if source_filename.lower() in
                   doc.metadata.get("source", "").lower()
            ][:5]

    else:
        docs = vectorstore.similarity_search(query, k=5)

    if not docs:
        return (
            f"No relevant content found"
            f"{' in ' + source_filename if source_filename else ''}."
        ), []

    serialized = "\n\n".join(
        f"Source: {doc.metadata.get('source', 'Unknown')}\n"
        f"Content: {doc.page_content}"
        for doc in docs
    )

    return serialized, docs


# =========================================
# CREATE STUDENT TOOL
# =========================================

@tool
def create_student_Old(
    first_name: str,
    last_name: str,
    grade_name: str
):
    """
    Create a new student.
    """

    # normalize input
    normalized_grade = grade_name.lower()

    # attempt flexible matching
    grades = Grade.objects.all()

    matched_grade = None

    for grade in grades:

        db_grade = grade.grade_name.lower()

        if (
            normalized_grade in db_grade
            or db_grade in normalized_grade
        ):
            matched_grade = grade
            break

    if not matched_grade:

        # fallback example
        available = ", ".join(
            [g.grade_name for g in grades]
        )

        return (
            f"Grade not found. "
            f"Available grades: {available}"
        )

    student = Student.objects.create(
        first_name=first_name,
        last_name=last_name,
        grade=matched_grade,
        admission_number=f"ADM-{Student.objects.count()+1}",
        gender="Male",
        address="Demo Address",
        parent_name="Demo Parent",
        parent_phone="9999999999",
        admission_date="2026-01-01",
        date_of_birth="2015-01-01"
    )

    return (
        f"Student created successfully.\n"
        f"Name: {student.first_name} {student.last_name}\n"
        f"Grade: {matched_grade.grade_name}"
    )

import uuid
from datetime import date

@tool
def create_student(
    first_name: str,
    last_name: str,
    grade_name: str,
    gender: str = "Not Specified",
    parent_name: str = "Not Specified",
    parent_phone: str = "Not Specified",
    address: str = "Not Specified"
) -> str:
    """
    Creates a new student record in the database.
    Use this tool when a user explicitly asks to add, enroll, or create a new student.
    
    Args:
        first_name (str): The student's first name.
        last_name (str): The student's last name.
        grade_name (str): The exact name of the grade (e.g., "Grade 10").
        gender (str, optional): The student's gender. Leave empty if unknown.
        parent_name (str, optional): The parent or guardian's full name. Leave empty if unknown.
        parent_phone (str, optional): The parent's contact number. Leave empty if unknown.
        address (str, optional): The student's home address. Leave empty if unknown.
        
    Returns:
        str: A success message with the new student's details, or an error message if the grade is invalid.
    """
    
    # 1. Safer Grade Matching via ORM
    # First, try an exact case-insensitive match
    clean_grade = grade_name.strip()
    matched_grade = Grade.objects.filter(grade_name__iexact=clean_grade).first()

    # Fallback: Try a slightly looser 'contains' match if exact fails
    if not matched_grade:
        matched_grade = Grade.objects.filter(grade_name__icontains=clean_grade).first()

    # 2. Handle missing grades elegantly
    if not matched_grade:
        # Fetching all grades could be heavy, limit to a list of names
        available = ", ".join(list(Grade.objects.values_list('grade_name', flat=True)[:10]))
        return (
            f"Error: Grade '{grade_name}' not found. "
            f"Please ask the user to clarify. Some available grades include: {available}..."
        )

    # 3. Generate a safe Admission Number (UUID fragment to avoid race conditions)
    # Note: If your model handles this automatically via an AutoField or default callable, 
    # you should completely remove 'admission_number' from the .create() method below.
    #safe_adm_number = f"ADM-{str(uuid.uuid4())[:8].upper()}"

    # 4. Create the student with dynamic data
    try:
        student = Student.objects.create(
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            grade=matched_grade,
            admission_number=f"ADM-{Student.objects.count()+1}",
            #admission_number=safe_adm_number, 
            gender=gender,
            address=address,
            parent_name=parent_name,
            parent_phone=parent_phone,
            admission_date=date.today().isoformat(), # Automatically use today's date
            # date_of_birth should ideally be an argument too, leaving as a placeholder or omit if nullable
            date_of_birth="2015-01-01" 
        )

        return (
            f"Success! Student created.\n"
            f"Name: {student.first_name} {student.last_name}\n"
            f"Grade: {matched_grade.grade_name}\n"
            f"Admission No: {student.admission_number}"
        )
        
    except Exception as e:
        return f"An error occurred while trying to save the student to the database: {str(e)}"
# =========================================
# SEARCH STUDENT TOOL
# =========================================

@tool
def search_students(first_name: str = "", last_name: str = "") -> str:
    """
    Searches the student database to retrieve a student's grade and admission number.
    Use this tool whenever you need to look up a student's details by their name.
    
    Args:
        first_name (str, optional): The student's first name (e.g., "John"). Leave empty if unknown.
        last_name (str, optional): The student's last name (e.g., "Smith"). Leave empty if unknown.
        
    Returns:
        str: A formatted string of up to 5 matching students, or a "No students found" message.
    """
    
    # Start with all students
    query = Student.objects.all()
    
    # Dynamically filter based on what the LLM provides
    if first_name:
        query = query.filter(first_name__icontains=first_name.strip())
    if last_name:
        query = query.filter(last_name__icontains=last_name.strip())
        
    students = query[:5]

    if not students:
        return "No students found matching that name."

    result = []
    for student in students:
        # Use textwrap.dedent or strip to keep formatting clean for the LLM context window
        result.append(
            f"Name: {student.first_name} {student.last_name}\n"
            f"Grade: {student.grade}\n"
            f"Admission No: {student.admission_number}\n"
            f"Phone: {student.phone}\n"
            f"Email: {student.email}\n"
            f"date Of Birth: {student.date_of_birth}\n"

            f"---"
        )

    return "\n".join(result)
# =========================================
# HOLIDAY TOOL
# =========================================

@tool
def get_holidays():
    """
    Get school holidays.
    """

    holidays = Holiday.objects.all().order_by(
        "holiday_date"
    )

    if not holidays:
        return "No holidays found"

    result = []

    for holiday in holidays:

        result.append(
            f"{holiday.name} - {holiday.holiday_date}"
        )

    return "\n".join(result)