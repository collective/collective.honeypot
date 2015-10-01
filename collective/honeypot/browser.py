from collective.honeypot import config
from plone.protect.authenticator import AuthenticatorView
from zope.component import getMultiAdapter


class HoneypotFieldView(AuthenticatorView):
    honeypot_field_name = config.HONEYPOT_FIELD


class HoneypotAuthenticatorView(AuthenticatorView):

    def authenticator(self, extra='', name='_authenticator'):
        csrf = super(HoneypotAuthenticatorView, self).authenticator()
        honeypot_view = getMultiAdapter(
            (self.context, self.request), name='honeypot_field')
        honeypot = honeypot_view()
        return csrf + honeypot
