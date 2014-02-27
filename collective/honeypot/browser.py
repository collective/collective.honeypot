from Products.Five import BrowserView
from collective.honeypot import config


class HoneyFields(BrowserView):
    forbidden_field = config.FORBIDDEN_HONEYPOT_FIELD
    required_field = config.REQUIRED_HONEYPOT_FIELD
