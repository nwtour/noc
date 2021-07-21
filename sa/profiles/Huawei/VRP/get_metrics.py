# ---------------------------------------------------------------------
# Huawei.VRP.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics
from .oidrules.slot import SlotRule
from .oidrules.sslot import SSlotRule
from noc.core.mib import mib


SLA_METRICS_MAP = {
    "SLA | Packets": "NQA-MIB::nqaJitterStatsSentProbes",
    "SLA | Packets | Loss | Ratio": "NQA-MIB::nqaJitterCollectStatsPacketLossRatio",
    "SLA | Packets | Loss | Out": "NQA-MIB::nqaJitterStatsPacketLossSD",
    "SLA | Packets | Loss | In": "NQA-MIB::nqaJitterStatsPacketLossDS",
    "SLA | Packets | Disordered": "NQA-MIB::nqaJitterStatsPktDisorderNum",
    "SLA | Probes | Error": "NQA-MIB::nqaJitterStatsErrors",
    "SLA | OneWayLatency | Out | Max": "NQA-MIB::nqaJitterStatsMaxDelaySD",
    "SLA | OneWayLatency | In | Max": "NQA-MIB::nqaJitterStatsMaxDelayDS",
    "SLA | Jitter | Avg": "NQA-MIB::nqaJitterStatsAvgJitter",
    "SLA | Jitter | Out | Avg": "NQA-MIB::nqaJitterStatsAvgJitterSD",
    "SLA | Jitter | In | Avg": "NQA-MIB::nqaJitterStatsAvgJitterDS",
    "SLA | Jitter | MOS": "NQA-MIB::nqaJitterStatsOperOfMos",
    "SLA | Jitter | ICPIF": "NQA-MIB::nqaJitterStatsOperOfIcpif",
    "SLA | RTT | Min": "NQA-MIB::nqaJitterStatsRTTMin",
    "SLA | RTT | Max": "NQA-MIB::nqaJitterStatsRTTMax",
}


class Script(GetMetricsScript):
    name = "Huawei.VRP.get_metrics"

    OID_RULES = [SlotRule, SSlotRule]

    @metrics(
        ["Interface | Status | Duplex"],
        has_capability="DB | Interfaces",
        matcher="is_cx200X",
        volatile=False,
        access="S",
    )
    def get_duplex_interface_metrics(self, metrics):
        if_map = {
            m.ifindex: m.labels
            for m in metrics
            if m.ifindex and m.metric == "Interface | Status | Duplex"
        }
        for oid, duplex in self.snmp.getnext(mib["EtherLike-MIB::dot3StatsDuplexStatus"]):
            _, ifindex = oid.rsplit(".", 1)
            if int(ifindex) not in if_map:
                continue
            self.set_metric(id=("Interface | Status | Duplex", if_map[int(ifindex)]), value=duplex)

    @metrics(
        ["Subscribers | Summary"],
        has_capability="BRAS | PPPoE",
        volatile=False,
        access="S",  # not CLI version
    )
    def get_subscribers_metrics(self, metrics):
        if "Slot | Member Ids" in self.capabilities:
            hwSlotIndex = self.capabilities["Slot | Member Ids"].split(" | ")
            for si in hwSlotIndex:
                for mi in [0, 1]:
                    v = self.snmp.get(f"1.3.6.1.4.1.2011.5.2.1.33.1.8.{si}.{mi}")
                    if v:
                        self.set_metric(
                            id=("Subscribers | Summary", None),
                            labels=("noc::chassis::0", f"noc::slot::{si}", f"noc::module::{mi}"),
                            value=int(v),
                            multi=True,
                        )
        v = self.snmp.get("1.3.6.1.4.1.2011.5.2.1.14.1.2.0")
        if v:
            self.set_metric(
                id=("Subscribers | Summary", None),
                labels=[],
                value=int(v),
                multi=True,
            )

    @metrics(
        [
            "Interface | CBQOS | Drops | In | Delta",
            "Interface | CBQOS | Drops | Out | Delta",
            "Interface | CBQOS | Octets | In | Delta",
            "Interface | CBQOS | Octets | Out | Delta",
            "Interface | CBQOS | Packets | In | Delta",
            "Interface | CBQOS | Packets | Out | Delta",
        ],
        volatile=False,
        access="S",  # CLI version
    )
    def get_interface_cbqos_metrics_snmp(self, metrics):
        """
        Use available SNMP Table for collecting value
        :param metrics:
        :return:
        """
        if self.has_capability("Huawei | OID | hwCBQoSPolicyStatisticsClassifierTable"):
            self.get_interface_cbqos_metrics_policy_snmp(metrics)
        elif self.has_capability("Huawei | OID | hwCBQoSClassifierStatisticsTable"):
            self.get_interface_cbqos_metrics_classifier_snmp(metrics)

    def get_interface_cbqos_metrics_classifier_snmp(self, metrics):
        self.logger.debug("Use hwCBQoSClassifierStatisticsTable for collected metrics")
        ifaces = {m.ifindex: m.labels for m in metrics if m.ifindex}
        direction_map = {1: "In", 2: "Out"}
        class_map = {}
        for oid, name in self.snmp.getnext(mib["HUAWEI-CBQOS-MIB::hwCBQoSClassifierName"]):
            class_map[oid.rsplit(".", 1)[-1]] = name
        for index, packets, bytes, discards in self.snmp.get_tables(
            [
                mib["HUAWEI-CBQOS-MIB::hwCBQoSClassifierMatchedPackets"],
                mib["HUAWEI-CBQOS-MIB::hwCBQoSClassifierMatchedBytes"],
                mib["HUAWEI-CBQOS-MIB::hwCBQoSClassifierMatchedDropPackets"],
            ]
        ):
            ifindex, direction, ifvlanid1, ifvlanid2, classifier = index.split(".")
            if ifindex not in ifaces:
                continue
            ts = self.get_ts()
            for metric, value in [
                (f"Interface | CBQOS | Drops | {direction_map[direction]} | Delta", discards),
                (f"Interface | CBQOS | Octets | {direction_map[direction]} | Delta", bytes),
                # (f"Interface | CBQOS | Octets | {direction_map[direction]}", bytes),
                (f"Interface | CBQOS | Packets | {direction_map[direction]} | Delta", packets),
                # (f"Interface | CBQOS | Packets | {direction_map[direction]}", packets),
            ]:
                scale = 1
                self.set_metric(
                    id=(metric, ifaces[ifindex]),
                    metric=metric,
                    value=float(value),
                    ts=ts,
                    labels=ifaces[ifindex] + [f"noc::traffic_class::{class_map[classifier]}"],
                    multi=True,
                    type="delta" if metric.endswith("Delta") else "gauge",
                    scale=scale,
                )

    def get_interface_cbqos_metrics_policy_snmp(self, metrics):
        self.logger.debug("Use hwCBQoSPolicyStatisticsClassifierTable for collected metrics")
        ifaces = {m.ifindex: m.labels for m in metrics if m.ifindex}
        direction_map = {"1": "In", "2": "Out"}
        for index, packets, bytes, discards in self.snmp.get_tables(
            [
                mib["HUAWEI-CBQOS-MIB::hwCBQoSPolicyStatClassifierMatchedPassPackets"],
                mib["HUAWEI-CBQOS-MIB::hwCBQoSPolicyStatClassifierMatchedPassBytes"],
                mib["HUAWEI-CBQOS-MIB::hwCBQoSPolicyStatClassifierMatchedDropPackets"],
            ]
        ):
            ifindex, ifvlanid1, direction, classifier = index.split(".", 3)
            ifindex = int(ifindex)
            if not ifindex or ifindex not in ifaces:
                self.logger.info("Interface Vlan %s not collected", ifvlanid1)
                # Interface vlan
                continue
            traffic_class = "".join(chr(int(c)) for c in classifier.split(".")[1:])
            ts = self.get_ts()
            for metric, value in [
                (f"Interface | CBQOS | Drops | {direction_map[direction]} | Delta", discards),
                (f"Interface | CBQOS | Octets | {direction_map[direction]} | Delta", bytes),
                # (f"Interface | CBQOS | Load | {direction_map[direction]}", bytes),
                (f"Interface | CBQOS | Packets | {direction_map[direction]} | Delta", packets),
                # (f"Interface | CBQOS | Packets | {direction_map[direction]}", packets),
            ]:
                mtype, scale = "gauge", 1
                if metric.endswith("Delta"):
                    mtype = "delta"
                self.set_metric(
                    id=(metric, ifaces[ifindex]),
                    metric=metric,
                    value=float(value),
                    ts=ts,
                    labels=ifaces[ifindex] + [f"noc::traffic_class::{traffic_class}"],
                    multi=True,
                    type=mtype,
                    scale=scale,
                )

    def collect_profile_metrics(self, metrics):
        # SLA Metrics
        if self.has_capability("Huawei | NQA | Probes"):
            self.get_ip_sla_udp_jitter_metrics_snmp(
                [m for m in metrics if m.metric in SLA_METRICS_MAP]
            )

    # @metrics(
    #     list(SLA_METRICS_MAP.keys()),
    #     has_capability="Huawei | NQA | Probes",
    #     volatile=True,
    #     access="S",  # CLI version
    # )
    def get_ip_sla_udp_jitter_metrics_snmp(self, metrics):
        """
        Returns collected ip sla metrics in form
        probe id -> {
            rtt: RTT in seconds
        }
        :return:
        """
        oids = {}
        # stat_index = 250
        stat_index = {}
        for oid, r in self.snmp.getnext(mib["NQA-MIB::nqaJitterStatsCompletions"], only_first=True):
            key = ".".join(oid.split(".")[14:-1])
            stat_index[key] = oid.rsplit(".", 1)[-1]
        for m in metrics:
            if m.metric not in SLA_METRICS_MAP:
                continue
            if len(m.labels) < 2:
                continue
            _, name = m.labels[0].rsplit("::", 1)
            _, group = m.labels[1].rsplit("::", 1)
            key = f'{len(group)}.{".".join(str(ord(s)) for s in group)}.{len(name)}.{".".join(str(ord(s)) for s in name)}'
            oid = mib[
                SLA_METRICS_MAP[m.metric],
                key,
                stat_index[key],
            ]
            oids[oid] = m
        results = self.snmp.get_chunked(
            oids=list(oids),
            chunk_size=self.get_snmp_metrics_get_chunk(),
            timeout_limits=self.get_snmp_metrics_get_timeout(),
        )
        ts = self.get_ts()
        for r in results:
            if results[r] is None:
                continue
            m = oids[r]
            self.set_metric(
                id=m.id,
                metric=m.metric,
                value=float(results[r]),
                ts=ts,
                labels=m.labels,
                multi=True,
                type="gauge",
                scale=1,
            )

    # @metrics(
    #     ["Interface | Errors | CRC", "Interface | Errors | Frame"],
    #     has_capability="DB | Interfaces",
    #     volatile=False,
    #     access="C",  # CLI version
    # )
    # def get_vrp_interface_metrics(self, metrics):
    #     v = self.cli("display interface")
    #     ifdata = self.profile.parse_ifaces(v)
    #     for iface, data in ifdata.items():
    #         iface = self.profile.convert_interface_name(iface)
    #         ipath = ["", "", "", iface]
    #         if "CRC" in data:
    #             self.set_metric(id=("Interface | Errors | CRC", ipath), value=int(data["CRC"]))
    #         if "Frames" in data:
    #             self.set_metric(id=("Interface | Errors | Frame", ipath), value=int(data["Frames"]))
