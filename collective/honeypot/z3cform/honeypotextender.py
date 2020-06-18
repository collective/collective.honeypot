from collective.honeypot.interfaces import IHoneypot
from collective.honeypot.z3cform.widget import HoneypotFieldWidget
from plone.z3cform.fieldsets import extensible
from z3c.form import interfaces
from z3c.form.field import Fields


class HoneypotExtender(extensible.FormExtender):
    """Extends the comment form with a honeypot field.
    """

    fields = Fields(IHoneypot)

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form

    def update(self):
        self.add(IHoneypot, prefix="")
        self.form.fields["honeypot"].widgetFactory = HoneypotFieldWidget
        self.form.fields["honeypot"].mode = interfaces.HIDDEN_MODE

