from collective.honeypot import config

protected = [
    'discussion_reply',
    'discussion_reply_form',
    ]
# Explicitly add the actions that we protect.
config.EXTRA_PROTECTED_ACTIONS.update(protected)
