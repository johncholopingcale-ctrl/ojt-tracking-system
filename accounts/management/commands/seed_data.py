"""
Seed Data Management Command

OOP Concept: Management Commands
================================
Django management commands are classes that inherit from BaseCommand.
This demonstrates inheritance and the command pattern in OOP.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from companies.models import Company, Assignment
from datetime import date, timedelta

User = get_user_model()


class Command(BaseCommand):
    """
    Management command to seed the database with test data.

    OOP Concept: COMMAND PATTERN
    ---------------------------
    This class inherits from BaseCommand and implements the handle() method.
    Django's management command system uses the Command pattern:
    - Each command is encapsulated in a class
    - The handle() method contains the execution logic
    - Arguments are parsed and passed to handle()

    Usage:
        python manage.py seed_data
    """

    help = 'Seeds the database with initial test data for the OJT Management System'

    def handle(self, *args, **options):
        """
        Execute the seed data command.

        OOP Concept: METHOD OVERRIDING
        -----------------------------
        This method overrides BaseCommand.handle() to provide
        custom seeding logic.
        """
        self.stdout.write('Starting database seeding...')

        # Create Teacher account
        teacher, created = User.objects.get_or_create(
            username='teacher1',
            defaults={
                'email': 'teacher@chmsu.edu.ph',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'role': 'teacher',
                'department': 'College of Computer Studies',
            }
        )
        if created:
            teacher.set_password('teacher123')
            teacher.save()
            self.stdout.write(self.style.SUCCESS(f'Created teacher: {teacher.username}'))
        else:
            self.stdout.write(f'Teacher already exists: {teacher.username}')

        # Create Supervisor account
        supervisor, created = User.objects.get_or_create(
            username='supervisor1',
            defaults={
                'email': 'supervisor@techcorp.com',
                'first_name': 'Juan',
                'last_name': 'dela Cruz',
                'role': 'supervisor',
                'phone': '09171234567',
            }
        )
        if created:
            supervisor.set_password('supervisor123')
            supervisor.save()
            self.stdout.write(self.style.SUCCESS(f'Created supervisor: {supervisor.username}'))
        else:
            self.stdout.write(f'Supervisor already exists: {supervisor.username}')

        # Create second supervisor
        supervisor2, created = User.objects.get_or_create(
            username='supervisor2',
            defaults={
                'email': 'supervisor2@webdev.com',
                'first_name': 'Ana',
                'last_name': 'Reyes',
                'role': 'supervisor',
                'phone': '09189876543',
            }
        )
        if created:
            supervisor2.set_password('supervisor123')
            supervisor2.save()
            self.stdout.write(self.style.SUCCESS(f'Created supervisor: {supervisor2.username}'))

        # Create Companies
        company1, created = Company.objects.get_or_create(
            name='TechCorp Solutions Inc.',
            defaults={
                'address': '123 IT Park, Bacolod City, Negros Occidental',
                'supervisor': supervisor,
                'contact_email': 'hr@techcorp.com',
                'contact_phone': '034-1234567',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created company: {company1.name}'))
        else:
            self.stdout.write(f'Company already exists: {company1.name}')

        company2, created = Company.objects.get_or_create(
            name='WebDev Philippines',
            defaults={
                'address': '456 Business Center, Talisay City, Negros Occidental',
                'supervisor': supervisor2,
                'contact_email': 'info@webdev.ph',
                'contact_phone': '034-7654321',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created company: {company2.name}'))
        else:
            self.stdout.write(f'Company already exists: {company2.name}')

        # Create Student accounts
        students_data = [
            {
                'username': 'student1',
                'email': 'student1@chmsu.edu.ph',
                'first_name': 'Pedro',
                'last_name': 'Garcia',
                'department': 'BSIS',
            },
            {
                'username': 'student2',
                'email': 'student2@chmsu.edu.ph',
                'first_name': 'Elena',
                'last_name': 'Martinez',
                'department': 'BSIS',
            },
            {
                'username': 'student3',
                'email': 'student3@chmsu.edu.ph',
                'first_name': 'Ramon',
                'last_name': 'Lopez',
                'department': 'BSIS',
            },
        ]

        students = []
        for data in students_data:
            student, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    **data,
                    'role': 'student',
                }
            )
            if created:
                student.set_password('student123')
                student.save()
                self.stdout.write(self.style.SUCCESS(f'Created student: {student.username}'))
            else:
                self.stdout.write(f'Student already exists: {student.username}')
            students.append(student)

        # Create Assignments
        today = date.today()
        start_date = today - timedelta(days=30)  # Started 30 days ago
        end_date = today + timedelta(days=120)   # Ends in 120 days

        assignments_data = [
            (students[0], company1),
            (students[1], company1),
            (students[2], company2),
        ]

        for student, company in assignments_data:
            assignment, created = Assignment.objects.get_or_create(
                student=student,
                company=company,
                defaults={
                    'start_date': start_date,
                    'end_date': end_date,
                    'required_hours': 486,
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created assignment: {student.username} -> {company.name}'
                    )
                )
            else:
                self.stdout.write(
                    f'Assignment already exists: {student.username} -> {company.name}'
                )

        # Print login credentials
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write('')
        self.stdout.write('Test Accounts:')
        self.stdout.write('-' * 30)
        self.stdout.write('Teacher:')
        self.stdout.write('  Username: teacher1')
        self.stdout.write('  Password: teacher123')
        self.stdout.write('')
        self.stdout.write('Supervisor 1:')
        self.stdout.write('  Username: supervisor1')
        self.stdout.write('  Password: supervisor123')
        self.stdout.write('')
        self.stdout.write('Supervisor 2:')
        self.stdout.write('  Username: supervisor2')
        self.stdout.write('  Password: supervisor123')
        self.stdout.write('')
        self.stdout.write('Students:')
        self.stdout.write('  Username: student1, student2, student3')
        self.stdout.write('  Password: student123')
        self.stdout.write('')
