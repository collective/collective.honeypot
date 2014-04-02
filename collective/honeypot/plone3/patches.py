# In Plone 4, you are allowed to import Forbidden in a python skin
# script.  In Plone 3 apparently not.  We do want it, so we explicitly
# allow it here.
from AccessControl import allow_class
from zExceptions import Forbidden
allow_class(Forbidden)

from collective.honeypot import config

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
