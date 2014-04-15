import logging
from copy import deepcopy
from collective.honeypot.config import ACCEPTED_LOG_LEVEL
from collective.honeypot.config import DISALLOW_ALL_POSTS
from collective.honeypot.config import EXTRA_PROTECTED_ACTIONS
from collective.honeypot.config import HONEYPOT_FIELD
from collective.honeypot.config import IGNORED_FORM_FIELDS
from collective.honeypot.config import SPAMMER_LOG_LEVEL
from collective.honeypot.config import WHITELISTED_ACTIONS
from collective.honeypot.config import WHITELISTED_START
from zExceptions import Forbidden

logger = logging.getLogger('collective.honeypot')


def found_honeypot(form, required):
    """Did a spammer find a honeypot?

    We have two requirements:

    1. The honeypot field MUST be there if required is True.
    2. The honeypot field MUST be empty.

    Return True when one of these requirements is not met.
    """
    if not HONEYPOT_FIELD:
        # Apparently the user is only interested in logging the
        # requests, not in stopping spammers.
        return False
    if required and HONEYPOT_FIELD not in form:
        # Spammer did not submit required field.
        return 'misses required field'
    value = form.get(HONEYPOT_FIELD)
    if not value:
        # All tests are clear.
        return False
    # Spammer submitted forbidden field with non-empty value.
    # But: we could have made a mistake and put in the honeypot
    # field twice, which means it gets submitted as a list.
    if isinstance(value, list):
        value = ''.join(value)
        if not value:
            # All clear
            return False
    return 'has forbidden field'


def deny(msg=None):
    # Deny access.
    if msg is None:
        msg = ("Posting denied due to possible spamming. "
               "Please contact us if we are wrong.")
    raise Forbidden(msg)


def whitelisted(action):
    if action in WHITELISTED_ACTIONS:
        return True
    # Check action start strings.
    for white in WHITELISTED_START:
        if action.startswith(white):
            return True
    return False


def get_form(request):
    if hasattr(request, 'form'):
        form = request.form
    else:
        form = request
    # We may need to make a copy of the form.  This may be expensive
    # in memory, so we make sure to do this only once when needed.
    copied = False
    for field in IGNORED_FORM_FIELDS:
        if field not in form:
            continue
        if not copied:
            form = deepcopy(form)
            copied = True
        form.pop(field)
    # Remove all password fields.
    for field in form:
        if 'password' not in field:
            continue
        if not copied:
            form = deepcopy(form)
            copied = True
        form.pop(field)
    return form


def get_small_form(form):
    # Avoid printing large textareas or complete file uploads.
    small_form = {}
    for key, value in form.items():
        if not isinstance(value, basestring):
            small_form[key] = value
            continue
        if len(value) > 250:
            small_form[key] = value[:250] + '...'

    return small_form


def check_post(request):
    """Log a POST request.

    And possibly forbid access.

    Could be useful in case of a spam attack.
    """
    if request.get('REQUEST_METHOD', '').upper() != 'POST':
        return
    if DISALLOW_ALL_POSTS:
        logger.warn('All posts are disallowed.')
        # block the request:
        deny(msg='All posts are disallowed.')
    ip = request.get('HTTP_X_FORWARDED_FOR') or request.get('REMOTE_ADDR',
                                                            'unknown')
    referer = request.get('HTTP_REFERER', '')
    url = request.get('ACTUAL_URL', '')

    action = url.split('/')[-1]  # last part of url
    action = action.lstrip('@')

    if whitelisted(action):
        logger.debug("Action whitelisted: %s.", action)
        return
    form = get_form(request)
    if action in EXTRA_PROTECTED_ACTIONS:
        result = found_honeypot(form, required=True)
    else:
        result = found_honeypot(form, required=False)
    logger.debug("Checking honeypot fields for action %s. Result: %s.",
                 action, result)
    if not result:
        try:
            form = get_small_form(form)
        except:
            # Do not crash just because we want to log something.
            pass
        logger.log(ACCEPTED_LOG_LEVEL,
                   "ACCEPTED POST from ip %s, url %r, referer %r, with form "
                   "%r", ip, url, referer, form)
        return
    logger.log(SPAMMER_LOG_LEVEL,
               "SPAMMER caught in honeypot: %s.  ip %s, url %r",
               result, ip, url)
    # block the request:
    deny()
