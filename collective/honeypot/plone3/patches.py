import logging

from AccessControl import allow_class
from collective.honeypot import config
from zExceptions import Forbidden

logger = logging.getLogger('collective.honeypot')
logger.info('Loading plone3 patches.')

# In Plone 4, you are allowed to import Forbidden in a python skin
# script.  In Plone 3 apparently not.  We do want it, so we explicitly
# allow it here.
allow_class(Forbidden)
logger.info('Allowing script access to zExceptions.Forbidden.')

protected = [
     'sendto_form',
     'sendto',
     'contact-info',
     'send_feedback_site',
     'register',
     'join_form',
     ]
# Explicitly add the actions that we protect.
config.EXTRA_PROTECTED_ACTIONS.update(protected)
logger.info('Extra protected actions: %r', config.EXTRA_PROTECTED_ACTIONS)
