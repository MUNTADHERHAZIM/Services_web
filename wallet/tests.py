"""
Wallet Tests - اختبارات شاملة لنظام المحفظة وشحن وسحب الرصيد وتدقيق السوبر أدمن
"""

from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from wallet.models import Wallet, Transaction, DepositMethod, DepositRequest, WithdrawalRequest, Receipt


class WalletSystemTests(TestCase):
    def setUp(self):
        self.client = Client()

        # مستخدم عادي
        self.user = User.objects.create_user(
            username='ahmed_client',
            email='ahmed@example.com',
            password='TestPassword123!',
            first_name='أحمد',
            last_name='علي'
        )

        # مدير نظام (Staff / Superuser)
        self.admin_user = User.objects.create_superuser(
            username='admin_boss',
            email='admin@example.com',
            password='AdminPassword123!'
        )

        # وسيلة شحن
        self.deposit_method = DepositMethod.objects.create(
            name='زين كاش (ZainCash)',
            account_name='إدارة المنصة',
            account_number='07701234567',
            instructions='يرجى التحويل وإرفاق الوصل',
            min_amount=Decimal('5.00'),
            max_amount=Decimal('1000.00'),
            is_active=True,
            display_order=1
        )

    def get_test_image(self):
        import io
        from PIL import Image
        f_io = io.BytesIO()
        img = Image.new('RGB', (20, 20), color='green')
        img.save(f_io, 'PNG')
        f_io.seek(0)
        return SimpleUploadedFile('test_receipt.png', f_io.read(), content_type='image/png')

    def test_wallet_created_for_user(self):
        """التحقق من إنشاء محفظة تلقائياً للمستخدم برصيد صفري"""
        wallet, created = Wallet.objects.get_or_create(user=self.user)
        self.assertEqual(wallet.balance, Decimal('0'))
        self.assertEqual(wallet.available_balance, Decimal('0'))
        self.assertEqual(wallet.frozen_balance, Decimal('0'))

    def test_my_wallet_view_authenticated(self):
        """التحقق من فتح صفحة المحفظة للمستخدم المسجل بنجاح"""
        self.client.login(username='ahmed_client', password='TestPassword123!')
        response = self.client.get(reverse('wallet:my_wallet'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'المحفظة والرصيد المالي')
        self.assertContains(response, 'زين كاش (ZainCash)')

    def test_deposit_request_submission_and_approval(self):
        """التحقق من دورة تقديم طلب شحن الرصيد والموافقة عليه من الإدارة"""
        self.client.login(username='ahmed_client', password='TestPassword123!')

        # 1. إرسال طلب الشحن مع وصل التحويل
        post_data = {
            'deposit_method': self.deposit_method.id,
            'amount': '50.00',
            'sender_name': 'أحمد علي',
            'sender_phone': '07701234567',
            'transaction_reference': 'TX-987654321',
            'receipt_image': self.get_test_image(),
        }
        response = self.client.post(reverse('wallet:deposit'), post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        # التحقق من إنشاء طلب الشحن والمعاملة المعلقة
        deposit_req = DepositRequest.objects.get(transaction_reference='TX-987654321')
        self.assertEqual(deposit_req.status, DepositRequest.Status.PENDING)
        self.assertEqual(deposit_req.amount, Decimal('50.00'))

        wallet = Wallet.objects.get(user=self.user)
        # الرصيد لم يتغير بعد لأن الطلب قيد الانتظار
        self.assertEqual(wallet.balance, Decimal('0.00'))

        # المعاملة المسجلة بحالة معلقة
        pending_tx = Transaction.objects.get(reference_id=deposit_req.reference_id)
        self.assertEqual(pending_tx.status, Transaction.TransactionStatus.PENDING)

        # 2. قيام السوبر أدمن بالموافقة على الطلب
        deposit_req.approve(admin_user=self.admin_user, admin_notes='تم التحقق من الحوالة.')

        deposit_req.refresh_from_db()
        wallet.refresh_from_db()
        pending_tx.refresh_from_db()

        self.assertEqual(deposit_req.status, DepositRequest.Status.APPROVED)
        self.assertEqual(wallet.balance, Decimal('50.00'))
        self.assertEqual(wallet.available_balance, Decimal('50.00'))
        self.assertEqual(pending_tx.status, Transaction.TransactionStatus.COMPLETED)

    def test_deposit_request_rejection(self):
        """التحقق من رفض طلب شحن الرصيد من قبل الإدارة دون المساس بالأرصدة"""
        deposit_req = DepositRequest.objects.create(
            wallet=self.user.wallet,
            deposit_method=self.deposit_method,
            amount=Decimal('100.00'),
            sender_name='أحمد علي',
            sender_phone='07701234567',
            transaction_reference='TX-REJECT-001',
            receipt_image=self.get_test_image(),
            reference_id='DEP-REJECT01',
            status=DepositRequest.Status.PENDING
        )
        Transaction.objects.create(
            wallet=self.user.wallet,
            transaction_type=Transaction.TransactionType.DEPOSIT,
            amount=Decimal('100.00'),
            status=Transaction.TransactionStatus.PENDING,
            reference_id=deposit_req.reference_id
        )

        deposit_req.reject(admin_user=self.admin_user, admin_notes='الصورة غير واضحة.')

        deposit_req.refresh_from_db()
        wallet = self.user.wallet
        wallet.refresh_from_db()
        tx = Transaction.objects.get(reference_id='DEP-REJECT01')

        self.assertEqual(deposit_req.status, DepositRequest.Status.REJECTED)
        self.assertEqual(wallet.balance, Decimal('0.00'))
        self.assertEqual(tx.status, Transaction.TransactionStatus.CANCELED)

    def test_withdrawal_request_freeze_and_approval(self):
        """التحقق من طلب سحب الرصيد، تجميد المبلغ، والموافقة عليه وخصمه"""
        wallet = self.user.wallet
        wallet.balance = Decimal('150.00')
        wallet.save()

        self.client.login(username='ahmed_client', password='TestPassword123!')

        # طلب سحب 50 دولار
        post_data = {
            'method': 'zain_cash',
            'amount': '50.00',
            'account_holder': 'أحمد علي حسن',
            'account_number': '07701234567',
            'bank_or_branch': '',
            'notes': 'تحويل سريع لو سمحتم'
        }
        response = self.client.post(reverse('wallet:withdraw'), post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        wallet.refresh_from_db()
        # المبلغ تم تجميده: الرصيد الكلي 150، المجمد 50، المتاح 100
        self.assertEqual(wallet.balance, Decimal('150.00'))
        self.assertEqual(wallet.frozen_balance, Decimal('50.00'))
        self.assertEqual(wallet.available_balance, Decimal('100.00'))

        w_req = WithdrawalRequest.objects.get(wallet=wallet)
        self.assertEqual(w_req.status, WithdrawalRequest.Status.PENDING)
        self.assertEqual(w_req.amount, Decimal('50.00'))

        # قيام الإدارة بالموافقة على السحب بعد التحويل
        w_req.approve(admin_user=self.admin_user, admin_notes='تم التحويل عبر زين كاش.')

        w_req.refresh_from_db()
        wallet.refresh_from_db()

        self.assertEqual(w_req.status, WithdrawalRequest.Status.COMPLETED)
        self.assertEqual(wallet.balance, Decimal('100.00'))
        self.assertEqual(wallet.frozen_balance, Decimal('0.00'))
        self.assertEqual(wallet.available_balance, Decimal('100.00'))
        self.assertEqual(wallet.total_withdrawn, Decimal('50.00'))

    def test_withdrawal_request_rejection_unfreezes_funds(self):
        """التحقق من رفض طلب السحب وإلغاء تجميد الرصيد ليعود متاحاً فوراً"""
        wallet = self.user.wallet
        wallet.balance = Decimal('100.00')
        wallet.frozen_balance = Decimal('40.00')
        wallet.save()

        w_req = WithdrawalRequest.objects.create(
            wallet=wallet,
            amount=Decimal('40.00'),
            method='qi_card',
            account_info={'account_holder': 'أحمد علي', 'account_number': '123456'},
            status=WithdrawalRequest.Status.PENDING
        )

        w_req.reject(admin_user=self.admin_user, admin_notes='رقم البطاقة غير صحيح.')

        wallet.refresh_from_db()
        self.assertEqual(wallet.frozen_balance, Decimal('0.00'))
        self.assertEqual(wallet.available_balance, Decimal('100.00'))
        self.assertEqual(wallet.balance, Decimal('100.00'))

    def test_user_can_cancel_pending_withdrawal(self):
        """التحقق من إمكانية إلغاء المستخدم لطلب السحب بنفسه واستعادة الرصيد المتاح"""
        wallet = self.user.wallet
        wallet.balance = Decimal('80.00')
        wallet.frozen_balance = Decimal('30.00')
        wallet.save()

        w_req = WithdrawalRequest.objects.create(
            wallet=wallet,
            amount=Decimal('30.00'),
            method='bank',
            account_info={'account_holder': 'أحمد علي', 'account_number': 'IQ0001'},
            status=WithdrawalRequest.Status.PENDING
        )

        self.client.login(username='ahmed_client', password='TestPassword123!')
        response = self.client.post(reverse('wallet:cancel_withdrawal', args=[w_req.pk]), follow=True)
        self.assertEqual(response.status_code, 200)

        wallet.refresh_from_db()
        w_req.refresh_from_db()
        self.assertEqual(wallet.frozen_balance, Decimal('0.00'))
        self.assertEqual(wallet.available_balance, Decimal('80.00'))
        self.assertEqual(w_req.status, WithdrawalRequest.Status.REJECTED)

    def test_western_union_withdrawal_request(self):
        """التحقق من تقديم طلب سحب عبر ويسترن يونيون وتوليد السند المالي بنجاح"""
        wallet = self.user.wallet
        wallet.balance = Decimal('200.00')
        wallet.save()

        self.client.login(username='ahmed_client', password='TestPassword123!')
        post_data = {
            'method': 'western_union',
            'amount': '75.00',
            'account_holder': 'Ahmed Ali Hassan',
            'account_number': '07701234567',
            'bank_or_branch': 'العراق - بغداد / الكرخ',
            'notes': 'يرجى إرسال رقم MTCN فور التحويل'
        }
        response = self.client.post(reverse('wallet:withdraw'), post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        w_req = WithdrawalRequest.objects.get(wallet=wallet, method='western_union')
        self.assertEqual(w_req.amount, Decimal('75.00'))
        self.assertEqual(w_req.get_method_display(), 'ويسترن يونيون (Western Union)')

        # اعتماد الطلب وتوليد الوصل
        w_req.approve(admin_user=self.admin_user, admin_notes='تم إرسال حوالة ويسترن يونيون MTCN: 123-456-7890')
        w_req.refresh_from_db()
        self.assertEqual(w_req.status, WithdrawalRequest.Status.COMPLETED)

        receipt = Receipt.objects.filter(withdrawal_request=w_req).first()
        self.assertIsNotNone(receipt)
        self.assertIn("ويسترن يونيون", receipt.title)

    def test_receipt_created_for_deposit_and_viewable(self):
        """التحقق من إنشاء وصل مالي رسمي معتمد لشحن الرصيد والقدرة على استعراضه"""
        deposit_req = DepositRequest.objects.create(
            wallet=self.user.wallet,
            deposit_method=self.deposit_method,
            amount=Decimal('75.00'),
            sender_name='أحمد علي',
            sender_phone='07701234567',
            transaction_reference='TX-REC-TEST-01',
            receipt_image=self.get_test_image(),
            reference_id='DEP-RECTEST01',
            status=DepositRequest.Status.PENDING
        )
        # الموافقة على الطلب تؤدي لإنشاء الوصل
        deposit_req.approve(admin_user=self.admin_user)

        receipt = Receipt.objects.filter(deposit_request=deposit_req).first()
        self.assertIsNotNone(receipt)
        self.assertEqual(receipt.status, Receipt.Status.COMPLETED)
        self.assertEqual(receipt.total_amount, Decimal('75.00'))
        self.assertTrue(bool(receipt.qr_code_svg))
        self.assertTrue(bool(receipt.security_hash))

        # استعراض الوصل من قبل صاحب الحساب
        self.client.login(username='ahmed_client', password='TestPassword123!')
        response = self.client.get(reverse('wallet:receipt_detail', args=[receipt.receipt_number]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, receipt.receipt_number)
        self.assertContains(response, 'وثيقة مالية رسمية معتمدة')

        # التحقق الرقمي العام من الوصل
        self.client.logout()
        verify_response = self.client.get(reverse('wallet:receipt_verify', args=[receipt.verification_token]))
        self.assertEqual(verify_response.status_code, 200)
        self.assertContains(verify_response, receipt.receipt_number)
        self.assertContains(verify_response, 'وثيقة مالية رسمية موثقة ومعتمدة')

    def test_my_receipts_list_view(self):
        """التحقق من فتح صفحة أرشيف الفواتير والوصولات الرسمية للمستخدم"""
        self.client.login(username='ahmed_client', password='TestPassword123!')
        response = self.client.get(reverse('wallet:my_receipts'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'سجل الفواتير والوصولات الرسمية')
