# Field that MAY be in some requests, but MUST be empty.
HONEYPOT_FIELD = 'protected_1'
# Currently, these actions are protected, meaning: the forms have been
# changed to add the above field.  If you add actions here but do not
# change the forms, they become unusable for visitors, which is not
# what you want.
PROTECTED_ACTIONS = (
    'discussion_reply',
    'join_form',
    'sendto_form',
    )
# Actions that are not checked:
WHITELISTED_ACTIONS = (
    'jq_reveal_email',  # zest.emailhider
    )
# Fields that are not logged:
IGNORED_FORM_FIELDS = (
    'password',
    'password_confirm',
    '__ac_password',
    )
