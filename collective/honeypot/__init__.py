import sys

# If we are using Python less than 2.5, it means we are using Plone 3.
if sys.version_info < (2, 5):
    # In Plone 4, you are allowed to import 'Forbidden' in a Python
    # skin script.  In Plone 3 apparently not.  We do want it, so we
    # explicitly allow it here.
    import logging
    from AccessControl import allow_class
    from zExceptions import Forbidden
    logger = logging.getLogger('collective.honeypot')
    allow_class(Forbidden)
    logger.info('Allowing script access to zExceptions.Forbidden.')
