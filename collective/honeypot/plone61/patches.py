from collective.honeypot import logger, config

logger.info("Loading plone61 patches.")

protected = [
    "sendto_form",
    "sendto",
    "contact-info",
    "send_feedback_site",
    "register",
]
# Explicitly add the actions that we protect.
config.EXTRA_PROTECTED_ACTIONS.update(protected)
logger.info("Extra protected actions: %r", config.EXTRA_PROTECTED_ACTIONS)
