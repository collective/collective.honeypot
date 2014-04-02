# In Plone 4, you are allowed to import Forbidden in a python skin
# script.  In Plone 3 apparently not.  We do want it, so we explicitly
# allow it here.
from AccessControl import allow_class
from zExceptions import Forbidden
allow_class(Forbidden)
