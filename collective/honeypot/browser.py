from collective.honeypot import config
from plone.protect.authenticator import AuthenticatorView


class HoneypotAuthenticatorView(AuthenticatorView):
    honeypot_field_name = config.HONEYPOT_FIELD

    def authenticator(self, extra='', name='_authenticator'):
        csrf = super(HoneypotAuthenticatorView, self).authenticator()
        honeypot = self.index()
        return csrf + honeypot
