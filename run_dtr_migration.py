"""
Script to manually run the DTR history migration.
This is a manual alternative to 'python manage.py migrate dtr 0004_add_dtr_history'
"""
import os
import sys
import django

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ojt_project.settings')
django.setup()

# Now we can import Django modules
from django.core.management import call_command

def run_migration():
    """Run the DTR history migration."""
    print("=" * 60)
    print("Running DTR History Migration...")
    print("=" * 60)
    
    try:
        # Run the specific migration
        print("\n1. Applying migration: dtr.0004_add_dtr_history")
        call_command('migrate', 'dtr', '0004_add_dtr_history', verbosity=2)
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        
        # Show the migration status
        print("\nCurrent migration status for DTR app:")
        call_command('showmigrations', 'dtr', verbosity=1)
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Error running migration: {e}")
        print("=" * 60)
        return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
