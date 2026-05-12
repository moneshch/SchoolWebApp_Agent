from django.db import models
from django.contrib.auth.models import User
# =========================================
# GRADE / CLASS
# =========================================

class Grade(models.Model):
    grade_name = models.CharField(max_length=20)      # Example: Grade 5
    division = models.CharField(max_length=5)         # Example: A, B
    academic_year = models.CharField(max_length=20)   # Example: 2025-2026

    class_teacher = models.ForeignKey(
        'Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='class_teacher_for'
    )

    def __str__(self):
        return f"{self.grade_name}-{self.division}"


# =========================================
# SUBJECT
# =========================================

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# =========================================
# TEACHER
# =========================================

class Teacher(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)

    qualification = models.CharField(max_length=255)

    years_of_experience = models.PositiveIntegerField(default=0)

    joining_date = models.DateField()

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# =========================================
# TEACHER SUBJECT ASSIGNMENT
# =========================================

class TeacherSubjectAssignment(models.Model):

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE
    )

    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    assigned_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('teacher', 'grade', 'subject')

    def __str__(self):
        return f"{self.teacher} - {self.subject} - {self.grade}"


# =========================================
# STUDENT
# =========================================

class Student(models.Model):

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    date_of_birth = models.DateField()

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    admission_number = models.CharField(
        max_length=50,
        unique=True
    )

    email = models.EmailField(blank=True, null=True)

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    address = models.TextField()

    parent_name = models.CharField(max_length=255)

    parent_phone = models.CharField(max_length=20)

    admission_date = models.DateField()

    is_active = models.BooleanField(default=True)

    grade = models.ForeignKey(
        Grade,
        on_delete=models.SET_NULL,
        null=True,
        related_name='students'
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# =========================================
# STUDENT LEAVE
# =========================================

class StudentLeave(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='leaves'
    )

    start_date = models.DateField()

    end_date = models.DateField()

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    applied_on = models.DateTimeField(auto_now_add=True)

    approved_by = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.student} Leave ({self.status})"


# =========================================
# SCHOOL POLICY
# =========================================

class SchoolPolicy(models.Model):

    POLICY_TYPES = (
        ('Attendance', 'Attendance'),
        ('Leave', 'Leave'),
        ('Discipline', 'Discipline'),
        ('Fees', 'Fees'),
        ('General', 'General'),
    )

    title = models.CharField(max_length=255)

    policy_type = models.CharField(
        max_length=50,
        choices=POLICY_TYPES
    )

    content = models.TextField()

    uploaded_file = models.FileField(
        upload_to='policies/',
        blank=True,
        null=True
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =========================================
# HOLIDAY
# =========================================

class Holiday(models.Model):

    name = models.CharField(max_length=255)

    holiday_date = models.DateField()

    description = models.TextField(blank=True, null=True)

    is_optional = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.holiday_date})"


# =========================================
# UPLOADED DOCUMENTS
# =========================================

class UploadedDocument(models.Model):

    title = models.CharField(max_length=255)

    file = models.FileField(upload_to='documents/')

    uploaded_at = models.DateTimeField(auto_now_add=True)

    uploaded_by = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    processed = models.BooleanField(default=False)

    summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
    

# =========================================
# CHAT SESSION
# =========================================

class ChatSession(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_sessions"
    )

    title = models.CharField(
        max_length=255,
        default="New Chat"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.title}"


# =========================================
# CHAT MESSAGE
# =========================================

class ChatMessage(models.Model):

    ROLE_CHOICES = (
        ("user", "User"),
        ("assistant", "Assistant"),
    )

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.role} - {self.created_at}"
    

# =========================================================
# AGENT LOGS
# =========================================================

class AgentLog(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    user_message = models.TextField()

    tool_used = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    tool_input = models.TextField(
        blank=True,
        null=True
    )

    tool_output = models.TextField(
        blank=True,
        null=True
    )

    final_response = models.TextField()

    execution_time = models.FloatField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.user.username} - "
            f"{self.created_at}"
        )