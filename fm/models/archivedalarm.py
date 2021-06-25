# ---------------------------------------------------------------------
# ArchivedAlarm model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
from django.template import Template, Context
from mongoengine.document import Document
from mongoengine.fields import (
    StringField,
    DateTimeField,
    ListField,
    EmbeddedDocumentField,
    IntField,
    LongField,
    ObjectIdField,
    DictField,
)

# NOC modules
from noc.config import config
from noc.core.mongo.fields import ForeignKeyField, PlainReferenceField
from noc.sa.models.managedobject import ManagedObject
from noc.core.datastream.decorator import datastream
from noc.sa.models.servicesummary import SummaryItem, ObjectSummaryItem
from noc.core.span import get_current_span
from noc.core.fm.enum import RCA_NONE
from .alarmclass import AlarmClass
from .alarmlog import AlarmLog
from .alarmseverity import AlarmSeverity


@datastream
class ArchivedAlarm(Document):
    meta = {
        "collection": "noc.alarms.archived",
        "strict": False,
        "auto_create_index": False,
        "indexes": [
            "root",
            "timestamp",
            "managed_object",
            ("managed_object", "discriminator", "control_time"),
            "escalation_tt",
            "escalation_ts",
        ],
    }
    status = "C"

    timestamp = DateTimeField(required=True)
    clear_timestamp = DateTimeField(required=True)
    managed_object = ForeignKeyField(ManagedObject)
    alarm_class = PlainReferenceField(AlarmClass)
    severity = IntField(required=True)
    vars = DictField()
    log = ListField(EmbeddedDocumentField(AlarmLog))
    #
    opening_event = ObjectIdField(required=False)
    closing_event = ObjectIdField(required=False)
    # Number of reopens
    reopens = IntField(required=False)
    # Copied discriminator
    discriminator = StringField(required=False)
    # Manual acknowledgement timestamp
    ack_ts = DateTimeField(required=False)
    # Manual acknowledgement user name
    ack_user = StringField(required=False)
    # Control time within alarm will be reopen instead
    # instead of creating the new alarm
    control_time = DateTimeField(required=False)
    # RCA
    # Reference to root cause (Active Alarm or Archived Alarm instance)
    root = ObjectIdField(required=False)
    # Escalated TT ID in form
    # <external system name>:<external tt id>
    escalation_ts = DateTimeField(required=False)
    escalation_tt = StringField(required=False)
    escalation_error = StringField(required=False)
    escalation_ctx = LongField(required=False)
    escalation_close_ts = DateTimeField(required=False)
    escalation_close_error = StringField(required=False)
    escalation_close_ctx = LongField(required=False)
    # Directly affected services summary, grouped by profiles
    # (connected to the same managed object)
    direct_services = ListField(EmbeddedDocumentField(SummaryItem))
    direct_subscribers = ListField(EmbeddedDocumentField(SummaryItem))
    # Indirectly affected services summary, groupped by profiles
    # (covered by this and all inferred alarms)
    total_objects = ListField(EmbeddedDocumentField(ObjectSummaryItem))
    total_services = ListField(EmbeddedDocumentField(SummaryItem))
    total_subscribers = ListField(EmbeddedDocumentField(SummaryItem))
    # Paths
    adm_path = ListField(IntField())
    segment_path = ListField(ObjectIdField())
    container_path = ListField(ObjectIdField())
    # Uplinks, for topology_rca only
    uplinks = ListField(IntField())
    # RCA neighbor cache, for topology_rca only
    rca_neighbors = ListField(IntField())
    # RCA_* enums
    rca_type = IntField(default=RCA_NONE)
    # labels
    labels = ListField(StringField())
    effective_labels = ListField(StringField())

    def __str__(self):
        return "%s" % self.id

    def iter_changed_datastream(self, changed_fields=None):
        if config.datastream.enable_alarm:
            yield "alarm", str(self.id)

    def log_message(self, message, source=None):
        self.log += [
            AlarmLog(
                timestamp=datetime.datetime.now(),
                from_status=self.status,
                to_status=self.status,
                message=message,
                source=source,
            )
        ]
        self.save()

    def get_template_vars(self):
        """
        Prepare template variables
        """
        vars = self.vars.copy()
        vars.update({"alarm": self})
        return vars

    @property
    def subject(self):
        ctx = Context(self.get_template_vars())
        s = Template(self.alarm_class.subject_template).render(ctx)
        if len(s) >= 255:
            s = s[:125] + " ... " + s[-125:]
        return s

    @property
    def body(self):
        ctx = Context(self.get_template_vars())
        s = Template(self.alarm_class.body_template).render(ctx)
        return s

    @property
    def duration(self):
        dt = self.clear_timestamp - self.timestamp
        return dt.days * 86400 + dt.seconds

    @property
    def display_duration(self):
        duration = self.clear_timestamp - self.timestamp
        secs = duration.seconds % 60
        mins = (duration.seconds / 60) % 60
        hours = (duration.seconds / 3600) % 24
        days = duration.days
        if days:
            return "%dd %02d:%02d:%02d" % (days, hours, mins, secs)
        else:
            return "%02d:%02d:%02d" % (hours, mins, secs)

    @property
    def effective_style(self):
        return AlarmSeverity.get_severity(self.severity).style

    def set_root(self, root_alarm):
        pass

    def reopen(self, message):
        """
        Reopen alarm back
        """
        reopens = self.reopens or 0
        ts = datetime.datetime.now()
        log = self.log + [AlarmLog(timestamp=ts, from_status="C", to_status="A", message=message)]
        a = ActiveAlarm(
            id=self.id,
            timestamp=self.timestamp,
            last_update=ts,
            managed_object=self.managed_object,
            alarm_class=self.alarm_class,
            severity=self.severity,
            vars=self.vars,
            log=log,
            root=self.root,
            escalation_ts=self.escalation_ts,
            escalation_tt=self.escalation_tt,
            escalation_error=self.escalation_error,
            escalation_ctx=self.escalation_ctx,
            opening_event=self.opening_event,
            discriminator=self.discriminator,
            reopens=reopens + 1,
            direct_services=self.direct_services,
            direct_subscribers=self.direct_subscribers,
            total_objects=self.total_objects,
            total_services=self.total_services,
            total_subscribers=self.total_subscribers,
            adm_path=self.adm_path,
            segment_path=self.segment_path,
            container_path=self.container_path,
            uplinks=self.uplinks,
        )
        a.save()
        # @todo: Clear related correlator jobs
        self.delete()
        # Send notifications
        # Do not set notifications for child and for previously reopened
        # alarms
        if not a.root and not reopens:
            a.managed_object.event(
                a.managed_object.EV_ALARM_REOPENED,
                {
                    "alarm": a,
                    "subject": a.subject,
                    "body": a.body,
                    "symptoms": a.alarm_class.symptoms,
                    "recommended_actions": a.alarm_class.recommended_actions,
                    "probable_causes": a.alarm_class.probable_causes,
                },
            )
        return a

    def iter_consequences(self):
        """
        Generator yielding all consequences alarm
        """
        for a in ArchivedAlarm.objects.filter(root=self.id):
            yield a
            yield from a.iter_consequences()

    def iter_affected(self):
        """
        Generator yielding all affected managed objects
        """
        seen = {self.managed_object}
        yield self.managed_object
        for a in self.iter_consequences():
            if a.managed_object not in seen:
                seen.add(a.managed_object)
                yield a.managed_object

    def set_escalation_close_error(self, error):
        self.escalation_error = error
        self._get_collection().update({"_id": self.id}, {"$set": {"escalation_close_error": error}})

    def close_escalation(self):
        now = datetime.datetime.now()
        self.escalation_close_ts = now
        self._get_collection().update({"_id": self.id}, {"$set": {"escalation_close_ts": now}})

    def set_escalation_close_ctx(self):
        current_context, current_span = get_current_span()
        if current_context or self.escalation_close_ctx:
            self.escalation_close_ctx = current_context
            self._get_collection().update(
                {"_id": self.id}, {"$set": {"escalation_close_ctx": current_context}}
            )


# Avoid circular references
from .activealarm import ActiveAlarm
