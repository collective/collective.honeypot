## Script (Python) "discussion_reply"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=subject,body_text,text_format='plain',username=None,password=None
##title=Reply to content

from Products.PythonScripts.standard import url_quote_plus
from Products.CMFCore.utils import getToolByName
from quintagroup.plonecomments.utils import manage_mails
from Products.CMFPlone import MessageFactory
from Products.CMFPlone import PloneMessageFactory
_ = MessageFactory("quintagroup.plonecomments")

mtool = getToolByName(context, 'portal_membership')
dtool = getToolByName(context, 'portal_discussion')

req = context.REQUEST
pp = getToolByName(context,'portal_properties')
# Get properties
isForAnonymous = pp['qPloneComments'].getProperty('enable_anonymous_commenting', False)
ifModerate = pp['qPloneComments'].getProperty('enable_moderation', False)
requireEmail = pp['qPloneComments'].getProperty('require_email', False)
if username or password:
    # The user username/password inputs on on the comment form were used,
    # which might happen when anonymous commenting is enabled. If they typed
    # something in to either of the inputs, we send them to 'logged_in'.
    # 'logged_in' will redirect them back to this script if authentication
    # succeeds with a query string which will post the message appropriately
    # and show them the result.  if 'logged_in' fails, the user will be
    # presented with the stock login failure page.  This all depends
    # heavily on cookiecrumbler, but I believe that is a Plone requirement.
    came_from = '%s?subject=%s&amp;body_text=%s' % (req['URL'], subject, body_text)
    came_from = url_quote_plus(came_from)
    portal_url = context.portal_url()

    return req.RESPONSE.redirect(
        '%s/logged_in?__ac_name=%s'
        '&amp;__ac_password=%s'
        '&amp;came_from=%s' % (portal_url,
                               url_quote_plus(username),
                               url_quote_plus(password),
                               came_from,
                               )
        )

# if (the user is already logged in) or (if anonymous commenting is enabled and
# they posted without typing a username or password into the form), we do
# the following

#########################################################
# Get discussion item (reply) author and creating reply #
comment_creator = req.get('Creator', None)
if isForAnonymous and comment_creator:
    # Get entered anonymous name
    comment_creator = comment_creator
else:
    member = mtool.getAuthenticatedMember()
    comment_creator = member.getUserName()
tb = dtool.getDiscussionFor(context)
if requireEmail:
    if mtool.isAnonymousUser():
        email = req.get('email', '')
    else:
        email = mtool.getAuthenticatedMember().getProperty('email')

    id = tb.createReply(title=subject, text=body_text, Creator=comment_creator, email=email)
else:
    id = tb.createReply(title=subject, text=body_text, Creator=comment_creator)

reply = tb.getReply(id)

# TODO THIS NEEDS TO GO AWAY!
if hasattr(dtool.aq_explicit, 'cookReply'):
    dtool.cookReply(reply, text_format='plain')

parent = tb.aq_parent
# Send notification e-mail

manage_mails(reply, context, 'aproving')
if not ifModerate:
    manage_mails(reply, context, 'publishing')

# return to the discussable object.
redirect_target = context.plone_utils.getDiscussionThread(tb)[0]
view = redirect_target.getTypeInfo().getActionInfo('object/view',
                                                   redirect_target)['url']
anchor = reply.getId()

# Inform user about awaiting moderation
portal_status_message=_(u'Comment published.')
if ifModerate and reply:
    portal_status_message=_(u'Currently, all comments require approval before being published. Please check back later.')

from Products.CMFPlone.utils import transaction_note
transaction_note('Added comment to %s at %s' % (parent.title_or_id(),
                                                reply.absolute_url()))

context.plone_utils.addPortalMessage(portal_status_message)
context.plone_utils.addPortalMessage(PloneMessageFactory(u'Comment added.'))

target = '%s#%s' % (view, anchor)
return req.RESPONSE.redirect(target)
