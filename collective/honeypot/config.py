# Field that MAY be in some requests, but MUST be empty.
FORBIDDEN_HONEYPOT_FIELD = 'protected_1'
# Field that MUST be in some requests, but MAY be empty.  This is to
# catch spammers that know how to post to Plone without loading the
# form first, in which case they will never have the forbidden field
# so that check will fail us.
REQUIRED_HONEYPOT_FIELD = 'protected_2'
# Currently, these actions are protected, meaning: the forms have been
# changed to add the above fields.  If you add actions here but do not
# change the forms, they become unusable for visitors, which is not
# what you want.
PROTECTED_ACTIONS = (
    'discussion_reply',
    'join_form',
    'sendto_form',
    )
