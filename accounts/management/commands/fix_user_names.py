"""
Management command to fix users without first/last names.
Removes test users and prompts for real names.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Fix users who have no first/last name set'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-test',
            action='store_true',
            help='Delete users with test-like usernames (e.g., supervisor1, student1)',
        )

    def handle(self, *args, **options):
        # Find users without proper names
        users_without_names = User.objects.filter(first_name='') | User.objects.filter(last_name='')
        
        if not users_without_names.exists():
            self.stdout.write(self.style.SUCCESS('All users have first and last names set!'))
            return

        self.stdout.write(f'\nFound {users_without_names.count()} user(s) without proper names:\n')
        
        for user in users_without_names:
            self.stdout.write(f'  - {user.username} ({user.role}) - Name: "{user.first_name} {user.last_name}"')

        if options['delete_test']:
            # Delete test users (those with numeric suffixes like supervisor1, student1)
            import re
            test_users = [u for u in users_without_names if re.match(r'^(supervisor|student|teacher)\d+$', u.username)]
            
            if test_users:
                self.stdout.write(f'\nDeleting {len(test_users)} test user(s)...')
                for user in test_users:
                    self.stdout.write(f'  Deleting: {user.username}')
                    user.delete()
                self.stdout.write(self.style.SUCCESS('Test users deleted!'))
            else:
                self.stdout.write('No test users found to delete.')
        else:
            self.stdout.write('\nTo delete test users, run with --delete-test flag')
            self.stdout.write('Example: python manage.py fix_user_names --delete-test')
