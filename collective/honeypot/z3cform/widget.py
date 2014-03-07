import zope.interface
from collective.honeypot import config
from z3c.form.browser import text
from z3c.form.interfaces import IWidget
from z3c.form.widget import FieldWidget


class IHoneypotWidget(IWidget):
    """Marker interface for the honeypot widget
    """


class HoneypotWidget(text.TextWidget):
    zope.interface.implementsOnly(IHoneypotWidget)
    honeypot_field_name = config.HONEYPOT_FIELD

    def update(self):
        super(HoneypotWidget, self).update()
        # Force the configured name of our honeypot field.
        self.name = self.id = config.HONEYPOT_FIELD


def HoneypotFieldWidget(field, request):
    """IFieldWidget factory for HoneypotWidget."""
    return FieldWidget(field, HoneypotWidget(request))
