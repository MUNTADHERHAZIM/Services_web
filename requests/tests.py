"""
Requests Tests - اختبارات طلبات الخدمات
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Provider
from services.models import Category, Service
from requests.models import ServiceRequest


class ServiceRequestCreateTest(TestCase):
    """اختبارات إنشاء طلب خدمة"""
    
    def setUp(self):
        self.client = Client()
        
        # إنشاء مستخدم عميل
        self.customer = User.objects.create_user('customer', 'customer@test.com', 'testpass123')
        
        # إنشاء مقدم خدمة
        self.provider_user = User.objects.create_user('provider', 'provider@test.com', 'testpass123')
        self.provider = Provider.objects.create(
            user=self.provider_user,
            display_name='مقدم تجريبي',
            is_active=True
        )
        
        # إنشاء خدمة
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

    def test_request_create_requires_login(self):
        """اختبار أن إنشاء طلب يتطلب تسجيل الدخول"""
        response = self.client.get(
            reverse('requests:request_create', kwargs={'service_slug': self.service.slug})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_request_create_view_when_logged_in(self):
        """اختبار عرض صفحة إنشاء الطلب للمستخدم المسجل"""
        self.client.login(username='customer', password='testpass123')
        response = self.client.get(
            reverse('requests:request_create', kwargs={'service_slug': self.service.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests/request_create.html')

    def test_create_request_successfully(self):
        """اختبار إنشاء طلب بنجاح"""
        self.client.login(username='customer', password='testpass123')
        response = self.client.post(
            reverse('requests:request_create', kwargs={'service_slug': self.service.slug}),
            {
                'customer_notes': 'ملاحظات تجريبية',
                'contact_phone': '0501234567',
                'contact_email': 'customer@test.com'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(ServiceRequest.objects.filter(
            customer=self.customer,
            service=self.service
        ).exists())

    def test_request_initial_status_is_new(self):
        """اختبار أن حالة الطلب الجديد هي NEW"""
        self.client.login(username='customer', password='testpass123')
        self.client.post(
            reverse('requests:request_create', kwargs={'service_slug': self.service.slug}),
            {'customer_notes': 'ملاحظات'}
        )
        request = ServiceRequest.objects.get(customer=self.customer, service=self.service)
        self.assertEqual(request.status, 'new')

    def test_cannot_request_inactive_service(self):
        """اختبار عدم إمكانية طلب خدمة غير نشطة"""
        self.service.is_active = False
        self.service.save()
        self.client.login(username='customer', password='testpass123')
        response = self.client.get(
            reverse('requests:request_create', kwargs={'service_slug': self.service.slug})
        )
        self.assertEqual(response.status_code, 404)


class MyRequestsListTest(TestCase):
    """اختبارات قائمة طلباتي"""
    
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user('customer', 'customer@test.com', 'testpass123')
        self.other_user = User.objects.create_user('other', 'other@test.com', 'testpass123')
        
        self.provider_user = User.objects.create_user('provider', 'provider@test.com', 'testpass123')
        self.provider = Provider.objects.create(
            user=self.provider_user,
            display_name='مقدم',
            is_active=True
        )
        
        self.category = Category.objects.create(name='تصنيف', slug='cat', is_active=True)
        self.service = Service.objects.create(
            category=self.category,
            provider=self.provider,
            title='خدمة',
            slug='service',
            summary='ملخص',
            description='وصف',
            is_active=True
        )
        
        # إنشاء طلب للعميل
        self.request = ServiceRequest.objects.create(
            service=self.service,
            customer=self.customer,
            status='new'
        )

    def test_my_requests_requires_login(self):
        """اختبار أن طلباتي تتطلب تسجيل الدخول"""
        response = self.client.get(reverse('requests:my_requests'))
        self.assertEqual(response.status_code, 302)

    def test_my_requests_shows_only_user_requests(self):
        """اختبار أن قائمة الطلبات تظهر طلبات المستخدم فقط"""
        self.client.login(username='customer', password='testpass123')
        response = self.client.get(reverse('requests:my_requests'))
        self.assertContains(response, 'خدمة')
        
        # تسجيل دخول مستخدم آخر
        self.client.login(username='other', password='testpass123')
        response = self.client.get(reverse('requests:my_requests'))
        self.assertNotContains(response, 'خدمة')
