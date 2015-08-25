Changelog
=========


1.0.1 (2015-08-25)
------------------

- Require POST for ``send_feedback`` script.  This script can only be
  used by authenticated users, so there is little danger, but POST is
  still better.
  [maurits]


1.0 (2015-08-24)
----------------

- First official public release.

- Add kssValidateField to the default WHITELIST_ACTIONS to suppress kss inline
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

- Whitelist edit forms by default.
  [maurits]

- Log when we load patches and add extra protected actions.
  [maurits]


0.5 (2014-04-16)
----------------

- Support disallowing all posts.
  [maurits]

- Support checking start strings for white listed actions.
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
