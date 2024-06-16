from collective.honeypot import _
from collective.honeypot.config import ACCEPTED_LOG_LEVEL
from collective.honeypot.config import DISALLOW_ALL_POSTS
from collective.honeypot.config import EXTRA_PROTECTED_ACTIONS
from collective.honeypot.config import HONEYPOT_FIELD
from collective.honeypot.config import IGNORED_FORM_FIELDS
from collective.honeypot.config import SPAMMER_LOG_LEVEL
from collective.honeypot.config import ALLOWLISTED_ACTIONS
from collective.honeypot.config import ALLOWLISTED_START
from copy import deepcopy
from zExceptions import Forbidden
from zope.globalrequest import getRequest
from zope.i18n import translate

try:
    from plone.restapi.deserializer import json_body
except ImportError:
    json_body = None

import logging
import six


logger = logging.getLogger("collective.honeypot")


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
        return "misses required field"
    value = form.get(HONEYPOT_FIELD)
    if not value:
        # All tests are clear.
        return False
    # Spammer submitted forbidden field with non-empty value.
    # But: we could have made a mistake and put in the honeypot
    # field twice, which means it gets submitted as a list.
    if isinstance(value, list):
        value = "".join(value)
        if not value:
            # All clear
            return False
    return "has forbidden field"


def deny(msg=None):
    # Deny access.
    if msg is None:
        msg = translate(
            _(
                "post_denied_label",
                default="Posting denied due to possible spamming. "
                "Please contact us if we are wrong.",
            ),
            context=getRequest(),
        )
    raise Forbidden(msg)


def allowlisted(action):
    if action in ALLOWLISTED_ACTIONS:
        return True
    # Check action start strings.
    for allow in ALLOWLISTED_START:
        if action.startswith(allow):
            return True
    return False


def get_form(request):
    form = getattr(request, "form", {})
    if (
        not form
        and getattr(request, "CONTENT_TYPE", "") == "application/json"
        and json_body
    ):
        # restapi post
        form = json_body(request)
    if not form and isinstance(request, dict):
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
        if "password" not in field:
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
        if not isinstance(value, six.string_types):
            small_form[key] = value
            continue
        if len(value) > 250:
            small_form[key] = value[:250] + "..."

    return small_form


def check_post(request):
    """Log a POST request.

    And possibly forbid access.

    Could be useful in case of a spam attack.
    """
    if request.get("REQUEST_METHOD", "").upper() != "POST":
        return
    if DISALLOW_ALL_POSTS:
        logger.warn("All posts are disallowed.")
        # block the request:
        deny(msg="All posts are disallowed.")
    ip = request.get("HTTP_X_FORWARDED_FOR") or request.get("REMOTE_ADDR", "unknown")
    referer = request.get("HTTP_REFERER", "")
    url = request.get("ACTUAL_URL", "")

    action = url.split("/")[-1]  # last part of url
    action = action.lstrip("@")

    if allowlisted(action):
        logger.debug("Action allowlisted: %s.", action)
        return
    form = get_form(request)
    if action in EXTRA_PROTECTED_ACTIONS:
        result = found_honeypot(form, required=True)
    else:
        result = found_honeypot(form, required=False)
    logger.debug("Checking honeypot fields for action %s. Result: %s.", action, result)
    if not result:
        try:
            form = get_small_form(form)
        except Exception:
            # Do not crash just because we want to log something.
            pass
        logger.log(
            ACCEPTED_LOG_LEVEL,
            "ACCEPTED POST from ip %s, url %r, referer %r, with form " "%r",
            ip,
            url,
            referer,
            form,
        )
        return
    logger.log(
        SPAMMER_LOG_LEVEL,
        "SPAMMER caught in honeypot: %s.  ip %s, url %r",
        result,
        ip,
        url,
    )
    # block the request:
    deny()
