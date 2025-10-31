import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.users.models import User

# Check if user exists
user = User.objects.filter(username='darkdevil').first()

if user:
    print(f'User found!')
    print(f'Username: {user.username}')
    print(f'Email: {user.email}')
    print(f'Is staff: {user.is_staff}')
    print(f'Is superuser: {user.is_superuser}')
    print(f'Password check for "sneha2604": {user.check_password("sneha2604")}')
else:
    print('User not found!')
    print('Creating new admin user...')
    user = User.objects.create_superuser('darkdevil', 'chirag.garg.5293@gmail.com', 'sneha2604')
    print(f'Admin user created: {user.username}')
    print(f'Is staff: {user.is_staff}')
    print(f'Is superuser: {user.is_superuser}')
