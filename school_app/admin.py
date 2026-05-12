from django.contrib import admin

from .models import (
    Grade,
    Subject,
    Teacher,
    TeacherSubjectAssignment,
    Student,
    StudentLeave,
    SchoolPolicy,
    Holiday,
    UploadedDocument,  ChatSession,
    ChatMessage , AgentLog
)


# =========================================================
# GRADE ADMIN
# =========================================================

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "grade_name",
        "division",
        "academic_year",
        "class_teacher"
    )

    search_fields = (
        "grade_name",
        "division",
        "academic_year"
    )

    list_filter = (
        "academic_year",
    )

    ordering = (
        "grade_name",
        "division"
    )


# =========================================================
# SUBJECT ADMIN
# =========================================================

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name"
    )

    search_fields = (
        "name",
    )

    ordering = (
        "name",
    )


# =========================================================
# TEACHER ADMIN
# =========================================================

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "first_name",
        "last_name",
        "email",
        "phone",
        "qualification",
        "years_of_experience",
        "joining_date",
        "is_active"
    )

    search_fields = (
        "first_name",
        "last_name",
        "email",
        "qualification"
    )

    list_filter = (
        "qualification",
        "is_active",
        "joining_date"
    )

    ordering = (
        "first_name",
        "last_name"
    )


# =========================================================
# TEACHER SUBJECT ASSIGNMENT ADMIN
# =========================================================

@admin.register(TeacherSubjectAssignment)
class TeacherSubjectAssignmentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "teacher",
        "grade",
        "subject",
        "assigned_date"
    )

    search_fields = (
        "teacher__first_name",
        "teacher__last_name",
        "subject__name",
        "grade__grade_name"
    )

    list_filter = (
        "subject",
        "grade"
    )

    ordering = (
        "teacher",
    )


# =========================================================
# STUDENT ADMIN
# =========================================================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "admission_number",
        "first_name",
        "last_name",
        "gender",
        "grade",
        "parent_name",
        "parent_phone",
        "email",
        "is_active"
    )

    search_fields = (
        "first_name",
        "last_name",
        "admission_number",
        "email",
        "parent_name"
    )

    list_filter = (
        "gender",
        "grade",
        "is_active",
        "admission_date"
    )

    ordering = (
        "first_name",
        "last_name"
    )

    list_per_page = 20


# =========================================================
# STUDENT LEAVE ADMIN
# =========================================================

@admin.register(StudentLeave)
class StudentLeaveAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "student",
        "start_date",
        "end_date",
        "status",
        "approved_by",
        "applied_on"
    )

    search_fields = (
        "student__first_name",
        "student__last_name",
        "reason"
    )

    list_filter = (
        "status",
        "start_date",
        "end_date"
    )

    ordering = (
        "-applied_on",
    )


# =========================================================
# SCHOOL POLICY ADMIN
# =========================================================

@admin.register(SchoolPolicy)
class SchoolPolicyAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "policy_type",
        "uploaded_at"
    )

    search_fields = (
        "title",
        "content"
    )

    list_filter = (
        "policy_type",
        "uploaded_at"
    )

    ordering = (
        "title",
    )


# =========================================================
# HOLIDAY ADMIN
# =========================================================

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "holiday_date",
        "is_optional"
    )

    search_fields = (
        "name",
        "description"
    )

    list_filter = (
        "is_optional",
        "holiday_date"
    )

    ordering = (
        "holiday_date",
    )


# =========================================================
# UPLOADED DOCUMENT ADMIN
# =========================================================

@admin.register(UploadedDocument)
class UploadedDocumentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "uploaded_by",
        "processed",
        "uploaded_at"
    )

    search_fields = (
        "title",
        "uploaded_by"
    )

    list_filter = (
        "processed",
        "uploaded_at"
    )

    ordering = (
        "-uploaded_at",
    )

# =========================================
# CHAT SESSION ADMIN
# =========================================

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "title",
        "created_at"
    )

    search_fields = (
        "user__username",
        "title"
    )

    ordering = (
        "-created_at",
    )


# =========================================
# CHAT MESSAGE ADMIN
# =========================================

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "session",
        "role",
        "created_at"
    )

    search_fields = (
        "content",
    )

    list_filter = (
        "role",
    )

    ordering = (
        "-created_at",
    )

# =========================================
# AGENT LOG ADMIN
# =========================================


@admin.register(AgentLog)
class AgentLogAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "tool_used",
        "execution_time",
        "created_at"
    )

    search_fields = (
        "user_message",
        "tool_used",
        "final_response"
    )

    list_filter = (
        "tool_used",
        "created_at"
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
    )