from django import template
from core.captcha import generate_captcha_challenge

register = template.Library()

@register.inclusion_tag('components/captcha.html', takes_context=True)
def render_captcha(context, input_name='captcha_code', token_name='captcha_token'):
    challenge = generate_captcha_challenge()
    return {
        'captcha_svg': challenge['svg'],
        'captcha_token': challenge['token'],
        'input_name': input_name,
        'token_name': token_name,
        'request': context.get('request'),
    }
