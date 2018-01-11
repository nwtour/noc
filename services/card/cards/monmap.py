# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MonMap
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
import itertools
from collections import defaultdict
# Third-party modules
import cachetools
# import geojson
import random
# NOC modules
from noc.services.card.cards.base import BaseCard
from noc.inv.models.object import Object
from noc.lib.nosql import DoesNotExist
from noc.sa.models.managedobject import ManagedObject
from noc.fm.models.activealarm import ActiveAlarm
from noc.sa.models.servicesummary import ServiceSummary
from noc.gis.models.layer import Layer
from noc.config import config


class MonMapCard(BaseCard):
    name = "monmap"
    card_css = [
        "/ui/pkg/leaflet/leaflet.css",
        "/ui/pkg/leaflet.markercluster/MarkerCluster.css",
        "/ui/card/css/monmap.css"
    ]
    card_js = [
        "/ui/pkg/leaflet/leaflet.js",
        "/ui/pkg/leaflet.heat/leaflet-heat.js",
        "/ui/pkg/leaflet.markercluster/leaflet.markercluster.js",
        "/ui/card/js/monmap.js"
    ]

    default_template_name = "monmap"
    o_default_name = "Root"

    color_map = {"error": "#FF0000",
                 "warning": "#F0C20C",
                 "default": "#6ECC39"}

    _layer_cache = {}
    TOOLTIP_LIMIT = config.card.alarmheat_tooltip_limit

    def get_object(self, id=None):
        self.root = Object.objects.get(name=self.o_default_name)
        if id:
            try:
                self.root = Object.objects.get(id=id)
            except DoesNotExist:
                pass
        print id

    def get_data(self):
        p = self.current_user.get_profile()
        return {
            "maintenance": 0,
            "lon": p.heatmap_lon or 0,
            "lat": p.heatmap_lat or 0,
            "zoom": p.heatmap_zoom or 0
        }

    @classmethod
    @cachetools.cachedmethod(operator.attrgetter("_layer_cache"))
    def get_pop_layers(cls):
        return list(
            Layer.objects.filter(code__startswith="pop_")
        )

    def get_ajax_data(self, **kwargs):
        def update_dict(d, s):
            for k in s:
                if k in d:
                    d[k] += s[k]
                else:
                    d[k] = s[k]

        # zoom = int(self.handler.get_argument("z"))
        # west = float(self.handler.get_argument("w"))
        # east = float(self.handler.get_argument("e"))
        # north = float(self.handler.get_argument("n"))
        # south = float(self.handler.get_argument("s"))
        # ms = int(self.handler.get_argument("maintenance"))
        # active_layers = [l for l in self.get_pop_layers() if l.min_zoom <= zoom <= l.max_zoom]
        objects = []
        sss = {"error": {},
               "warning": {},
               "good": {}}

        services = defaultdict(list)
        moss = ManagedObject.objects.filter(is_managed=True).exclude(container=None)

        alarms = dict(ActiveAlarm.objects.filter(managed_object__in=list(moss.values_list("id", flat=True))).scalar("managed_object", "severity"))

        for container, mol in itertools.groupby(moss, key=lambda o: o.container):
            x = container.get_data("geopoint", "x")
            y = container.get_data("geopoint", "y")
            mos = list(mol)
            if not x or not y or not len(mos):
                continue
            ss = {
                "name": container.name,
                "id": str(container.id),
                "x": x,
                "y": y,
                "objects": [],
                "total": len(mos),
                "error": 0,
                "warning": 0,
                "good": 0}
            for mo in mos:
                s_service = ServiceSummary.get_object_summary(mo)
                status = "good"
                if random.randint(0, 10) > 8:
                    status = "error"
                elif alarms.get(mo) < 2000:
                    status = "warning"
                elif alarms.get(mo) > 2000:
                    status = "error"
                update_dict(sss[status], s_service["service"])
                ss[status] += 1
                ss["objects"] += [{"id": mo.id, "name": mo.name, "status": status}]

            objects += [ss.copy()]
        for r in ["error", "warning", "good"]:
            for p in sss[r]:
                services[p] += [(self.color_map.get(r, self.color_map["default"]),
                                 sss[r].get(p, 0))]
        return {
            "objects": objects,
            "summary": self.f_glyph_summary({
                "service": services
                # "subscriber": subscribers
            }),
        }

    @staticmethod
    def get_containers_by_root(root_id=None):
        # @todo containers only with coordinates (Filter by models)
        # from noc.sa.models.managedobject import ManagedObject
        # from noc.inv.models.object import Object
        # If None - all objects
        root = Object.get_by_id(root_id)
        work_set = {root.id}
        os = set()
        kk = None
        for r in range(1, 9):
            work_set = set(Object.objects.filter(container__in=list(work_set)).values_list("id"))
            # work_set |= work_set.union(os)
            os |= work_set
            if len(work_set) == kk:
                break
            kk = len(work_set)
            print len(work_set)
            print len(os)
        return os

    def f_glyph_summary(self, s, collapse=False):
        def get_summary(d, profile):
            v = []
            if hasattr(profile, "show_in_summary"):
                def show_in_summary(p):
                    return p.show_in_summary
            else:
                def show_in_summary(p):
                    return True
            # for p, c in sorted(d.items(), key=lambda x: -x[1]):
            for p, c in sorted(d.items()):
                pv = profile.get_by_id(p)
                if pv and show_in_summary(pv):
                    if isinstance(c, list):
                        badge = "".join(" <span class=\"badge\" style=\"color: %s\">%s</span>" % cc for cc in c)
                    else:
                        if collapse and c < 2:
                            badge = ""
                        else:
                            badge = " <span class=\"badge\">%s</span>" % c
                    v += [
                        "<i class=\"%s\" title=\"%s\"></i>%s" % (
                            pv.glyph,
                            pv.name,
                            badge
                        )
                    ]
            return " ".join(v)

        if not isinstance(s, dict):
            return ""
        r = []
        if "subscriber" in s:
            from noc.crm.models.subscriberprofile import SubscriberProfile
            r += [get_summary(s["subscriber"], SubscriberProfile)]
        if "service" in s:
            from noc.sa.models.serviceprofile import ServiceProfile
            r += [get_summary(s["service"], ServiceProfile)]
        if "fresh_alarms" in s and s["fresh_alarms"]:
            r += ["<i class=\"fa fa-exclamation-triangle\"></i><span class=\"badge\">%s</span>"
                  % s["fresh_alarms"]["FreshAlarm"]]
        r = [x for x in r if x]
        return "&nbsp;".join(r)
