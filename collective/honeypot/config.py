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
    'at_validate_field',
    'atct_edit',
    'edit',
    'kssValidateField',
    'jq_reveal_email',  # zest.emailhider
    'z3cform_validate_field',
))
logger.info('Whitelisted actions: %r', WHITELISTED_ACTIONS)
# Actions starting with these strings are not checked.  Note: regular
# expressions are too easily done wrong, so we do not support them.
WHITELISTED_START = get_multi('WHITELISTED_START', ())
logger.info('Whitelisted action start strings: %r', WHITELISTED_START)

# Fields that are not logged:
IGNORED_FORM_FIELDS = get_multi('IGNORED_FORM_FIELDS', ())
logger.info('Ignored form fields: %r', IGNORED_FORM_FIELDS)


def get_log_level(key, default):
    # Get one of the standard log levels or fall back to the default.
    value = os.environ.get(key, None)
    if value is None:
        return default
    value = value.upper()
    if value == 'DEBUG':
        return logging.DEBUG
    if value == 'INFO':
        return logging.INFO
    if value.startswith('WARN'):
        return logging.WARN
    if value == 'ERROR':
        return logging.ERROR
    if value == 'CRITICAL':
        return logging.CRITICAL
    # Default:
    return logging.INFO

# Log level for accepted posts.
ACCEPTED_LOG_LEVEL = get_log_level('ACCEPTED_LOG_LEVEL', logging.INFO)
logger.info('Accepted log level: %r', ACCEPTED_LOG_LEVEL)
# Log level for caught spammers.
SPAMMER_LOG_LEVEL = get_log_level('SPAMMER_LOG_LEVEL', logging.ERROR)
logger.info('Spammer log level: %r', SPAMMER_LOG_LEVEL)

# Disallow all posts, even whitelisted ones.
DISALLOW_ALL_POSTS = os.environ.get('DISALLOW_ALL_POSTS', '')
if DISALLOW_ALL_POSTS and DISALLOW_ALL_POSTS.lower() in \
        ['1', 'on', 'true', 'yes']:
    DISALLOW_ALL_POSTS = True
    logger.warn('DISALLOW_ALL_POSTS is true. All posts are disallowed!')
else:
    DISALLOW_ALL_POSTS = False
