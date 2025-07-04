.. contents::
.. Table of contents


Introduction
============

This package gives honeypot protection for forms.

Use cases
=========

Spammers have found you and are pounding various forms on your
website. Prime victims are the join form, contact form, sendto form
and comment form.

Maybe you have some captcha protection in place but spammers have
found a way around it.  Or you want to detect a spammer before doing a
possibly time consuming validation.

You have noticed that some scripts send e-mails or add a comment even
when they receive a ``GET`` instead of a ``POST`` request.

You do not want to put up any user unfriendly captchas, but do not
want to make it easy for spammers either.

Or, rather differently, you wonder if you can temporarily disallow all
``POST`` requests while you are doing a big migration.


Idea
====

One anti-spam idea that has found adoption is a honeypot: adding a
field that would never be filled in by a human.  The reasoning is that
spammers will likely fill in all fields in a form, for two reasons:

1. The bots do not know which fields are required, so they
   fill everything in, just to be sure.

2. After a successful submission, each field might be shown on the
   website, so they fill all fields to get their message in the face
   of unsuspecting visitors.

The field should be hidden so it does not distract humans.  But:
making the input type hidden could mean that a spammer ignores it and
does not fill it in after all, so we hide it with css instead.

Some spambots seem to know a bit about Plone.  They know which fields
are required on a few forms in a standard Plone website without
captchas, or they even know a way around validation.  If we add an
invisible field they will simply not use it.  So: for a few explicitly
selected forms we require that the invisible field is in the submitted
form, although it must be empty.


Translations
============

This product has been translated into

- Italian

- Spanish


Installation and usage
======================

Add ``collective.honeypot`` to the eggs of your Zope instance in your
buildout config:

::

  [instance]
  eggs =
      collective.honeypot

Run buildout and start the Zope instance.

What does this do?

- This registers overrides for several templates and scripts (using
  `z3c.jbot <https://github.com/zopefoundation/z3c.jbot>`_).

- It adds those templates and scripts to the list of extra protected
  actions.  This means that a ``POST`` request to these actions now
  **must** have the honeypot field and it **must** be empty.


Fixes
=====

Some scripts in standard Plone happily add a comment or send an e-mail
when you use a ``GET`` request.  This package does not agree with that
policy and has fixes to require a ``POST`` request.

When using ``z3c.jbot``, the package detects which fixes are needed.
Some add-ons may or may not be
available, so we only load fixes that can be applied, especially for
`plone.app.discussion <https://github.com/plone/plone.app.discussion>`_.

If you override a script or template in an own skin layer or via some
zcml, then our fixes may have no effect, so you need to do a fix
yourself.

So, what are the actual fixes that this package contains?

- Some forms may get the invisible honeypot field automatically.  This
  package registers an override for the ``@@authenticator`` view from
  `plone.protect <https://github.com/plone/plone.protect>`_ that is used in several templates for CSRF
  protection (cross site request forgery).  So any template that
  already uses this, is automatically loading our honeypot field.

- ``plone.app.discussion``:

  - Add the honeypot field to the 'add comment' form.  This fix is
    only done when you load ``fixes.zcml``.

  - The honeypot field is *not* required, because the 'add comment'
    form posts to the context, not to a specific action.

- Plone:

  - Require ``POST`` for the ``send_feedback_site`` and ``sendto``
    scripts.

  - Add the honeypot field to the ``sendto_form`` and ``contact-info``
    forms.

  - The register form is automatically protected by our
    ``@@authenticator`` override.

  - Require the honeypot field for the above actions and the join
    form, specifically: ``sendto_form``, ``sendto``, ``contact-info``,
    ``send_feedback_site``, ``register``, ``join_form``.



Protecting your own forms
=========================

In a form that you want to protect, you must add this:

::

  <div tal:replace="structure context/@@honeypot_field|nothing" />

This is all that is needed to have the basic protection of an
invisible field that captures spammers if they fill it in.  A
``Forbidden`` exception is raised in that case.

Some forms may get this invisible field automatically.  This package
registers an override for the ``@@authenticator`` view from
``plone.protect`` that is used in several templates for CSRF
protection (cross site request forgery).  So any template that already
uses this, is automatically loading our honeypot field.

For extra protection, you can add the page on which the form appears
to the ``EXTRA_PROTECTED_ACTIONS``.  This means that the ``Forbidden``
exception is also raised if the field is not submitted in the form at
all.  See the Configuration_ section.

Note that it would be nice to accept all posts from authenticated
users, but our code is run too early in the Zope process: we cannot
know yet if the user is logged in or not.


Configuration
=============

There is no configuration that you can do within a Plone Site.  That
would be too easy to get wrong, possibly even disabling the means to
undo the damage.  Also, with multiple Plone Sites in one Zope instance
this would get even trickier.  So we chose a different approach.

You can configure settings via environment variables in the
``zope.conf`` of your Zope instance.  For testing you could set an
environment variable in your command shell and start the Zope instance
and it will get picked up.  But the usual way would be to do this in
``buildout.cfg``:

::

  [instance]
  environment-vars =
      HONEYPOT_FIELD pooh
      EXTRA_PROTECTED_ACTIONS discussion_reply join_form sendto_form
      ALLOWLISTED_ACTIONS jq_reveal_email
      ALLOWLISTED_START jq_*
      IGNORED_FORM_FIELDS secret_field
      ACCEPTED_LOG_LEVEL info
      SPAMMER_LOG_LEVEL error
      DISALLOW_ALL_POSTS no

General notes:

- None of the options are required.  It will work fine without any
  environment variables.

- Values are split on whitespace or comma.

- Any ``@`` character gets automatically replaced by a space, to make
  it easier to reference ``@@some_view`` by simply ``some_view``, as
  we always protect them both.

These are the supported variables:

HONEYPOT_FIELD
    Name to use as input name of the honeypot field.  If you give no
    value here, no honeypot checks are done, so you only get some
    logging.  This is obviously not the main goal of this package, but
    it may be useful when you need to do some debugging.  If you do
    not list the variable, you get the default value of
    ``protected_1``.  In case spammers learn about this package and do
    not fill in the standard name, you can change the name here.

EXTRA_PROTECTED_ACTIONS
    For these form actions the honeypot field is required: the field
    **must** be in the posted request, though it of course still **must**
    be empty.  If you add actions here but do not change the forms,
    they become unusable for visitors, which is not what you want.  On
    the other hand, if you have a form that you no longer wish to use,
    you can add it here and it will stop functioning.  For ``@@view``
    simply use ``view`` and it will match both.

ALLOWLISTED_ACTIONS
    These form actions are not checked.  List here actions that are
    harmless, for example actions that load some data via an AJAX
    call.  Generally, actions that change nothing in the database and
    do not send emails are safe to add here.  If you add this
    environment variable but leave it empty, you override the
    default and do not allow anything.  By default we allow
    these actions:

    - ``at_validate_field`` (inline validation)

    - ``atct_edit`` (edit form)

    - ``edit`` (edit form)

    - ``kssValidateField`` (inline validation)

    - ``jq_reveal_email`` (``zest.emailhider``)

    - ``z3cform_validate_field``  (inline validation)



ALLOWLISTED_START
    Form actions starting with one of these strings are not checked.
    See ``ALLOWLISTED_ACTIONS`` for more info.  If you have lots of
    harmless actions that start with ``jq_`` you can add that string
    to this list.  Regular expression are too easy to get wrong, so we
    do not support it.

IGNORED_FORM_FIELDS
    We log information about ``POST`` requests, to allow a system admin to
    go through the log and discover posts that are obviously spam
    attempts but are not caught yet and need extra handling, perhaps
    an extra form that should get protection.  This information may
    contain form fields that should be left secret or that are not
    interesting.  No matter what you fill in here, we always ignore
    fields that contain the term `password`.

ACCEPTED_LOG_LEVEL
    Log level for accepted posts.  This accepts standard lower or
    upper case log levels: debug, info, warn, warning, error,
    critical.  When an unknown level is used or the setting is empty,
    we fall back to the default: ``DEBUG``.

SPAMMER_LOG_LEVEL
    Log level for caught spammers.  This accepts standard lower or
    upper case log levels: debug, info, warn, warning, error,
    critical.  When an unknown level is used or the setting is empty,
    we fall back to the default: ``ERROR``.

DISALLOW_ALL_POSTS
    Set this to ``1``, ``on``, ``true``, or ``yes`` to disallow all
    ``POST`` requests.  This may be handy if you want to effectively
    make a Plone Site read-only, for example in preparation of a
    security release or when you are doing a big migration in a new
    Zope instance and want to keep the old instance alive for the time
    being.  Note that, like the rest of the checks, this only has an
    effect in a Plone (or CMF) site, not in the Zope root.


When are the checks *not* done?
===============================

This package does not check fields on any ``GET`` requests, it actually blocks
the ``GET`` requests on selected forms and requires a ``POST`` there. Hence the
field checks only work on ``POST`` requests.

If you have made the ``HONEYPOT_FIELD`` configuration option empty, no
honeypot checks are done, so you only get some logging.

If Zope does any traversal, only the original action is checked.  For
example:

- A visitor makes a POST request to a ``my_form`` action.  The
  honeypot checks are done for that action.

- The ``my_form`` action may be an old-style CMF form controller
  action that calls a validation script ``validate_my_form``.  This
  validation script does *not* get honeypot checks.

- After validation, the action may do a traverse to a script
  ``do_action`` that does the real work, like changing the database or
  sending an email.  This script does *not* get honeypot checks.

As an aside, if you have such a setup, you should make sure the
``do_action`` script calls a validation script too and only accepts
``POST`` requests.  Otherwise a smart spammer can bypass the
``validate_my_form`` validation script by requesting the ``do_action``
script directly.  And he can bypass the honeypot checks by using a
``GET`` request.


z3c.form
========

You can easily add a honeypot field to a ``z3c.form``.  Just add a
``TextLine`` field to your form ``Interface`` definition, set the
``widgetFactory`` to the widget that ``collective.honeypot`` supplies,
and make it hidden. Something like this:

::

  from collective.honeypot.z3cform.widget import HoneypotFieldWidget
  from z3c.form import form, interfaces
  from zope import schema
  from zope.interface import Interface

  class IHoneypot(Interface):
      # Keep field title empty so visitors do not see it.
      honeypot = schema.TextLine(title=u"", required=False)

  class MyForm(form.Form):
      fields = form.field.Fields(IHoneypot)

      def update(self):
          self.fields['honeypot'].widgetFactory = HoneypotFieldWidget
          self.fields['honeypot'].mode = interfaces.HIDDEN_MODE

See ``collective/honeypot/discussion/z3cformextender.py`` for an
example of how to extend an existing form, in this case the comment
form in ``plone.app.discussion``.


Compatibility
=============

This works on:

- Plone 5.2.

- Plone 6.0.

- Plone 6.1.
