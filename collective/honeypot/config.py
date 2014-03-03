# Field that MAY be in some requests, but MUST be empty.
HONEYPOT_FIELD = 'protected_1'
# Currently, these actions are extra protected by making the honeypot
# field required, though it of course still needs to be empty.  If you
# add actions here but do not change the forms, they become unusable
# for visitors, which is not what you want.  On the other hand, if you
# have a form that you no longer wish to use, you can add it here and
# it will stop functioning.
PROTECTED_ACTIONS = (
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
