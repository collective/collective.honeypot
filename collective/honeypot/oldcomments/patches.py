import logging
from collective.honeypot import config

logger = logging.getLogger('collective.honeypot')
logger.info('Loading oldcomments patches.')

# Note: we cannot add 'discussion_reply_form' in this list, because a
# page will contain a simple form with this action and a single button
# 'Add Comment' to open the real form.  That initial form will not
# have our honeypot field.
protected = [
    'discussion_reply',
]
# Explicitly add the actions that we protect.
config.EXTRA_PROTECTED_ACTIONS.update(protected)
logger.info('Extra protected actions: %r', config.EXTRA_PROTECTED_ACTIONS)
