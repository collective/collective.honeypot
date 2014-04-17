import logging
from collective.honeypot import config

logger = logging.getLogger('collective.honeypot')
logger.info('Loading plone4 patches.')

protected = [
    'sendto_form',
    'sendto',
    'contact-info',
    'send_feedback_site',
    'register',
]
# Explicitly add the actions that we protect.
config.EXTRA_PROTECTED_ACTIONS.update(protected)
logger.info('Extra protected actions: %r', config.EXTRA_PROTECTED_ACTIONS)
