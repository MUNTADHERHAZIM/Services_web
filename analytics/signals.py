from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from accounts.models import Provider
from requests.models import ServiceRequest
from analytics.models import ProviderStats
from wallet.models import Wallet, Transaction

@receiver(post_save, sender=Provider)
def create_provider_stats(sender, instance, created, **kwargs):
    """إنشاء إحصائيات المزود تلقائياً عند إنشاء مزود جديد"""
    if created:
        ProviderStats.objects.get_or_create(provider=instance)

@receiver(post_save, sender=ServiceRequest)
def update_provider_stats_and_wallet(sender, instance, **kwargs):
    """تحديث إحصائيات المزود ومحفظته تلقائياً عند تغيير حالة الطلب"""
    service = instance.service
    provider = service.provider
    
    # التأكد من وجود كائن الإحصائيات
    stats, _ = ProviderStats.objects.get_or_create(provider=provider)
    
    # 1. تحديث أرقام الطلبات
    all_requests = ServiceRequest.objects.filter(service__provider=provider)
    stats.total_orders = all_requests.count()
    stats.completed_orders = all_requests.filter(status='done').count()
    stats.canceled_orders = all_requests.filter(status='canceled').count()
    
    # 2. احتساب الأرباح المعلقة والمنفذة
    pending_statuses = ['approved', 'in_progress', 'in_review', 'new']
    pending_requests = all_requests.filter(status__in=pending_statuses)
    stats.pending_balance = pending_requests.aggregate(total=Sum('service__price'))['total'] or 0
    
    completed_requests = all_requests.filter(status='done')
    stats.total_earnings = completed_requests.aggregate(total=Sum('service__price'))['total'] or 0
    
    # 3. تحديث المحفظة الافتراضية والمعاملات
    provider_user = provider.user
    wallet, _ = Wallet.objects.get_or_create(user=provider_user)
    
    if instance.status == 'done':
        # التحقق مما إذا كانت المعاملة مسجلة مسبقاً
        transaction_exists = Transaction.objects.filter(
            wallet=wallet,
            transaction_type=Transaction.TransactionType.ORDER_EARNING,
            related_order=instance,
            status=Transaction.TransactionStatus.COMPLETED
        ).exists()
        
        if not transaction_exists:
            # إنشاء معاملة جديدة
            Transaction.objects.create(
                wallet=wallet,
                transaction_type=Transaction.TransactionType.ORDER_EARNING,
                amount=service.price,
                status=Transaction.TransactionStatus.COMPLETED,
                related_order=instance,
                description=f"أرباح الطلب #{instance.pk} لخدمة '{service.title}'"
            )
            # تحديث المحفظة
            wallet.balance += service.price
            wallet.total_earned += service.price
            wallet.save()
            
    elif instance.status == 'canceled':
        # إذا تم إلغاء الطلب وكان قد اكتمل سابقاً، نقوم بعكس المعاملة
        earning_transaction = Transaction.objects.filter(
            wallet=wallet,
            transaction_type=Transaction.TransactionType.ORDER_EARNING,
            related_order=instance,
            status=Transaction.TransactionStatus.COMPLETED
        ).first()
        
        if earning_transaction:
            earning_transaction.status = Transaction.TransactionStatus.CANCELED
            earning_transaction.save()
            
            # خصم من المحفظة
            wallet.balance -= service.price
            wallet.total_earned -= service.price
            wallet.save()
            
    # تحديث الرصيد المتاح والمعلق في الإحصائيات
    stats.available_balance = wallet.balance
    stats.save()
