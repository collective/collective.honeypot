import logging
from collective.honeypot.config import FORBIDDEN_HONEYPOT_FIELD
from collective.honeypot.config import PROTECTED_ACTIONS
from collective.honeypot.config import WHITELISTED_ACTIONS
from collective.honeypot.config import REQUIRED_HONEYPOT_FIELD
from zExceptions import Forbidden

logger = logging.getLogger('collective.honeypot')


def found_honeypot(form):
    """Did a spammer find a honeypot?

    We have two requirements:

    1. The required field MUST be there, but MAY be empty.
    2. The forbidden field MAY be there, but MUST be empty.

    Return True when one of these requirements is not met.
    """
    # The required field does not need to have a value, it just needs
    # to be in the form.
    if not REQUIRED_HONEYPOT_FIELD in form:
        # Spammer did not submit required field.
        return 'misses required field'
    if form.get(FORBIDDEN_HONEYPOT_FIELD, False):
        # Spammer submitted forbidden field with non-empty value.
        return 'has forbidden field'
    # All tests are clear.
    return False


def deny():
    # Deny access.
    raise Forbidden("Posting denied due to possible spamming. "
                    "Please contact us if we are wrong.")


def logpost(request):
    """Log a POST request.

    And possibly forbid access.

    Could be useful in case of a spam attack.
    """
    if request.get('REQUEST_METHOD', '').upper() != 'POST':
        return
    if hasattr(request, 'form'):
        form = request.form
    else:
        form = request
    ip = request.get('HTTP_X_FORWARDED_FOR') or request.get('REMOTE_ADDR',
                                                            'unknown')
    referer = request.get('HTTP_REFERER', '')
    url = request.get('ACTUAL_URL', '')
    user = request.get('AUTHENTICATED_USER', '')

    action = url.split('/')[-1]  # last part of url
    action = action.lstrip('@')
    if action in WHITELISTED_ACTIONS:
        logger.info("Action whitelisted: %s.", action)
        return
    if action not in PROTECTED_ACTIONS:
        return
    result = found_honeypot(form)
    logger.info("Checking honeypot fields for action %s. Result: %s.",
                action, result)
    if not result:
        logger.info("POST from ip %s, user %r, url %r, referer %r, with form "
                    "%r", ip, user, url, referer, form)
        return
    logger.warn("SPAMMER caught in honeypot: %s. ip %s, user %r, "
                "url %r, referer %r, with form %r",
                result, ip, user, url, referer, form)
    # block the request:
    deny()


if __name__ == '__main__':
    # Quick test for honeypot checker.
    # 1. The required field MUST be there, but MAY be empty.
    # 2. The forbidden field MAY be there, but MUST be empty.
    assert found_honeypot({}) == 'misses required field'
    assert found_honeypot(
        {REQUIRED_HONEYPOT_FIELD: ''}) is False
    assert found_honeypot(
        {FORBIDDEN_HONEYPOT_FIELD: ''}) == 'misses required field'
    assert found_honeypot(
        {REQUIRED_HONEYPOT_FIELD: 'hello'}) is False
    assert found_honeypot(
        {REQUIRED_HONEYPOT_FIELD: '',
         FORBIDDEN_HONEYPOT_FIELD: ''}) is False
    assert found_honeypot(
        {REQUIRED_HONEYPOT_FIELD: '',
         FORBIDDEN_HONEYPOT_FIELD: 'hello'}) == 'has forbidden field'
    assert found_honeypot(
        {REQUIRED_HONEYPOT_FIELD: 'hello',
         FORBIDDEN_HONEYPOT_FIELD: 'hello'}) == 'has forbidden field'
