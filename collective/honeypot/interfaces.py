from zope import schema
from zope.interface import Interface


class IHoneypot(Interface):
    """Honeypot text field.
    """
    # Keep field title empty so visitors do not see it.
    honeypot = schema.TextLine(title=u"", required=False)
