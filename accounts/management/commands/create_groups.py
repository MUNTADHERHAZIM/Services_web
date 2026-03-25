"""
Management command to create user groups and assign permissions
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'إنشاء مجموعات المستخدمين (Customers, Providers, Admins) مع الصلاحيات'

    def handle(self, *args, **options):
        # إنشاء المجموعات
        customer_group, created = Group.objects.get_or_create(name='Customers')
        provider_group, created = Group.objects.get_or_create(name='Providers')
        admin_group, created = Group.objects.get_or_create(name='Admins')
        
        self.stdout.write(self.style.SUCCESS('✓ تم إنشاء المجموعات'))
        
        # Customers Permissions
        from services.models import Service
        from requests.models import ServiceRequest
        
        # العملاء يمكنهم: عرض الخدمات، إنشاء طلبات، تقييم
        customer_permissions = Permission.objects.filter(
            codename__in=[
                'view_service',
                'add_servicerequest',
                'change_servicerequest',
                'view_servicerequest',
            ]
        )
        customer_group.permissions.set(customer_permissions)
        self.stdout.write('  - صلاحيات العملاء: عرض خدمات، طلب خدمات')
        
        # Providers Permissions
        # المزودون يمكنهم: كل صلاحيات العملاء + إنشاء خدمات + إدارة طلبات
        provider_permissions = Permission.objects.filter(
            codename__in=[
                'view_service',
                'add_service',
                'change_service',
                'delete_service',
                'add_servicerequest',
                'change_servicerequest',
                'view_servicerequest',
            ]
        )
        provider_group.permissions.set(provider_permissions)
        self.stdout.write('  - صلاحيات المزودين: إنشاء خدمات، إدارة طلبات')
        
        # Admins
        # المدراء لديهم كل الصلاحيات (superuser)
        self.stdout.write('  - المدراء: كل الصلاحيات (superuser)')
        
        self.stdout.write(self.style.SUCCESS('\n✅ تم إعداد نظام الصلاحيات بنجاح'))
        self.stdout.write(self.style.WARNING('\nملاحظة: المدراء يجب تعيينهم كـ is_staff و is_superuser يدوياً'))
