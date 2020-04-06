from __future__ import print_function

from StringIO import StringIO

from Products.CMFCore.utils import getToolByName


def uninstall(self):
    out = StringIO()
    setup_tool = getToolByName(self, "portal_setup")
    profile = "profile-collective.honeypot:uninstall"
    setup_tool.runAllImportStepsFromProfile(profile)
    print("Imported uninstall profile.", file=out)
    return out.getvalue()
