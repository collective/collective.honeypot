import logging
from copy import deepcopy
from collective.honeypot.config import HONEYPOT_FIELD
from collective.honeypot.config import IGNORED_FORM_FIELDS
from collective.honeypot.config import EXTRA_PROTECTED_ACTIONS
from collective.honeypot.config import WHITELISTED_ACTIONS
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
    if form.get(HONEYPOT_FIELD):
        # Spammer submitted forbidden field with non-empty value.
        return 'has forbidden field'
    # All tests are clear.
    return False


def deny():
    # Deny access.
    raise Forbidden("Posting denied due to possible spamming. "
                    "Please contact us if we are wrong.")


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


def check_post(request):
    """Log a POST request.

    And possibly forbid access.

    Could be useful in case of a spam attack.
    """
    if request.get('REQUEST_METHOD', '').upper() != 'POST':
        return
    ip = request.get('HTTP_X_FORWARDED_FOR') or request.get('REMOTE_ADDR',
                                                            'unknown')
    referer = request.get('HTTP_REFERER', '')
    url = request.get('ACTUAL_URL', '')

    action = url.split('/')[-1]  # last part of url
    action = action.lstrip('@')
    if action in WHITELISTED_ACTIONS:
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
        logger.info("ACCEPTED POST from ip %s, url %r, referer %r, with form "
                    "%r", ip, url, referer, form)
        return
    logger.warn("SPAMMER caught in honeypot: %s.  ip %s, url %r",
                result, ip, url)
    # block the request:
    deny()
