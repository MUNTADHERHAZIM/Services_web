from django import template
from decimal import Decimal

register = template.Library()

EXCHANGE_RATE = 1500  # 1 USD = 1,500 IQD

@register.filter(name='service_price')
def service_price(service, user_currency='IQD'):
    """
    يعرض سعر الخدمة بحسب العملة المفضلة للمستخدم
    إذا كانت IQD: يعرض بالدينار العراقي
    إذا كانت USD: يعرض بالدولار الأمريكي
    """
    if not service or not hasattr(service, 'get_primary_price_display'):
        return ''
    return service.get_primary_price_display(user_currency)


@register.filter(name='service_orig_price')
def service_orig_price(service, user_currency='IQD'):
    """
    يعرض السعر الأصلي للخدمة قبل الخصم بحسب العملة المفضلة للمستخدم
    """
    if not service or not hasattr(service, 'get_primary_original_price_display'):
        return ''
    return service.get_primary_original_price_display(user_currency) or ''


@register.filter(name='service_sec_price')
def service_sec_price(service, user_currency='IQD'):
    """
    يعرض السعر المعادل بالعملة البديلة (شفافية وراحة العميل)
    """
    if not service or not hasattr(service, 'get_secondary_price_display'):
        return ''
    return service.get_secondary_price_display(user_currency)


@register.filter(name='money_format')
def money_format(value, target_currency='IQD'):
    """
    تنسيق الأرقام النقدية مع رمز العملة
    """
    if value is None or value == '':
        return ''
    try:
        num = float(value)
    except (ValueError, TypeError):
        return value

    if target_currency == 'USD':
        return f"${num:,.2f}" if num % 1 != 0 else f"${int(num):,}"
    else:
        return f"{int(round(num)):,} د.ع"
