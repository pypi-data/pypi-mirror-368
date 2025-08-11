import uuid
from django.utils import timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('name', models.CharField(editable=False, max_length=100, primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, max_length=480)),
                ('internal', models.BooleanField(db_index=True, default=False)),
                ('created_at', models.DateTimeField(default=timezone.now)),
            ],
            options={
                'verbose_name': 'permission',
                'verbose_name_plural': 'permissions',
                'db_table': 'saas_permission',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=140)),
                ('slug', models.SlugField(help_text='Identity of the tenant, e.g. <slug>.example.com', unique=True)),
                ('region', models.CharField(blank=True, default='', max_length=24)),
                ('environment', models.CharField(blank=True, default='', max_length=48)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(db_index=True, default=timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(null=True, on_delete=models.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'tenant',
                'verbose_name_plural': 'tenants',
                'db_table': 'saas_tenant',
                'ordering': ['created_at'],
                'abstract': False,
                'swappable': 'SAAS_TENANT_MODEL',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(db_index=True, max_length=100)),
                ('managed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(db_index=True, default=timezone.now)),
                ('tenant', models.ForeignKey(on_delete=models.CASCADE, to=settings.SAAS_TENANT_MODEL)),
                ('permissions', models.ManyToManyField(blank=True, to='saas_base.permission')),
            ],
            options={
                'verbose_name': 'group',
                'verbose_name_plural': 'groups',
                'db_table': 'saas_group',
                'ordering': ['created_at'],
                'unique_together': {('tenant', 'name')},
            },
        ),
        migrations.CreateModel(
            name='UserEmail',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('verified', models.BooleanField(default=False)),
                ('primary', models.BooleanField(db_index=True, default=False)),
                ('created_at', models.DateTimeField(db_index=True, default=timezone.now)),
                (
                    'user',
                    models.ForeignKey(on_delete=models.CASCADE, related_name='emails', to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                'verbose_name': 'email',
                'verbose_name_plural': 'emails',
                'db_table': 'saas_auth_email',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('invite_email', models.EmailField(blank=True, max_length=254, null=True)),
                (
                    'status',
                    models.SmallIntegerField(choices=[(0, 'request'), (1, 'waiting'), (2, 'active')], default=0),
                ),
                ('created_at', models.DateTimeField(db_index=True, default=timezone.now)),
                (
                    'groups',
                    models.ManyToManyField(
                        blank=True,
                        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                        to='saas_base.group',
                    ),
                ),
                (
                    'inviter',
                    models.ForeignKey(
                        blank=True, null=True, on_delete=models.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL
                    ),
                ),
                ('tenant', models.ForeignKey(on_delete=models.CASCADE, to=settings.SAAS_TENANT_MODEL)),
                (
                    'user',
                    models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to=settings.AUTH_USER_MODEL),
                ),
                (
                    'permissions',
                    models.ManyToManyField(
                        blank=True, help_text='Specific permissions for this user.', to='saas_base.permission'
                    ),
                ),
            ],
            options={
                'verbose_name': 'member',
                'verbose_name_plural': 'members',
                'db_table': 'saas_member',
                'ordering': ['-created_at'],
                'unique_together': {('tenant', 'user')},
            },
        ),
    ]
