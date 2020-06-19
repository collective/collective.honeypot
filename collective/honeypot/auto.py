from collective.honeypot import config
from lxml import etree
from lxml import html
from plone.transformchain.interfaces import ITransform
from repoze.xmliter.serializer import XMLSerializer
from repoze.xmliter.utils import getHTMLSerializer
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

import logging


logger = logging.getLogger("collective.honeypot")


@implementer(ITransform)
@adapter(Interface, Interface)
class ProtectHoneyTransform(object):

    order = 8200

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def parseTree(self, result, encoding):
        # if it's a redirect, the result shall not be transformed
        request = self.request

        if request.response.status in (301, 302):
            return None

        if isinstance(result, XMLSerializer):
            return result

        # hhmmm, this is kind of taken right out of plone.app.theming
        # maybe this logic(parsing dom) should be someone central?
        contentType = self.request.response.getHeader("Content-Type")
        if contentType is None or not contentType.startswith("text/html"):
            return None

        contentEncoding = self.request.response.getHeader("Content-Encoding")
        if contentEncoding and contentEncoding in ("zip", "deflate", "compress",):
            return None

        if isinstance(result, list) and len(result) == 1:
            # do not parse empty strings to omit warning log message
            if not result[0].strip():
                return None
        try:
            result = getHTMLSerializer(result, pretty_print=False, encoding=encoding)
            # We are going to force html output here always as XHTML
            # output does odd character encodings
            result.serializer = html.tostring
            return result
        except (AttributeError, TypeError, etree.ParseError):
            # XXX handle something special?
            logger.warn(
                "error parsing dom, failure to add csrf "
                "token to response for url %s" % self.request.URL
            )
            return None

    def transformBytes(self, result, encoding):
        result = result.decode(encoding, "ignore")
        return self.transformIterable([result], encoding)

    def transformString(self, result, encoding):
        return self.transformIterable([result], encoding)

    def transformUnicode(self, result, encoding):
        return self.transformIterable([result], encoding)

    def transformIterable(self, result, encoding):
        return self.transform(result, encoding)

    def transform(self, result, encoding):
        result = self.parseTree(result, encoding)
        if result is None:
            return None
        root = result.tree.getroot()

        for form in root.cssselect("form"):
            # some get forms we definitely do not want to protect.
            # for now, we know search we do not want to protect
            method = form.attrib.get("method", "GET").lower()
            action = form.attrib.get("action", "").strip()
            if method == "get" and "@@search" in action:
                continue
            action = form.attrib.get("action", "").strip()
            # check if the element is already on the form..
            hidden = form.cssselect('[name="{}"]'.format(config.HONEYPOT_FIELD))
            if len(hidden) == 0:
                # Change compared to original: add honeypot field.
                # We create this:
                # <div style="display: none">
                #   <input type="text" value=""
                #          tal:attributes="name view/honeypot_field_name" />
                # </div>
                #
                container = etree.Element("div")
                container.attrib["style"] = "display: none"
                honeypot = etree.Element("input")
                honeypot.attrib["name"] = config.HONEYPOT_FIELD
                honeypot.attrib["type"] = "text"
                honeypot.attrib["value"] = ""
                container.append(honeypot)
                form.append(container)

        return result
