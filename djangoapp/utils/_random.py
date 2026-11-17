from random import SystemRandom
import string
from django.utils.text import slugify

def random_letters(k) -> str:
    return ''.join(
        SystemRandom().choices(
        string.ascii_letters + string.digits,
        k= k,)
    )

def new_slugify(text, k):
    return slugify(text + '-' + random_letters(k))

