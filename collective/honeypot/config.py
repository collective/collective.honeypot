import logging
import os

logger = logging.getLogger('collective.honeypot')


def get_multi(key, default):
    value = os.environ.get(key, None)
    if value is None:
        return set(default)
    value = value.strip().replace(',', ' ').replace('@', ' ')
    value = set(value.split())
    return value

# Field that MAY be in some requests, but MUST be empty.
HONEYPOT_FIELD = os.environ.get('HONEYPOT_FIELD', 'protected_1').strip()
logger.info('Honey pot field: %r', HONEYPOT_FIELD)

# Currently, these actions are extra protected by making the honeypot
# field required, though it of course still needs to be empty.  If you
# add actions here but do not change the forms, they become unusable
# for visitors, which is not what you want.  On the other hand, if you
# have a form that you no longer wish to use, you can add it here and
# it will stop functioning.
EXTRA_PROTECTED_ACTIONS = get_multi('EXTRA_PROTECTED_ACTIONS', ())
logger.info('Extra protected actions: %r', EXTRA_PROTECTED_ACTIONS)

# Actions that are not checked:
WHITELISTED_ACTIONS = get_multi('WHITELISTED_ACTIONS', (
    'jq_reveal_email',  # zest.emailhider
    'z3cform_validate_field',
    ))
logger.info('Whitelisted actions: %r', WHITELISTED_ACTIONS)

# Fields that are not logged:
IGNORED_FORM_FIELDS = get_multi('IGNORED_FORM_FIELDS', ())
logger.info('Ignored form fields: %r', IGNORED_FORM_FIELDS)
