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

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """
    Retrieve school policy information.
    """

    vectorstore = load_vectorstore()

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )

    docs = retriever.invoke(query)

    serialized = "\n\n".join(
        f"Content: {doc.page_content}"
        for doc in docs
    )

    return serialized, docs


# =========================================
# CREATE STUDENT TOOL
# =========================================

@tool
def create_student(
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


# =========================================
# SEARCH STUDENT TOOL
# =========================================

@tool
def search_students(query: str):
    """
    Search students by name.
    """

    students = Student.objects.filter(
        first_name__icontains=query
    )[:5]

    if not students:
        return "No students found"

    result = []

    for student in students:

        result.append(
            f"""
            Name: {student.first_name} {student.last_name}
            Grade: {student.grade}
            Admission No: {student.admission_number}
            """
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