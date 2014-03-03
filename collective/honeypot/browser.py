from Products.Five import BrowserView
from collective.honeypot import config


class HoneypotField(BrowserView):
    honeypot_field_name = config.HONEYPOT_FIELD
