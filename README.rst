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
making the input type hidden could mean spammers do not fill it in, so
we hide it with css.

Some spambots know a bit about Plone.  They know which fields are
enough to use some of the standard forms in a standard Plone website
without captchas, or they even know a way around validation.  If we
add an invisible field they will simply not use it.  So: for selected
forms we require that the invisible field is in the submitted form,
although it may be empty.


Installation and usage
======================

Add ``collective.honeypot`` to the eggs of your zope instance in your
buildout config.  In Plone 3.2 or lower you need to add it to the zcml
option as well.  Run buildout and start the zope instance.

At this point it does not do anything yet.  You should take some
measures to make it protect forms.

In a form you want to protect, you must add this::

  <div tal:replace="structure context/@@honeypot_field|nothing" />

This is all that is needed to have the basic protection of an
invisible field that captures spammers if they fill it in.  A
``Forbidden`` exception is raised in that case.

Some forms may get that invisible field automatically.  This package
registers an override for the ``@@authenticator`` view from
``plone.protect`` that is used in several templates for csrf
protection (cross site request forgery).  So any template that already
uses this, is automatically loading our honeypot field.

For extra protection, you can add the page on which the form appears
to the ``EXTRA_PROTECTED_ACTIONS``.  This means that the ``Forbidden``
exception is also raised if the field is not submitted in the form at
all.  See the Configuration_ section.

The package has fixes for some standard Plone templates.  If you want
to use them, you need to explicitly enable them by loading
``fixes.zcml``.  In your buildout config::

  [instance]
  zcml =
      collective.honeypot-fixes

What does that do?

-  This registers overrides for several templates and scripts (using
``z3c.jbot``).

- It adds those templates and scripts to the list of extra protected
  actions.  This means that a post request to these actions now needs
  to have the honeypot field and it needs to be empty.


Configuration
=============

You can configure settings via environment variables in the
``zope.conf`` of your zope instance.  The usual way would be to do
this in ``buildout.cfg``::

  [instance]
  environment-vars =
      HONEYPOT_FIELD pooh
      EXTRA_PROTECTED_ACTIONS discussion_reply join_form sendto_form
      WHITELISTED_ACTIONS jq_reveal_email
      IGNORED_FORM_FIELDS secret_field

None of the options are required.

HONEYPOT_FIELD
    Name to use as input name of the honeypot field.  If you give no
    value here, no honeypot checks are done, so you only get some
    logging.  This is obviously not the main goal of this package, but
    it may be useful when you need to do some debugging.

EXTRA_PROTECTED_ACTIONS
    For these form actions the honeypot field is required: the field
    must be in the posted request, though it of course still needs to
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

IGNORED_FORM_FIELDS
    We log information about post requests, to allow a system admin to
    go through the log and discover posts that are obviously spam
    attempts but are not caught yet and need extra handling, perhaps
    an extra form that should get protection.  This information may
    contain form fields that should be left secret or that are not
    interesting.  No matter what you fill in here, we always ignore
    fields that contain the term `password`.


When are the checks *not* done?
===============================

This package ignores GET requests.  It only works on POST requests.

If you have made the HONEYPOT_FIELD configuration option empty, no
honeypot checks are done, so you only get some logging.

If Zope does any traversal, only the original action is checked.  For
example, a visitor makes a POST request to a ``my_form`` action.  The
honeypot checks are done for that action.  The ``my_form`` action may
be an old-style CMF form controller action that calls a validation
script ``validate_my_form``.  This validation script does not get
honeypot checks.  After validation, the action may do a traverse to a
script ``do_action`` that does the real work, like changing the
database or sending an email.  This script does not get honeypot
checks.

As an aside, if you have such a setup, you should make sure the
``do_action`` script calls a validation script too and only accepts
POST requests.  Otherwise a smart spammer can bypass the
``validate_my_form`` validation script by requesting the ``do_action``
script directly.  And he can bypass the honeypot checks by using a GET
request.


Future
======

We can probably make it easier to add this to a form based on
``z3c.form`` or ``zope.formlib``.  It should be possible to do some
hack to add the fields automatically to every form.  Having an extra
field should be okay, although it may trip up a few automated tests.


Compatibility
=============

This works on Plone 3 and Plone 4.  It does *not* work on Plone 2.5.


TODO
====


Plone 3:

- Check which of our Plone 4 fixes work on Plone 3 too.

- Protect discussion_reply.

- Protect join_form.
