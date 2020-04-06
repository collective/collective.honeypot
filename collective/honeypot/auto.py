import logging
from urlparse import urlparse

from collective.honeypot import config
from lxml import etree
from plone.protect.authenticator import createToken
from plone.protect.auto import ProtectTransform
from zope.component import ComponentLookupError

LOGGER = logging.getLogger("collective.honeypot")


class ProtectHoneyTransform(ProtectTransform):
    """
    XXX Need to be extremely careful with everything we do in here
    since an error here would mean the transform is skipped
    and no CSRF protection...
    """

    def transform(self, result, encoding):
        result = self.parseTree(result, encoding)
        if result is None:
            return None
        root = result.tree.getroot()
        url = urlparse(self.request.URL)
        try:
            token = createToken(manager=self.key_manager)
        except ComponentLookupError:
            if self.site is not None:
                LOGGER.warn('Keyring not found on site. This should not happen', exc_info=True)
            return result

        for form in root.cssselect('form'):
            # XXX should we only do POST? If we're logged in and
            # it's an internal form, I'm inclined to say no...
            # method = form.attrib.get('method', 'GET').lower()
            # if method != 'post':
            #    continue

            # some get forms we definitely do not want to protect.
            # for now, we know search we do not want to protect
            method = form.attrib.get('method', 'GET').lower()
            action = form.attrib.get('action', '').strip()
            if method == 'get' and '@@search' in action:
                continue
            action = form.attrib.get('action', '').strip()
            if not self.isActionInSite(action, url):
                continue
            # check if the token is already on the form..
            hidden = form.cssselect('[name="_authenticator"]')
            if len(hidden) == 0:
                hidden = etree.Element("input")
                hidden.attrib['name'] = '_authenticator'
                hidden.attrib['type'] = 'hidden'
                hidden.attrib['value'] = token
                form.append(hidden)
                # Change compared to original: add honeypot field.
                # We create this:
                # <div style="display: none">
                #   <input type="text" value=""
                #          tal:attributes="name view/honeypot_field_name" />
                # </div>
                #
                # XXX Ultimately this is not needed.  Or rather, it is not
                # enough.  This code is only called for authenticated users.
                # But on for example the contact-info form we need the honeypot
                # field for anonymous users.  So we need to do something else.
                container = etree.Element("div")
                container.attrib['style'] = 'display: none'
                honeypot = etree.Element("input")
                honeypot.attrib['name'] = config.HONEYPOT_FIELD
                honeypot.attrib['type'] = 'text'
                honeypot.attrib['value'] = ''
                container.append(honeypot)
                form.append(container)

        return result
