from collective.honeypot.utils import check_post


def pre_traverse_check(object, event):
    """Do a pre traverse check.

    We do this to log any POST requests and possibly forbid access.
    We are mostly interested in POSTs that try to add comments and
    catch spammers.
    """
    check_post(event.request)
