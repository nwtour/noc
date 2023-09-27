# ---------------------------------------------------------------------
# Generate event classes reference
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
import os
import re
import json
from dataclasses import dataclass
from typing import List, Iterable, DefaultDict, Tuple, Dict, Any
import logging
from collections import defaultdict
from pathlib import Path
from itertools import islice
from enum import Enum

# Third-party modules
import mkdocs_gen_files
import jinja2

# @todo: Arbitrary ToC depth
# @todo: en/ru

logger = logging.getLogger("mkdocs")

BUCKET_DEPTH = 1
AC_BUCKET_DEPTH = 1
COLLECTION_ROOT = Path("collections", "fm.eventclasses")
DOCS = Path("docs")
BOOK = Path("event-classes-reference")
YES = "{{ yes }}"
NO = "{{ no }}"

TEMPLATE = """# {{ title }} | *

{% for item in items %}
## {{ item.name }}
{% if item.symptoms -%}
### Symptoms
{{ item.symptoms }}
{% endif %}
{% if item.probable_causes %}
### Probable Causes
{{ item.probable_causes }}
{% endif %}
{% if item.recommended_actions %}
### Recommended Actions
{{ item.recommended_actions }}
{% endif %}
{% if item.vars %}
### Variables
| Name | Type | Description | Required |
| --- | --- | --- | --- |
{% for v in item.vars -%}
| {{ v.name }} | `{{ v.type }}` | {{ v.description }} | {% if v.required %}{{ yes }}{% else %}{{ no }}{% endif %} |
{% endfor %}
{% endif %}
{% if item.disposition -%}
### Related Alarms
| Alarm Class | Role | Description |
| --- | --- | --- |
{% for v in item.disposition -%}
| [{{ v.md_alarm_class }}]({{ v.alarm_link }}) | {% if v.action.is_open %}:material-arrow-up: opening event{% elif v.action.is_close %}:material-arrow-down: closing event{% endif %} | {{ v.name }} |
{% endfor %}
{% endif %}
{% endfor %}
"""


rx_md_anchor = re.compile(r"[ _\|\(\)/]+")


@dataclass(order=True)
class Var(object):
    name: str
    description: str
    type: str
    required: bool

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "Var":
        """
        Create from dict
        """
        return Var(
            name=d["name"], description=d["description"], type=d["type"], required=d["required"]
        )


class Action(Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"
    IGNORE = "IGNORE"

    @classmethod
    def from_action(cls, a: str) -> "Action":
        if a == "clear":
            return Action.CLOSE
        elif a == "raise":
            return Action.OPEN
        elif a == "ignore":
            return Action.IGNORE
        else:
            msg = f"Invalid action: {a}"
            raise ValueError(msg)

    @property
    def is_ignored(self) -> bool:
        return self == Action.IGNORE

    @property
    def is_open(self) -> bool:
        return self == Action.OPEN

    @property
    def is_close(self) -> bool:
        return self == Action.CLOSE


@dataclass(order=True)
class Disposition(object):
    alarm_class: str
    name: str
    action: Action

    @classmethod
    def from_json(cls, d: Dict[str, Any]) -> "Disposition":
        """
        Create from dict
        """
        return Disposition(
            alarm_class=d.get("alarm_class__name", ""),
            name=d["name"],
            action=Action.from_action(d["action"]),
        )

    @property
    def md_alarm_class(self) -> str:
        """
        Markdown-quoted name
        """
        return self.alarm_class.replace("|", "\\|")

    @property
    def alarm_link(self) -> str:
        path = [".."] * BUCKET_DEPTH
        path.append("alarm-classes-reference")
        path += [
            canonical_name(z)
            for z in islice((x.strip() for x in self.alarm_class.split("|", 1)), 0, AC_BUCKET_DEPTH)
        ]
        fp = "/".join(path)
        anchor = rx_md_anchor.sub("-", self.alarm_class.lower())
        return f"{fp}.md#{anchor}"


@dataclass(order=True)
class Data(object):
    """
    Collections data.

    Attributes:
        name: Alarm class name
        symptoms: Alarm symptoms
        probable_causes: Probable causes
        recommended_actions: Reccomentations
        vars: List of alarm variables
    """

    name: str
    symptoms: str
    probable_causes: str
    recommended_actions: str
    vars: List[Var]
    disposition: List[Disposition]

    @classmethod
    def read(cls, path: Path) -> "Data":
        """
        Read from JSON.

        Args:
            path: File path

        Returns:
            Initialized Data structure
        """
        with open(path) as fp:
            data = json.load(fp)
        disposition = [Disposition.from_json(x) for x in data.get("disposition", [])]
        return Data(
            name=data["name"],
            symptoms=data["symptoms"],
            probable_causes=data["probable_causes"],
            recommended_actions=data["recommended_actions"],
            vars=[Var.from_json(x) for x in data["vars"]],
            disposition=[x for x in disposition if not x.action.is_ignored],
        )

    @property
    def md_name(self) -> str:
        """
        Markdown-quoted name
        """
        return self.name.replace("|", "\\|")

    @property
    def md_anchor(self) -> str:
        return rx_md_anchor.sub("-", self.name.lower())

    @property
    def bucket(self) -> Tuple[str, ...]:
        return tuple(islice((x.strip() for x in self.name.split("|", 1)), 0, BUCKET_DEPTH))

    def link_from(self, src: "Data") -> str:
        """
        Generate MD link from source to self.

        Args:
            src: Source item (page)
        """
        dst_bucket = self.bucket
        src_bucket = src.bucket
        anchor = f"#{self.md_anchor}"
        if src_bucket == dst_bucket:
            return anchor
        # Calculate common path
        common = 0
        for x, y in zip(src_bucket, dst_bucket):
            if x == y:
                common += 1
            else:
                break
        # Build link
        link = []
        up = len(src_bucket) - common
        if up > 0:
            link += [".."] * up
        link += list(bucket_path(dst_bucket[common:]).parts)
        return "/".join(link) + anchor


def iter_data() -> Iterable[Data]:
    """
    Iterate collection data.

    Returns:
        Yields Data structures
    """
    logger.info("Reading collections")
    n = 0
    t = time.time()
    for path in COLLECTION_ROOT.rglob("*.json"):
        yield Data.read(path)
        n += 1
    dt = time.time() - t
    logger.info("%d items read in %.3fs", n, dt)


def get_buckets() -> DefaultDict[Tuple[str, ...], List[Data]]:
    buckets: DefaultDict[Tuple[str, ...], List[Data]] = defaultdict(list)
    for data in iter_data():
        buckets[data.bucket].append(data)
    return buckets


def canonical_name(s: str) -> str:
    """
    Convert name to canonical one.
    """
    return s.replace(" | ", "-").replace(" ", "-").lower()


def bucket_path(s: Tuple[str, ...]) -> Path:
    """
    Convert bucket tuple to .md path
    """
    return Path(*tuple(canonical_name(x) for x in s)).with_suffix(".md")


rx_split_alnum = re.compile(r"(\d+|[^0-9]+)")


def _iter_split_alnum(s: str) -> Iterable[str]:
    """
    Iterator yielding alphabetic and numeric sections if string

    :param s:
    :return:
    """
    for match in rx_split_alnum.finditer(s):
        yield match.group(0)


def alnum_key(d: Data) -> str:
    """
    Comparable alpha-numeric key
    """

    def maybe_formatted_int(v: str) -> str:
        try:
            return "%012d" % int(v)
        except ValueError:
            return v

    return "".join(maybe_formatted_int(x) for x in _iter_split_alnum(d.name))


def main():
    """
    Generate Connection Types Reference.
    """
    # Compile template
    tpl = jinja2.Template(TEMPLATE)
    # Load buckets
    buckets = get_buckets()
    # Load alarms
    # Generate navigation and content
    nav = mkdocs_gen_files.Nav()
    nav["Overview"] = Path("index.md")
    for bucket in sorted(buckets):
        rel_path = bucket_path(bucket)
        nav[bucket] = rel_path
        items = list(sorted(buckets[bucket], key=alnum_key))
        out = BOOK / rel_path
        logging.debug("Rendering %s (%d items)", out, len(items))
        # with mkdocs_gen_files.open(out, "w") as fp:
        out_path = DOCS / out
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as fp:
            title = " | ".join(bucket)
            fp.write(tpl.render(items=items, title=title, yes=YES, no=NO))
    # Write navigation
    summary_path = BOOK / "__SUMMARY__"
    # with mkdocs_gen_files.open(summary_path, "w") as fp:
    with open(DOCS / summary_path, "w") as fp:
        fp.writelines(nav.build_literate_nav())


# Execute
if __name__ == "__main__":
    main()
