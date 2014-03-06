from collective.honeypot import config

protected = [
    'sendto_form',
    'sendto',
    'contact-info',
    'send_feedback_site',
    'register',
    ]
# Explicitly add the actions that we protect.
config.EXTRA_PROTECTED_ACTIONS.update(protected)
