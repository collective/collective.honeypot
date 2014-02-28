from Products.Five import BrowserView
from collective.honeypot import config


class HoneyFields(BrowserView):
    forbidden_field_name = config.FORBIDDEN_HONEYPOT_FIELD
    required_field_name = config.REQUIRED_HONEYPOT_FIELD
