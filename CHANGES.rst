Changelog
=========

4.0.0 (2025-06-05)
------------------

- Drop support for Plone 5.2 and Python 3.8.  [maurits]

- Change the default ``ACCEPTED_LOG_LEVEL`` to DEBUG. [davisagli]


3.0.0 (2024-06-18)
------------------

- Replace "WHITELISTED" by "ALLOWLISTED" in all environment variables.
  The old spelling is still checked as well for backwards compatibility.
  Fixes `issue 20 <https://github.com/collective/collective.honeypot/issues/20>`_.
  [maurits]

- Drop support for Python older than 3.8.  [maurits]

- Add Plone 6.0 and 6.1 override for ``plone.app.z3cform.templates.macros.pt``.
  [szakitibi, maurits]


2.1.1 (unreleased)
------------------

- Add Spanish translations.
  [macagua]


2.1 (2022-11-04)
----------------

- Add support for restapi POST.
  [cekk]

- Support Plone 5.2 on Py 2.7+3.7+3.8 and Plone 6.0 on Py 3.8+3.9+3.10.  [maurits]

- Test on GitHub Actions instead of Travis.  [maurits]


2.0 (2021-01-27)
----------------

- Automatically load the fixes if package is loaded. No need to explicitly include the ``fixes.zcml`` anymore.
  [thet]

- Secure collective.easyform with honeypot if available.
  [thet]

- Add a generic z3c.form honeypot extender module which can be configured via ZCML only and configure plone.app.discussion to use it.
  [thet]

- Add a dummy widget display view which renders empty - form renderings may expect it.
  [thet]

- Add data converter for z3c.form validation to not fail when multiple HoneyPot fields were injected.
  [thet]

- Update for support of Plone 5.2 and Python 3. Remove support for Plone 3 and 4.
  [thet, reinhardt]


1.0.3 (2020-04-08)
------------------

- Fix adapter registration conflict.
  [rodfersou]


1.0.2 (2015-10-01)
------------------

- Split honeypot_field and authenticator view.  When
  `@@authenticator`` is called, return the view without rendering it.
  Fixes AttributeError: 'unicode' object has no attribute 'token', for
  example on PloneFormGen quickedit form.
  [maurits]

- Added Travis badge to readme.
  [maurits]


1.0.1 (2015-08-25)
------------------

- Require POST for ``send_feedback`` script.  This script can only be
  used by authenticated users, so there is little danger, but POST is
  still better.
  [maurits]


1.0 (2015-08-24)
----------------

- First official public release.

- Add kssValidateField to the default ALLOWLISTED_ACTIONS to suppress kss inline
  validation being logged on Plone <= 4.2 .
  [fredvd]


0.7 (2014-04-18)
----------------

- Add GenericSetup profile, which adds skin layers with our fixes.
  This is recommended on Plone 3.  The reason is that this technique
  does not need ``z3c.jbot``, which can have a few ugly side effects
  in Plone 3: ``Products.CacheSetup`` does not like it and in other
  cases Zope does not even start up.
  [maurits]


0.6 (2014-04-17)
----------------

- Allow edit forms by default.
  [maurits]

- Log when we load patches and add extra protected actions.
  [maurits]


0.5 (2014-04-16)
----------------

- Support disallowing all posts.
  [maurits]

- Support checking start strings for allowed actions.
  [maurits]

- Allow configuring log levels.
  [maurits]

- Print less when logging the form.
  [maurits]


0.4 (2014-04-15)
----------------

- Add fixes for ``quintagroup.plonecomments``.
  [maurits]

- Add fixes for Plone 3.
  [maurits]


0.3 (2014-03-14)
----------------

- Remove ``z3c.jbot`` from the default dependencies so the
  last change actually works.
  [maurits]


0.2 (2014-03-14)
----------------

- Make ``z3c.jbot`` an extra dependency of ``collective.honeypot[fixes]``.
  This way, you only get ``z3c.jbot`` when you need it.
  [maurits]


0.1 (2014-03-14)
----------------

- Initial release.
  [maurits]
