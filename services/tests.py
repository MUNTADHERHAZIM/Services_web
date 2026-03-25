"""
Services Tests - اختبارات الخدمات
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Provider
from services.models import Category, Service


class ServiceListViewTest(TestCase):
    """اختبارات عرض قائمة الخدمات"""
    
    def setUp(self):
        self.client = Client()
        
        # إنشاء بيانات تجريبية
        self.user = User.objects.create_user('testuser', 'test@test.com', 'testpass123')
        self.provider = Provider.objects.create(
            user=self.user,
            display_name='مقدم تجريبي',
            is_active=True
        )
        self.category = Category.objects.create(
            name='تصنيف تجريبي',
            slug='test-category',
            is_active=True
        )
        self.service = Service.objects.create(
            category=self.category,
            provider=self.provider,
            title='خدمة تجريبية',
            slug='test-service',
            summary='ملخص الخدمة التجريبية',
            description='وصف تفصيلي للخدمة التجريبية',
            price=100,
            is_active=True
        )

    def test_service_list_view_status_code(self):
        """اختبار أن صفحة الخدمات تعمل بشكل صحيح"""
        response = self.client.get(reverse('services:service_list'))
        self.assertEqual(response.status_code, 200)

    def test_service_list_view_template(self):
        """اختبار استخدام القالب الصحيح"""
        response = self.client.get(reverse('services:service_list'))
        self.assertTemplateUsed(response, 'services/service_list.html')

    def test_service_list_contains_service(self):
        """اختبار أن قائمة الخدمات تحتوي على الخدمة"""
        response = self.client.get(reverse('services:service_list'))
        self.assertContains(response, 'خدمة تجريبية')

    def test_inactive_service_not_shown(self):
        """اختبار أن الخدمات غير النشطة لا تظهر"""
        self.service.is_active = False
        self.service.save()
        response = self.client.get(reverse('services:service_list'))
        self.assertNotContains(response, 'خدمة تجريبية')

    def test_search_filter(self):
        """اختبار البحث"""
        response = self.client.get(reverse('services:service_list') + '?search=تجريبية')
        self.assertContains(response, 'خدمة تجريبية')
        
        response = self.client.get(reverse('services:service_list') + '?search=غيرموجود')
        self.assertNotContains(response, 'خدمة تجريبية')


class ServiceDetailViewTest(TestCase):
    """اختبارات عرض تفاصيل الخدمة"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@test.com', 'testpass123')
        self.provider = Provider.objects.create(
            user=self.user,
            display_name='مقدم تجريبي',
            is_active=True
        )
        self.category = Category.objects.create(
            name='تصنيف تجريبي',
            slug='test-category',
            is_active=True
        )
        self.service = Service.objects.create(
            category=self.category,
            provider=self.provider,
            title='خدمة تجريبية',
            slug='test-service',
            summary='ملخص الخدمة',
            description='وصف تفصيلي',
            price=100,
            is_active=True
        )

    def test_service_detail_view_status_code(self):
        """اختبار أن صفحة تفاصيل الخدمة تعمل"""
        response = self.client.get(
            reverse('services:service_detail', kwargs={'slug': self.service.slug})
        )
        self.assertEqual(response.status_code, 200)

    def test_service_detail_view_template(self):
        """اختبار استخدام القالب الصحيح"""
        response = self.client.get(
            reverse('services:service_detail', kwargs={'slug': self.service.slug})
        )
        self.assertTemplateUsed(response, 'services/service_detail.html')

    def test_views_count_increment(self):
        """اختبار زيادة عدد المشاهدات"""
        initial_views = self.service.views_count
        self.client.get(
            reverse('services:service_detail', kwargs={'slug': self.service.slug})
        )
        self.service.refresh_from_db()
        self.assertEqual(self.service.views_count, initial_views + 1)

    def test_inactive_service_returns_404(self):
        """اختبار أن الخدمة غير النشطة ترجع 404"""
        self.service.is_active = False
        self.service.save()
        response = self.client.get(
            reverse('services:service_detail', kwargs={'slug': self.service.slug})
        )
        self.assertEqual(response.status_code, 404)
