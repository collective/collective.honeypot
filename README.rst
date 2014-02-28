Introduction
============

This package gives honeypot protection for forms.


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

An idea that has found adoption is a honeypot: adding a field that
would never be filled in by a human.  The reasoning is that spammers
will likely fill in all fields in a form.  The bots that do their
spamming work do not know which fields are required, so they will
everything in, just to be sure.  Also, after a successful submission,
each field might be shown on the website, so they fill all fields to
get their message in the face of unsuspecting visitors.

The field should be hidden, so it does not distract humans.  Making
the input type hidden could mean spammers do not fill it in.  So we
should hide it with css.

Some spambots know a bit about Plone.  They know which fields are
enough to use some of the standard forms in a standard Plone website
without captchas.  If we add an invisible field they will simply not
use it.  So: we add a second invisible field and require that this
field is in the submitted form, although it may be empty.


Installation and usage
======================

Add ``collective.honeypot`` to the eggs of your zope instance in your
buildout config.  In Plone 3.2 or lower you need to add it to the zcml
option as well.  Run buildout and start the zope instance.

At this point it does not do anything yet.  You should take some
measures to make it protect forms.

In a form you want to protect, you must add this::

  <div tal:replace="structure context/@@honeypot_fields" />

And you must add the page on which it appears in
``config.PROTECTED_ACTIONS``.


Future
======

We can probably make it easier to add this to a form based on
``z3c.form``.  It should be possible to do some hack to add the fields
automatically to every form.  Having extra fields should be okay,
although it may trip up a few automated tests.


Compatibility
=============

I hope this works on Plone 2.5.
