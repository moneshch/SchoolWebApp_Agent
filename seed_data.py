import os
import random
import django

from datetime import date, timedelta

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()

from school_app.models import (
    Grade,
    Subject,
    Teacher,
    TeacherSubjectAssignment,
    Student,
    StudentLeave,
    Holiday,
    SchoolPolicy
)


# =========================================================
# CLEAR EXISTING DATA
# =========================================================

print("Deleting old data...")

StudentLeave.objects.all().delete()
TeacherSubjectAssignment.objects.all().delete()

Student.objects.all().delete()
Teacher.objects.all().delete()

Holiday.objects.all().delete()
SchoolPolicy.objects.all().delete()

Subject.objects.all().delete()
Grade.objects.all().delete()

print("Old data deleted")


# =========================================================
# CREATE GRADES (1 TO 12)
# =========================================================

grades = {}

for i in range(1, 13):

    for division in ["A", "B"]:

        grade = Grade.objects.create(
            grade_name=f"Grade {i}",
            division=division,
            academic_year="2025-2026"
        )

        grades[f"Grade {i}-{division}"] = grade

print("Grades created")


# =========================================================
# SUBJECTS
# =========================================================

subject_names = [
    "Mathematics",
    "Science",
    "English",
    "History",
    "Geography",
    "Computer Science",
    "Physics",
    "Chemistry",
    "Biology",
    "Physical Education",
    "Art",
    "Music",
    "Economics",
    "Civics",
    "Environmental Science"
]

subjects = {}

for subject_name in subject_names:

    subject = Subject.objects.create(
        name=subject_name
    )

    subjects[subject_name] = subject

print("Subjects created")


# =========================================================
# TEACHERS
# =========================================================

male_teachers = [
    ("Rahul", "Sharma"),
    ("Amit", "Patil"),
    ("Raj", "Joshi"),
    ("Vikram", "Deshmukh"),
    ("Kiran", "Mehta"),
    ("Sanjay", "Kulkarni"),
    ("Rohit", "Pawar"),
    ("Ajay", "Naik"),
    ("Arjun", "Patwardhan"),
    ("Sameer", "Desai"),
]

female_teachers = [
    ("Anita", "Sharma"),
    ("Sneha", "Patil"),
    ("Pooja", "Joshi"),
    ("Neha", "Deshmukh"),
    ("Priya", "Mehta"),
    ("Meena", "Kulkarni"),
    ("Riya", "Pawar"),
    ("Kavita", "Naik"),
    ("Sanya", "Patwardhan"),
    ("Aarti", "Desai"),
]

qualifications = [
    "MSc Mathematics",
    "MSc Physics",
    "MSc Chemistry",
    "BEd English",
    "MCA",
    "MCom",
    "MA History",
    "BEd Science",
    "MSc Biology",
    "MA Geography"
]

teachers = []

teacher_index = 1

all_teacher_data = male_teachers + female_teachers

for first_name, last_name in all_teacher_data:

    teacher = Teacher.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=f"teacher{teacher_index}@school.com",
        phone=f"987650{teacher_index:04}",
        qualification=random.choice(qualifications),
        years_of_experience=random.randint(2, 18),
        joining_date=date(
            random.randint(2015, 2023),
            random.randint(1, 12),
            random.randint(1, 28)
        ),
        is_active=True
    )

    teachers.append(teacher)

    teacher_index += 1

print("20 teachers created")


# =========================================================
# ASSIGN CLASS TEACHERS
# =========================================================

all_grades = Grade.objects.all()

for index, grade in enumerate(all_grades):

    grade.class_teacher = teachers[
        index % len(teachers)
    ]

    grade.save()

print("Class teachers assigned")


# =========================================================
# TEACHER SUBJECT ASSIGNMENTS
# =========================================================

all_subjects = list(Subject.objects.all())

for teacher in teachers:

    assigned_grades = random.sample(
        list(all_grades),
        4
    )

    assigned_subjects = random.sample(
        all_subjects,
        3
    )

    for grade in assigned_grades:

        for subject in assigned_subjects:

            TeacherSubjectAssignment.objects.create(
                teacher=teacher,
                grade=grade,
                subject=subject
            )

print("Teacher subject assignments created")


# =========================================================
# STUDENTS
# =========================================================

male_students = [
    "Rahul", "Aarav", "Rohan", "Kabir",
    "Vihaan", "Atharv", "Arjun", "Yash",
    "Aditya", "Siddharth", "Kunal", "Ritesh",
    "Ayaan", "Ishaan", "Vedant", "Manav",
    "Om", "Pranav", "Harsh", "Dev"
]

female_students = [
    "Priya", "Diya", "Sanya", "Meera",
    "Anaya", "Ishita", "Sara", "Riya",
    "Kavya", "Aditi", "Pooja", "Sneha",
    "Neha", "Anushka", "Tanvi", "Mira",
    "Kiara", "Avni", "Riddhi", "Nisha"
]

student_last_names = [
    "Sharma", "Patil", "Mehta",
    "Joshi", "Kulkarni", "Desai",
    "Pawar", "Naik", "Jadhav", "Chavan"
]

student_count = 1

for i in range(25):

    # Male student
    first_name = random.choice(male_students)
    last_name = random.choice(student_last_names)

    Student.objects.create(
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date(
            random.randint(2008, 2018),
            random.randint(1, 12),
            random.randint(1, 28)
        ),
        gender="Male",
        admission_number=f"ADM-{1000 + student_count}",
        email=f"student{student_count}@school.com",
        phone=f"999900{student_count:04}",
        address="Pune, Maharashtra",
        parent_name=f"Mr. {last_name}",
        parent_phone=f"888800{student_count:04}",
        admission_date=date(2025, 6, 1),
        is_active=True,
        grade=random.choice(list(all_grades))
    )

    student_count += 1

for i in range(25):

    # Female student
    first_name = random.choice(female_students)
    last_name = random.choice(student_last_names)

    Student.objects.create(
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date(
            random.randint(2008, 2018),
            random.randint(1, 12),
            random.randint(1, 28)
        ),
        gender="Female",
        admission_number=f"ADM-{1000 + student_count}",
        email=f"student{student_count}@school.com",
        phone=f"999900{student_count:04}",
        address="Pune, Maharashtra",
        parent_name=f"Mrs. {last_name}",
        parent_phone=f"888800{student_count:04}",
        admission_date=date(2025, 6, 1),
        is_active=True,
        grade=random.choice(list(all_grades))
    )

    student_count += 1

print("50 students created")


# =========================================================
# STUDENT LEAVES
# =========================================================

students = list(Student.objects.all())

leave_reasons = [
    "Fever",
    "Medical Appointment",
    "Family Function",
    "Travel",
    "Personal Emergency",
    "Cold and Cough",
    "Religious Ceremony",
    "Health Checkup"
]

statuses = [
    "Pending",
    "Approved",
    "Rejected"
]

for i in range(30):

    student = random.choice(students)

    start_date = date.today() - timedelta(
        days=random.randint(1, 60)
    )

    end_date = start_date + timedelta(
        days=random.randint(1, 5)
    )

    StudentLeave.objects.create(
        student=student,
        start_date=start_date,
        end_date=end_date,
        reason=random.choice(leave_reasons),
        status=random.choice(statuses),
        approved_by=random.choice(teachers)
    )

print("Student leaves created")


# =========================================================
# HOLIDAYS (MINIMUM 8)
# =========================================================

holidays_data = [
    ("Republic Day", date(2026, 1, 26)),
    ("Mahashivratri", date(2026, 2, 15)),
    ("Holi", date(2026, 3, 14)),
    ("Ram Navami", date(2026, 4, 5)),
    ("Good Friday", date(2026, 4, 18)),
    ("Independence Day", date(2026, 8, 15)),
    ("Ganesh Chaturthi", date(2026, 9, 7)),
    ("Diwali Vacation", date(2026, 11, 1)),
    ("Christmas", date(2026, 12, 25)),
]

for name, holiday_date in holidays_data:

    Holiday.objects.create(
        name=name,
        holiday_date=holiday_date,
        description=f"{name} Holiday",
        is_optional=False
    )

print("9 holidays created")


# =========================================================
# SCHOOL POLICIES (10)
# =========================================================

policies = [
    (
        "Attendance Policy",
        "Attendance",
        "Students must maintain minimum 75% attendance."
    ),
    (
        "Leave Policy",
        "Leave",
        "Leave applications must be submitted in advance."
    ),
    (
        "Discipline Policy",
        "Discipline",
        "Bullying and misconduct are prohibited."
    ),
    (
        "Fee Policy",
        "Fees",
        "Fees should be paid before due date."
    ),
    (
        "Library Policy",
        "General",
        "Library books should be returned within 14 days."
    ),
    (
        "Computer Lab Policy",
        "General",
        "Students should not install unauthorized software."
    ),
    (
        "Uniform Policy",
        "Discipline",
        "Students must wear proper school uniform."
    ),
    (
        "Examination Policy",
        "General",
        "Cheating during examinations is prohibited."
    ),
    (
        "Sports Policy",
        "General",
        "Sports equipment should be handled carefully."
    ),
    (
        "Internet Usage Policy",
        "General",
        "Internet access is only for educational purposes."
    ),
]

for title, policy_type, content in policies:

    SchoolPolicy.objects.create(
        title=title,
        policy_type=policy_type,
        content=content
    )

print("10 school policies created")


print("\n===================================")
print("Large demo dataset inserted successfully.")
print("===================================")
print("Grades: 24")
print("Teachers: 20")
print("Students: 50")
print("Leaves: 30")
print("Policies: 10")
print("Holidays: 9")
print("===================================")