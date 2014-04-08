from collective.honeypot import config

# Note: we cannot add 'discussion_reply_form' in this list, because a
# page will contain a simple form with this action and a single button
# 'Add Comment' to open the real form.  That initial form will not
# have our honeypot field.
protected = [
    'discussion_reply',
    ]
# Explicitly add the actions that we protect.
config.EXTRA_PROTECTED_ACTIONS.update(protected)