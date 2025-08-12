# copyright 2003-2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact https://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of CubicWeb.
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <https://www.gnu.org/licenses/>.
"""some views to handle notification on data changes"""


from itertools import repeat
from inspect import getframeinfo, stack
import re

from logilab.common.registry import yes
from logilab.common.textutils import normalize_text

from cubicweb import _
from cubicweb.appobject import AppObject
from cubicweb.mail import construct_message_id, format_mail
from cubicweb.server.hook import SendMailOp
from cubicweb.server.session import Connection, InternalManager
from cubicweb.server import Service
from cubicweb.utils import format_and_escape_string, UStringIO


class RecipientsFinder(Service):
    """this component is responsible to find recipients of a notification

    by default user's with their email set are notified if any, else the default
    email addresses specified in the configuration are used
    """

    __regid__ = "recipients_finder"
    __select__ = yes()
    user_rql = (
        'Any X,E,A WHERE X is CWUser, X in_state S, S name "activated",'
        "X primary_email E, E address A"
    )

    def recipients(self):
        mode = self._cw.vreg.config["default-recipients-mode"]
        if mode == "users":
            execute = self._cw.execute
            dests = list(execute(self.user_rql, build_descr=True).entities())
        elif mode == "default-dest-addrs":
            lang = self._cw.vreg.property_value("ui.language")
            dests = zip(self._cw.vreg.config["default-dest-addrs"], repeat(lang))
        else:  # mode == 'none'
            dests = []
        return dests


# abstract or deactivated notification views and mixin ########################


class SkipEmail(Exception):
    """raise this if you decide to skip an email during its generation"""


class NotificationView(AppObject):
    """abstract view implementing the "email" API (eg to simplify sending
    notification)
    """

    # to be defined on concrete sub-classes

    __registry__ = "notification-views"
    content = None  # body of the mail
    message = None  # action verb of the subject
    msgid_timestamp = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def context(self, **kwargs):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        for key, val in kwargs.items():
            if val and isinstance(val, str) and val.strip():
                kwargs[key] = self._cw._(val)
        kwargs.update(
            {
                "user": self.user_data["login"],
                "eid": entity.eid,
                "etype": entity.dc_type(),
                "url": entity.absolute_url(),
                "title": entity.dc_long_title(),
            }
        )
        return kwargs

    def subject(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        subject = self._cw._(self.message)
        etype = entity.dc_type()
        eid = entity.eid
        login = self.user_data["login"]
        return self._cw._(f"{subject} {etype} #{eid} ({login})")

    # this is usually the method to call
    def render_and_send(self, **kwargs):
        """generate and send email messages for this view"""
        # render_emails changes self._cw so cache it here so all mails are sent
        # after we commit our transaction.
        cnx = self._cw
        for msg, recipients in self.render_emails(**kwargs):
            SendMailOp(cnx, recipients=recipients, msg=msg)

    def render_emails(self, **kwargs):
        """generate and send emails for this view (one per recipient)"""
        self._kwargs = kwargs
        recipients = self.recipients()
        if not recipients:
            self.info("skipping %s notification, no recipients", self.__regid__)
            return
        if self.cw_rset is not None:
            entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
            # if the view is using timestamp in message ids, no way to reference
            # previous email
            if not self.msgid_timestamp:
                refs = [
                    self.construct_message_id(eid)
                    for eid in entity.cw_adapt_to(
                        "INotifiable"
                    ).notification_references(self)
                ]
            else:
                refs = ()
            msgid = self.construct_message_id(entity.eid)
        else:
            refs = ()
            msgid = None
        req = self._cw
        self.user_data = req.user_data()
        for something in recipients:
            if isinstance(something, tuple):
                emailaddr, lang = something
                user = InternalManager(lang=lang)
            else:
                emailaddr = something.cw_adapt_to("IEmailable").get_email()
                user = something
            # hi-jack self._cw to get a session for the returned user
            with Connection(self._cw.repo, user) as cnx:
                self._cw = cnx
                try:
                    try:
                        # XXX forcing the row & col here may make the content and
                        #     subject inconsistent because subject will depend on
                        #     self.cw_row & self.cw_col if they are set.
                        content = self.render(**kwargs)
                        subject = self.subject()
                    except SkipEmail:
                        continue
                    except Exception as ex:
                        # shouldn't make the whole transaction fail because of rendering
                        # error (unauthorized or such) XXX check it doesn't actually
                        # occurs due to rollback on such error
                        self.exception(str(ex))
                        continue
                    msg = format_mail(
                        self.user_data,
                        [emailaddr],
                        content,
                        subject,
                        config=self._cw.vreg.config,
                        msgid=msgid,
                        references=refs,
                    )
                    yield msg, [emailaddr]
                finally:
                    self._cw = req

    # recipients handling ######################################################

    def recipients(self):
        """return a list of either 2-uple (email, language) or user entity to
        whom this email should be sent
        """
        finder = self._cw.vreg["services"].select(
            "recipients_finder",
            self._cw,
            rset=self.cw_rset,
            row=self.cw_row or 0,
            col=self.cw_col or 0,
        )
        return finder.recipients()

    # email generation helpers #################################################

    def construct_message_id(self, eid):
        return construct_message_id(
            self._cw.vreg.config.appid, eid, self.msgid_timestamp
        )

    def w(self, text, *args, escape=True):
        if self._w is None:
            raise Exception(f"Error: call to {self}.w before it has been set")

        if self.debug_html_rendering:
            caller = getframeinfo(stack()[1][0])
            if isinstance(text, str) and re.match(r"^ *<[a-zA-Z0-9]+( .*>|>)", text):
                to_add = (
                    'cubicweb-generated-by="%s.%s" cubicweb-from-source="%s:%s"'
                    % (
                        self.__module__,
                        self.__class__.__name__,
                        caller.filename,
                        caller.lineno,
                    )
                )

                before_space, beginning_of_html = text.split("<", 1)

                # when it's a tag without attribues like "<b>"
                if re.match(r"^ *<[a-zA-Z0-9]+>", text):
                    tag_name, rest = beginning_of_html.split(">", 1)
                    rest = ">" + rest
                else:
                    tag_name, rest = beginning_of_html.split(" ", 1)
                    rest = " " + rest
                text = f"{before_space}<{tag_name} {to_add}{rest}"

        text = format_and_escape_string(text, *args, escape=escape)

        return self._w(text)

    # main view interface #####################################################

    def render(self, **context):
        """called to render a view object for a result set.

        This method is a dispatched to an actual method selected
        according to optional row and col parameters, which are locating
        a particular row or cell in the result set:

        """
        stream = UStringIO()
        try:
            stream.write(
                format_and_escape_string(
                    self._cw._(self.content), (self.context(**context))
                )
            )
        except Exception:
            self.debug("view call %s failed (context=%s)", self.call, context)
            raise
        return stream.getvalue()


class StatusChangeMixIn:
    __regid__ = "notif_status_change"
    msgid_timestamp = True
    message = _("status changed")
    content = _(
        """
%(user)s changed status from <%(previous_state)s> to <%(current_state)s> for entity
'%(title)s'

%(comment)s

url: %(url)s
"""
    )


###############################################################################
# Actual notification views.                                                  #
#                                                                             #
# disable them at the recipients_finder level if you don't want them          #
###############################################################################

# XXX should be based on dc_title/dc_description, no?


class ContentAddedView(NotificationView):
    """abstract class for notification on entity/relation

    all you have to do by default is :
    * set id and __select__ attributes to match desired events and entity types
    * set a content attribute to define the content of the email (unless you
      override call)
    """

    __abstract__ = True
    __regid__ = "notif_after_add_entity"
    msgid_timestamp = False
    message = _("new")
    content = """
%(title)s

%(content)s

url: %(url)s
"""
    # to be defined on concrete sub-classes
    content_attr = None

    def context(self, **kwargs):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        content = entity.printable_value(self.content_attr, format="text/plain")
        if content:
            contentformat = getattr(entity, self.content_attr + "_format", "text/rest")
            # XXX don't try to wrap rest until we've a proper transformation (see
            # #103822)
            if contentformat != "text/rest":
                content = normalize_text(content, 80)
        return super().context(content=content, **kwargs)

    def subject(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return "{} #{} ({})".format(
            self._cw.__(f"New {entity.e_schema}"),
            entity.eid,
            self.user_data["login"],
        )


def format_value(value):
    if isinstance(value, str):
        return f'"{value}"'
    return value


class EntityUpdatedNotificationView(NotificationView):
    """abstract class for notification on entity/relation

    all you have to do by default is :
    * set id and __select__ attributes to match desired events and entity types
    * set a content attribute to define the content of the email (unless you
      override call)
    """

    __abstract__ = True
    __regid__ = "notif_entity_updated"
    msgid_timestamp = True
    message = _("updated")
    no_detailed_change_attrs = ()
    content = """
Properties have been updated by %(user)s:

%(changes)s

url: %(url)s
"""

    def context(self, changes=(), **kwargs):
        context = super().context(**kwargs)
        _ = self._cw._
        formatted_changes = []
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        for attr, oldvalue, newvalue in sorted(changes):
            # check current user has permission to see the attribute
            rschema = self._cw.vreg.schema[attr]
            if rschema.final:
                rdef = entity.e_schema.relation_definition(rschema)
                if not rdef.has_perm(self._cw, "read", eid=self.cw_rset[0][0]):
                    continue
            # XXX suppose it's a subject relation...
            elif not rschema.has_perm(self._cw, "read", fromeid=self.cw_rset[0][0]):
                continue
            if attr in self.no_detailed_change_attrs:
                msg = _("%s updated") % _(attr)
            elif oldvalue not in (None, ""):
                msg = _("%(attr)s updated from %(oldvalue)s to %(newvalue)s") % {
                    "attr": _(attr),
                    "oldvalue": format_value(oldvalue),
                    "newvalue": format_value(newvalue),
                }
            else:
                msg = _("%(attr)s set to %(newvalue)s") % {
                    "attr": _(attr),
                    "newvalue": format_value(newvalue),
                }
            formatted_changes.append("* " + msg)
        if not formatted_changes:
            # current user isn't allowed to see changes, skip this notification
            raise SkipEmail()
        context["changes"] = "\n".join(formatted_changes)
        return context

    def subject(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return "{} #{} ({})".format(
            self._cw.__(f"Updated {entity.e_schema}"),
            entity.eid,
            self.user_data["login"],
        )
