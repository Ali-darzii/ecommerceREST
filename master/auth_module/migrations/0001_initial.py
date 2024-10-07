# Generated by Django 5.1.1 on 2024-10-07 02:12

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(blank=True, error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator], verbose_name='username')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='PhoneMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=6, null=True)),
                ('expiration_time', models.DateTimeField()),
                ('phone_no', models.CharField(max_length=11, unique=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='phone_message', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User PhoneMessage',
                'verbose_name_plural': 'Users PhoneMessage',
                'db_table': 'PhoneMessage_DB',
            },
        ),
        migrations.CreateModel(
            name='UserLogins',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no_logins', models.PositiveIntegerField(default=0)),
                ('failed_attempts', models.PositiveIntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_logins', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Login',
                'verbose_name_plural': 'User Logins',
                'db_table': 'UserLogins_DB',
            },
        ),
        migrations.CreateModel(
            name='UserIP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=20)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('failed', models.BooleanField(default=False)),
                ('user_logins', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ips', to='auth_module.userlogins')),
            ],
            options={
                'verbose_name': 'User IPs',
                'verbose_name_plural': 'User IP',
                'db_table': 'UserIP_DB',
            },
        ),
        migrations.CreateModel(
            name='UserDevice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_name', models.CharField(max_length=100)),
                ('is_phone', models.BooleanField(default=False)),
                ('browser', models.CharField(max_length=100)),
                ('os', models.CharField(max_length=100)),
                ('user_logins', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='devices', to='auth_module.userlogins')),
            ],
            options={
                'verbose_name': 'User Devices',
                'verbose_name_plural': 'User Device',
                'db_table': 'UserDevice_DB',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(null=True, upload_to='../images/avatar')),
                ('address', models.TextField(null=True)),
                ('city', models.CharField(max_length=100, null=True)),
                ('postal_code', models.IntegerField(null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_profiles', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User Profile',
                'verbose_name_plural': 'Users Profiles',
                'db_table': 'UserProfile_DB',
            },
        ),
    ]