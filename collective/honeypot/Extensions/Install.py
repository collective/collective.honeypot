from Products.CMFCore.utils import getToolByName
from StringIO import StringIO


def uninstall(self):
    out = StringIO()
    setup_tool = getToolByName(self, 'portal_setup')
    profile = 'profile-collective.honeypot:uninstall'
    setup_tool.runAllImportStepsFromProfile(profile)
    print >> out, "Imported uninstall profile."
    return out.getvalue()
