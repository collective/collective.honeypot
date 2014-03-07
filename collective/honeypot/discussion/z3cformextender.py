# -*- coding: utf-8 -*-

from collective.honeypot.interfaces import IHoneypot
from collective.honeypot.z3cform.widget import HoneypotFieldWidget
from plone.app.discussion.browser.comments import CommentForm
from plone.z3cform.fieldsets import extensible
from z3c.form import interfaces
from z3c.form.field import Fields
from zope.component import adapts
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class HoneypotExtender(extensible.FormExtender):
    """Extends the comment form with a honeypot field.
    """
    # context, request, form
    adapts(Interface, IDefaultBrowserLayer, CommentForm)

    fields = Fields(IHoneypot)

    def __init__(self, context, request, form):
        self.context = context
        self.request = request
        self.form = form

    def update(self):
        self.add(IHoneypot, prefix="")
        self.form.fields['honeypot'].widgetFactory = HoneypotFieldWidget
        self.form.fields['honeypot'].mode = interfaces.HIDDEN_MODE
