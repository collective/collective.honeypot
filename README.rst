.. contents::
.. Table of contents


Introduction
============

This package gives honeypot protection for forms.

.. warning:: I [Maurits] want to move this to the github collective,
   but I want to do some more fixes and tell the Plone Security Team
   about this to get their opinion before making this public.
   Probably not needed, but let's be careful.


Use case
========

Spammers have found you and are pounding various forms on your
website.  Prime victims are the join form, contact form, sendto form
and comment form.

Maybe you have some captcha protection in place but spammers have
found a way around it.  Or you want to detect a spammer before doing a
possibly time consuming validation.

Or you do not want to put up any user unfriendly captchas but do not
want to make it easy for spammers either.


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


Installation and usage
======================

Add ``collective.honeypot`` to the eggs of your zope instance in your
buildout config.  In Plone 3.2 or lower (untested) you need to add it
to the zcml option as well.  Run buildout and start the zope instance.

At this point it does not do anything yet, except that it logs some
info whenever someone does a ``POST``.  You should take some measures to
make it actually protect forms.  Every form that you want to protect,
needs a change.  You can do that yourself and/or load the standard
fixes from ``collective.honeypot``.

``collective.honeypot`` has fixes for a few standard Plone templates.
If you want to use them, you need to explicitly enable them by loading
the extra ``fixes`` dependencies (``z3c.jbot`` currently) and loading
``fixes.zcml``.  In your Plone 4 buildout config::

  [instance]
  eggs =
      collective.honeypot[fixes]
  zcml =
      collective.honeypot-fixes

Or in your Plone 3 buildout config::

  [instance]
  eggs =
      collective.honeypot[fixes]

**Important**: in Plone 3 you will get an error when running buildout
if you have ``-fixes`` in a zcml line.  So we have changed the
behavior of ``collective.honeypot`` in Plone 3.3: you do not need an
explicit zcml line, but we always load the fixes if you have
``collective.honeypot[fixes]`` in the eggs, or if ``z3c.jbot`` is in
the eggs in some other way.

**Important**: I have seen one Plone 3 site that could not start up
due to some incompatibility between our ``z3c.jbot`` dependency and
either Plone Go Mobile or Grok in general.  So do test it out locally
before rolling it out on a server.  For reference, the error was::

  Traceback (most recent call last):
  ...
    File ".../Zope-2.10.13-final-py2.4/lib/python/zope/configuration/config.py", line 206, in resolve
      return __import__(mname+'.'+oname, *_import_chickens)
    File "/Users/mauritsvanrees/shared-eggs/five.grok-1.0-py2.4.egg/five/grok/__init__.py", line 23, in ?
      from five.grok.components import Model, Container, Site, LocalUtility
    File "/Users/mauritsvanrees/shared-eggs/five.grok-1.0-py2.4.egg/five/grok/components.py", line 133, in ?
  class ViewPageTemplateFile(BaseViewPageTemplateFile):
  zope.configuration.xmlconfig.ZopeXMLConfigurationError: File ".../parts/instance/etc/site.zcml", line 14.2-14.55
      ZopeXMLConfigurationError: File
          ".../parts/instance/etc/package-includes/005-gomobile.convergence-configure.zcml", line 1.0-1.64
      ZopeXMLConfigurationError: File
          ".../gomobile.convergence-0.1dev_r369-py2.4.egg/gomobile/convergence/configure.zcml", line 13.4-13.64
      ZopeXMLConfigurationError: File
          ".../plone.directives.form-1.0b6-py2.4.egg/plone/directives/form/meta.zcml", line 6.4-6.52
      TypeError: Error when calling the metaclass bases
      Can't mix __of__ and descriptors

Okay, you have added the fixes.  What does that do?

- This registers overrides for several templates and scripts (using
  ``z3c.jbot``).

- It adds those templates and scripts to the list of extra protected
  actions.  This means that a ``POST`` request to these actions now
  **must** have the honeypot field and it **must** be empty.


Protecting your own forms
=========================

In a form that you want to protect, you must add this::

  <div tal:replace="structure context/@@honeypot_field|nothing" />

This is all that is needed to have the basic protection of an
invisible field that captures spammers if they fill it in.  A
``Forbidden`` exception is raised in that case.

Some forms may get this invisible field automatically.  This package
registers an override for the ``@@authenticator`` view from
``plone.protect`` that is used in several templates for csrf
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
``zope.conf`` of your zope instance.  For testing you could set an
environment variable in your command shell and start the zope instance
and it will get picked up.  But the usual way would be to do this in
``buildout.cfg``::

  [instance]
  environment-vars =
      HONEYPOT_FIELD pooh
      EXTRA_PROTECTED_ACTIONS discussion_reply join_form sendto_form
      WHITELISTED_ACTIONS jq_reveal_email
      WHITELISTED_START jq_*
      IGNORED_FORM_FIELDS secret_field
      ACCEPTED_LOG_LEVEL info
      SPAMMER_LOG_LEVEL error
      DISALLOW_ALL_POSTS no

- None of the options are required.  It will work fine without any
  environment variables.

- Values are split on whitespace or comma.

- Any ``@`` character gets automatically replaced by a space, to make
  it easier to reference ``@@some_view`` by simply ``some_view``, as
  we always protect them both.

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

WHITELISTED_ACTIONS
    These form actions are not checked.  List here actions that are
    harmless, for example actions that load some data via an AJAX
    call.  Generally, actions that change nothing in the database and
    do not send emails are safe to add here.  You could add
    ``edit`` and ``atct_edit`` to avoid logging the large dexterity
    and Archetypes edit forms.  But you may find this interesting, so
    suit yourself.

WHITELISTED_START
    Form actions starting with one of these strings are not checked.
    See ``WHITELISTED_ACTIONS`` for more info.  If you have lots of
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
    we fall back to the default: ``INFO``.

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
    zope instance and want to keep the old instance alive for the time
    being.  Note that, like the rest of the checks, this only has an
    effect in a Plone (or CMF) site, not in the Zope root.


When are the checks *not* done?
===============================

This package ignores ``GET`` requests.  It only works on POST requests.

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


Future
======

We can probably make it easier to add this to a form based on
``z3c.form`` or ``zope.formlib``.  It should be possible to do some
hack to add the fields automatically to every form.  Having an extra
field should be okay, although it may trip up a few automated tests.


Compatibility
=============

This works on Plone 3 and Plone 4.  Specifically, it has been tested
with Plone 3.3.6, 4.0.10, 4.1.6, 4.2.7, 4.3.2.

It does *not* work on Plone 2.5.  The zope event that we hook into is
simply not fired there.

