"""wiki-tool — deterministic indexer/linter for instances/.

Zero external deps. Assumes instance files follow wiki-instance-guide.md
conventions strictly, so a minimal YAML subset parser is sufficient.

Commands
--------
  build-index          parse instances/**/*.yaml -> index/*.json
  check-invariants     run entity invariants against parsed instances
  check-refs           ensure every id reference resolves
  check-coverage       axis cartesian product vs actual instances
  list                 quick: list ids under an entity (e.g. `list skills`)
  query                filter instances by field=value pairs
  all                  build-index + all checks (exit 1 if any fail)

Everything runs offline, no LLM involvement.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
INSTANCES = ROOT / "instances"
INDEX = ROOT / "index"
SCHEMAS = ROOT  # wiki-entity-*.md and wiki-skill-schema.md live at root


# ---------------------------------------------------------------------------
# Minimal YAML parser (subset)
# ---------------------------------------------------------------------------
# Supports what wiki-instance-guide.md allows:
#   - top-level single mapping key
#   - nested mappings by indentation
#   - sequences via `- ` (block) and `[a, b, c]` (flow, scalars only)
#   - scalars: int, float, bool, null, "quoted string", bare string
#   - inline comments starting with '#'
# Any construct outside this set raises an explicit error.

_FLOW_SPLIT = re.compile(r",\s*(?![^\[\]]*\])")


def _strip_comment(line: str) -> str:
    in_str = False
    quote = ""
    out = []
    i = 0
    while i < len(line):
        ch = line[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < len(line):
                out.append(line[i + 1])
                i += 2
                continue
            if ch == quote:
                in_str = False
            i += 1
            continue
        if ch in ('"', "'"):
            in_str = True
            quote = ch
            out.append(ch)
            i += 1
            continue
        if ch == "#":
            break
        out.append(ch)
        i += 1
    return "".join(out).rstrip()


def _parse_scalar(raw: str) -> Any:
    s = raw.strip()
    if s == "" or s == "~" or s.lower() == "null":
        return None
    if s.lower() == "true":
        return True
    if s.lower() == "false":
        return False
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    # int
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    # float
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    # flow sequence [a, b, c]
    if s.startswith("[") and s.endswith("]"):
        body = s[1:-1].strip()
        if body == "":
            return []
        parts = _FLOW_SPLIT.split(body)
        return [_parse_scalar(p) for p in parts]
    # flow mapping {a: 1, b: 2} — limited, rare in instances
    if s.startswith("{") and s.endswith("}"):
        body = s[1:-1].strip()
        if body == "":
            return {}
        out: dict = {}
        for part in _FLOW_SPLIT.split(body):
            if ":" not in part:
                raise ValueError(f"bad flow map entry: {part!r}")
            k, v = part.split(":", 1)
            out[k.strip()] = _parse_scalar(v)
        return out
    return s


class YamlError(Exception):
    pass


def parse_yaml(text: str, source: str = "<str>") -> Any:
    # normalize line endings, keep line numbers
    lines = text.splitlines()
    # strip comments + record (indent, content, lineno) for non-blank
    records: list[tuple[int, str, int]] = []
    for n, raw in enumerate(lines, 1):
        stripped = _strip_comment(raw)
        if stripped.strip() == "":
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        if "\t" in stripped[:indent]:
            raise YamlError(f"{source}:{n}: tabs in indentation not allowed")
        records.append((indent, stripped.lstrip(" "), n))

    pos = [0]  # cursor

    def peek() -> tuple[int, str, int] | None:
        return records[pos[0]] if pos[0] < len(records) else None

    def advance() -> tuple[int, str, int]:
        rec = records[pos[0]]
        pos[0] += 1
        return rec

    def parse_block(base_indent: int) -> Any:
        # Decide: mapping or sequence (by looking at first record)
        nxt = peek()
        if nxt is None:
            return None
        ind, content, lineno = nxt
        if ind < base_indent:
            return None
        if content.startswith("- "):
            return parse_sequence(base_indent)
        return parse_mapping(base_indent)

    def parse_sequence(base_indent: int) -> list:
        items: list = []
        while True:
            nxt = peek()
            if nxt is None:
                break
            ind, content, lineno = nxt
            if ind < base_indent or not content.startswith("- "):
                break
            advance()
            item_body = content[2:]
            if item_body.strip() == "":
                # nested block after dash
                child = parse_block(base_indent + 2)
                items.append(child if child is not None else {})
            elif ":" in item_body and not (
                item_body.startswith('"') or item_body.startswith("'")
            ) and not item_body.startswith("["):
                # inline mapping start: `- key: value` — treat as first key of dict
                k, v = _split_key_value(item_body, lineno, source)
                obj: dict = {}
                if v == "":
                    child = parse_block(base_indent + 2 + 1)  # after "- "
                    obj[k] = child if child is not None else {}
                else:
                    obj[k] = _parse_scalar(v)
                # continue reading remaining keys at deeper indent
                while True:
                    nxt2 = peek()
                    if nxt2 is None:
                        break
                    ind2, content2, ln2 = nxt2
                    if ind2 <= base_indent:
                        break
                    if content2.startswith("- "):
                        break
                    # must be a key of this dict — indent must equal base_indent + 2
                    if ind2 != base_indent + 2:
                        break
                    advance()
                    k2, v2 = _split_key_value(content2, ln2, source)
                    if v2 == "":
                        child = parse_block(ind2 + 2)
                        obj[k2] = child if child is not None else {}
                    else:
                        obj[k2] = _parse_scalar(v2)
                items.append(obj)
            else:
                items.append(_parse_scalar(item_body))
        return items

    def parse_mapping(base_indent: int) -> dict:
        obj: dict = {}
        while True:
            nxt = peek()
            if nxt is None:
                break
            ind, content, lineno = nxt
            if ind < base_indent:
                break
            if ind > base_indent:
                raise YamlError(
                    f"{source}:{lineno}: unexpected indent {ind} (expected {base_indent})"
                )
            if content.startswith("- "):
                break
            advance()
            k, v = _split_key_value(content, lineno, source)
            if v == "":
                child = parse_block(base_indent + 2)
                obj[k] = child if child is not None else {}
            else:
                obj[k] = _parse_scalar(v)
        return obj

    if not records:
        return None
    first_indent = records[0][0]
    return parse_block(first_indent)


def _split_key_value(content: str, lineno: int, source: str) -> tuple[str, str]:
    # split on first unquoted colon
    in_str = False
    quote = ""
    for i, ch in enumerate(content):
        if in_str:
            if ch == quote:
                in_str = False
            continue
        if ch in ('"', "'"):
            in_str = True
            quote = ch
            continue
        if ch == ":":
            return content[:i].strip(), content[i + 1 :].strip()
    raise YamlError(f"{source}:{lineno}: mapping entry missing ':': {content!r}")


# ---------------------------------------------------------------------------
# Schema extraction (from wiki-entity-*.md / wiki-skill-schema.md)
# ---------------------------------------------------------------------------
# We don't need a full markdown parser. We only need the enum values in §1
# Classification Axes and invariants in §9.

AXES_HEADER = re.compile(r"^##\s*1️⃣\s*분류\s*축", re.UNICODE)
INVARIANT_HEADER = re.compile(r"^##\s+.*불변식", re.UNICODE)
NEXT_TOP_SECTION = re.compile(r"^##\s+", re.UNICODE)
AXIS_SUBHEADER = re.compile(r"^###\s+Axis\.(\w+)", re.UNICODE)
CODE_FENCE = re.compile(r"^```")
ENUM_LINE = re.compile(r"^\s*-\s+([A-Za-z0-9_\.]+)")
RULE_LINE = re.compile(r'^\s*-\s+rule:\s*"(.+)"\s*$')


def extract_axes(md_path: Path) -> dict[str, list[str]]:
    """Return {AxisName: [enum values...]} from the first §1 section."""
    if not md_path.exists():
        return {}
    lines = md_path.read_text(encoding="utf-8").splitlines()
    in_axes = False
    in_axis = None
    in_code = False
    axes: dict[str, list[str]] = {}
    for line in lines:
        if not in_axes:
            if AXES_HEADER.search(line):
                in_axes = True
            continue
        if NEXT_TOP_SECTION.match(line) and not AXES_HEADER.search(line):
            break
        m = AXIS_SUBHEADER.match(line)
        if m:
            in_axis = m.group(1)
            axes[in_axis] = []
            in_code = False
            continue
        if CODE_FENCE.match(line):
            in_code = not in_code
            continue
        if in_code and in_axis:
            em = ENUM_LINE.match(line)
            if em:
                axes[in_axis].append(em.group(1))
    return axes


def extract_invariants(md_path: Path) -> list[str]:
    if not md_path.exists():
        return []
    lines = md_path.read_text(encoding="utf-8").splitlines()
    in_inv = False
    in_code = False
    rules: list[str] = []
    for line in lines:
        if not in_inv:
            if INVARIANT_HEADER.search(line):
                in_inv = True
            continue
        if NEXT_TOP_SECTION.match(line) and not INVARIANT_HEADER.search(line):
            break
        if CODE_FENCE.match(line):
            in_code = not in_code
            continue
        if in_code:
            m = RULE_LINE.match(line)
            if m:
                rules.append(m.group(1))
    return rules


# ---------------------------------------------------------------------------
# Instance loading
# ---------------------------------------------------------------------------

ENTITY_DIRS = {
    "skill": "skills",
    "state": "states",
    "monster": "monsters",
    "item": "items",
    "zone": "zones",
    "quest": "quests",
    "interaction": "interactions",
    "ui": "ui-screens",
}

SCHEMA_FILES = {
    "skill": "wiki-skill-schema.md",
    "state": "wiki-entity-state.md",
    "monster": "wiki-entity-monster.md",
    "item": "wiki-entity-item.md",
    "zone": "wiki-entity-zone.md",
    "quest": "wiki-entity-quest.md",
    "interaction": "wiki-entity-interaction.md",
    "ui": "wiki-entity-ui.md",
}


def load_instances() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {k: [] for k in ENTITY_DIRS}
    for kind, sub in ENTITY_DIRS.items():
        d = INSTANCES / sub
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.yaml")):
            try:
                doc = parse_yaml(f.read_text(encoding="utf-8"), source=str(f))
            except YamlError as e:
                print(f"[parse error] {e}", file=sys.stderr)
                continue
            if not isinstance(doc, dict) or kind not in doc:
                print(
                    f"[skip] {f}: top-level key '{kind}' not found",
                    file=sys.stderr,
                )
                continue
            body = doc[kind]
            body["__file"] = str(f.relative_to(ROOT)).replace("\\", "/")
            out[kind].append(body)
    return out


# ---------------------------------------------------------------------------
# build-index
# ---------------------------------------------------------------------------

def _as_list(v: Any) -> list:
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]


def build_index(instances: dict[str, list[dict]]) -> dict[str, Any]:
    # by-axis: for each entity, group ids by each scalar/list axis value.
    by_axis: dict[str, dict[str, dict[str, list[str]]]] = {}
    by_archetype: dict[str, list[str]] = {}

    # Axes to index (derived from schema) — we take the intersection of
    # schema-defined axes and the keys actually present in instances.
    for kind, items in instances.items():
        if not items:
            continue
        schema = SCHEMAS / SCHEMA_FILES.get(kind, "")
        axes = extract_axes(schema)
        axis_camel = {a[0].lower() + a[1:]: vals for a, vals in axes.items()}
        by_axis[kind] = {}
        for inst in items:
            iid = inst.get("id", "?")
            for field, enum_vals in axis_camel.items():
                # try a couple of key spellings (exact, "Axis" dropped)
                v = inst.get(field)
                if v is None:
                    continue
                bucket = by_axis[kind].setdefault(field, {})
                for val in _as_list(v):
                    bucket.setdefault(str(val), []).append(iid)
            if kind == "skill":
                arch = inst.get("archetype")
                if arch:
                    by_archetype.setdefault(str(arch), []).append(iid)

    # hubs: reverse map for id references (State.id, Skill.id, Zone.id, Item.id)
    hubs: dict[str, list[dict]] = {}

    def add_ref(target_id: str, source: dict, where: str) -> None:
        hubs.setdefault(target_id, []).append(
            {
                "from": source.get("id", "?"),
                "fromEntity": source.get("__entity_kind", "?"),
                "field": where,
            }
        )

    def walk(node: Any, source: dict, path: str) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, source, f"{path}.{k}" if path else k)
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, source, f"{path}[{i}]")
        elif isinstance(node, str):
            if path == "id":
                return  # don't treat the id field as a reference to itself
            if re.fullmatch(
                r"(skill|state|monster|item|zone|quest|interaction|ui)\.[a-z0-9_]+",
                node,
            ):
                add_ref(node, source, path)

    for kind, items in instances.items():
        for inst in items:
            inst["__entity_kind"] = kind
            walk(inst, inst, "")

    return {
        "by_axis": by_axis,
        "by_archetype": by_archetype,
        "hubs": hubs,
    }


# ---------------------------------------------------------------------------
# check-refs
# ---------------------------------------------------------------------------

def check_refs(instances: dict[str, list[dict]]) -> list[dict]:
    existing: set[str] = set()
    for items in instances.values():
        for inst in items:
            iid = inst.get("id")
            if isinstance(iid, str):
                existing.add(iid)

    problems: list[dict] = []
    id_like = re.compile(
        r"(skill|state|monster|item|zone|quest|interaction|ui)\.[a-z0-9_]+"
    )

    def walk(node: Any, source: dict, path: str) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, source, f"{path}.{k}" if path else k)
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, source, f"{path}[{i}]")
        elif isinstance(node, str) and id_like.fullmatch(node):
            # Skip self
            if node == source.get("id"):
                return
            if node not in existing:
                problems.append(
                    {
                        "from": source.get("id", "?"),
                        "fromFile": source.get("__file"),
                        "path": path,
                        "missingId": node,
                    }
                )

    for items in instances.values():
        for inst in items:
            walk(inst, inst, "")
    return problems


# ---------------------------------------------------------------------------
# check-coverage
# ---------------------------------------------------------------------------

def check_coverage(instances: dict[str, list[dict]]) -> dict[str, Any]:
    """For each entity, for each axis, which enum values have zero instances."""
    out: dict[str, Any] = {}
    for kind, items in instances.items():
        schema = SCHEMAS / SCHEMA_FILES.get(kind, "")
        axes = extract_axes(schema)
        if not axes or not items:
            continue
        kind_report: dict[str, Any] = {}
        for axis_name, values in axes.items():
            field = axis_name[0].lower() + axis_name[1:]
            seen: set[str] = set()
            for inst in items:
                v = inst.get(field)
                for x in _as_list(v):
                    seen.add(str(x))
            missing = [v for v in values if v not in seen]
            kind_report[field] = {
                "defined": values,
                "seen": sorted(seen),
                "missing": missing,
            }
        out[kind] = kind_report
    return out


# ---------------------------------------------------------------------------
# check-invariants
# ---------------------------------------------------------------------------
# Each rule is a small Python predicate over an instance dict. We register
# per-entity rule sets explicitly; the free-text rules in §9 serve as docs.

Violation = dict


def _inv_skill(inst: dict) -> list[Violation]:
    v: list[Violation] = []
    iid = inst.get("id", "?")
    ec = _as_list(inst.get("effectCategory"))
    if "Damage" in ec and inst.get("damageType") in (None, "None"):
        v.append({"id": iid, "rule": "Damage requires damageType != None"})
    if "CrowdControl" in ec and inst.get("controlType") in (None, "None"):
        v.append({"id": iid, "rule": "CrowdControl requires controlType != None"})
    if inst.get("activationType") == "Passive":
        if inst.get("cooldown", 0) != 0 or inst.get("resourceCost", 0) != 0:
            v.append({"id": iid, "rule": "Passive requires cooldown=0 and resourceCost=0"})
    if inst.get("activationType") == "Channeled" and inst.get("channelDuration", 0) <= 0:
        v.append({"id": iid, "rule": "Channeled requires channelDuration > 0"})
    if inst.get("areaType") == "AreaOfEffect" and inst.get("areaRadius", 0) <= 0:
        v.append({"id": iid, "rule": "AreaOfEffect requires areaRadius > 0"})
    if inst.get("targetingMode") == "SelfCast" and inst.get("targetFaction") != "Self":
        v.append({"id": iid, "rule": "SelfCast requires targetFaction=Self"})
    if inst.get("targetingMode") == "NonTargeted" and inst.get("areaType") == "SingleTarget":
        v.append({"id": iid, "rule": "NonTargeted cannot have areaType=SingleTarget"})
    if inst.get("resourceType") == "Free" and inst.get("resourceCost", 0) != 0:
        v.append({"id": iid, "rule": "resourceType=Free requires resourceCost=0"})
    # unique restriction priorities
    prios = [r.get("priority") for r in _as_list(inst.get("restrictions")) if isinstance(r, dict)]
    if len(prios) != len(set(prios)):
        v.append({"id": iid, "rule": "restriction priorities must be unique"})
    if inst.get("durationType") == "OverTime":
        has_duration = any(
            isinstance(e, dict) and (e.get("duration") or 0) > 0
            for e in _as_list(inst.get("effects"))
        )
        if not has_duration:
            v.append({"id": iid, "rule": "durationType=OverTime requires an effect with duration>0"})
    return v


def _inv_state(inst: dict) -> list[Violation]:
    v: list[Violation] = []
    iid = inst.get("id", "?")
    if inst.get("polarity") == "Positive" and inst.get("isHarmful") is True:
        v.append({"id": iid, "rule": "Positive polarity requires isHarmful=false"})
    tags = _as_list(inst.get("tags"))
    if inst.get("category") == "CrowdControl" and not any(
        isinstance(t, str) and t.startswith("CC.") for t in tags
    ):
        v.append({"id": iid, "rule": "CrowdControl category requires a CC.* tag"})
    if inst.get("category") == "DoT":
        if inst.get("tickType") != "Periodic":
            v.append({"id": iid, "rule": "DoT requires tickType=Periodic"})
        has_hp_sub = any(
            isinstance(e, dict)
            and e.get("operation") == "Subtract"
            and e.get("attribute") == "HP"
            for e in _as_list(inst.get("tickEffects"))
        )
        if not has_hp_sub:
            v.append({"id": iid, "rule": "DoT requires tickEffects Subtract HP"})
    if inst.get("category") == "HoT":
        if inst.get("tickType") != "Periodic":
            v.append({"id": iid, "rule": "HoT requires tickType=Periodic"})
        has_hp_add = any(
            isinstance(e, dict) and e.get("operation") == "Add" and e.get("attribute") == "HP"
            for e in _as_list(inst.get("tickEffects"))
        )
        if not has_hp_add:
            v.append({"id": iid, "rule": "HoT requires tickEffects Add HP"})
    if inst.get("tickType") == "Periodic":
        if (inst.get("tickInterval") or 0) <= 0:
            v.append({"id": iid, "rule": "Periodic requires tickInterval > 0"})
        if not _as_list(inst.get("tickEffects")):
            v.append({"id": iid, "rule": "Periodic requires non-empty tickEffects"})
    if inst.get("stackingMode") == "NotStackable" and inst.get("stackMax", 0) != 1:
        v.append({"id": iid, "rule": "NotStackable requires stackMax=1"})
    if inst.get("stackingMode") == "AddStack" and inst.get("stackMax", 0) < 2:
        v.append({"id": iid, "rule": "AddStack requires stackMax >= 2"})
    if inst.get("dispelType") == "Undispellable" and "OnDispel" in _as_list(inst.get("removeOn")):
        v.append({"id": iid, "rule": "Undispellable cannot removeOn OnDispel"})
    if (inst.get("baseDuration") or 0) > (inst.get("maxDuration") or 0):
        v.append({"id": iid, "rule": "baseDuration must be <= maxDuration"})
    if inst.get("durationType") == "Instant" and inst.get("category") not in (
        "Marker",
        "Environmental",
    ):
        v.append({"id": iid, "rule": "Instant duration requires category Marker/Environmental"})
    if _as_list(inst.get("immunitiesGranted")) and inst.get("polarity") != "Positive":
        v.append({"id": iid, "rule": "immunitiesGranted requires polarity=Positive"})
    return v


def _inv_monster(inst: dict) -> list[Violation]:
    v: list[Violation] = []
    iid = inst.get("id", "?")
    if inst.get("lifeState") == "Dead":
        if inst.get("aggroState") != "Leashed":
            v.append({"id": iid, "rule": "lifeState=Dead requires aggroState=Leashed"})
        if inst.get("combatState") != "OutOfCombat":
            v.append({"id": iid, "rule": "lifeState=Dead requires combatState=OutOfCombat"})
    aggro_table = _as_list(inst.get("aggroTable"))
    if not aggro_table and inst.get("aggroState") not in (None, "Idle"):
        v.append({"id": iid, "rule": "empty aggroTable requires aggroState=Idle"})
    if aggro_table and inst.get("aggroState") == "Idle":
        v.append({"id": iid, "rule": "non-empty aggroTable requires aggroState != Idle"})
    if inst.get("rank") in ("Boss", "RaidBoss") and inst.get("isBoss") is not True:
        v.append({"id": iid, "rule": "rank=Boss/RaidBoss requires isBoss=true"})
    if inst.get("rank") == "RaidBoss" and inst.get("lootState") not in (None, "Locked", "Unlooted"):
        v.append({"id": iid, "rule": "RaidBoss requires lootState in {Locked, Unlooted}"})
    if (inst.get("respawnTimer") or 0) > 0 and inst.get("spawnState") != "Respawning":
        v.append({"id": iid, "rule": "respawnTimer>0 requires spawnState=Respawning"})
    slot_skills = [
        s.get("skillId") for s in _as_list(inst.get("skillSlots")) if isinstance(s, dict)
    ]
    policy_ids = [
        p.get("skillId")
        for p in _as_list(
            (inst.get("skillUsagePolicy") or {}).get("priorityList")
            if isinstance(inst.get("skillUsagePolicy"), dict)
            else []
        )
        if isinstance(p, dict)
    ]
    for sid in slot_skills:
        if sid is not None and sid not in policy_ids:
            v.append(
                {"id": iid, "rule": f"skillSlots.skillId {sid} missing from skillUsagePolicy.priorityList"}
            )
    return v


def _inv_item(inst: dict) -> list[Violation]:
    v: list[Violation] = []
    iid = inst.get("id", "?")
    it = inst.get("itemType")
    slot = inst.get("equipmentSlot")
    if it == "Equipment" and slot in (None, "None"):
        v.append({"id": iid, "rule": "itemType=Equipment requires equipmentSlot != None"})
    if it is not None and it != "Equipment" and slot not in (None, "None"):
        v.append({"id": iid, "rule": "itemType != Equipment requires equipmentSlot=None"})
    if inst.get("stackingPolicy") == "NotStackable" and inst.get("maxStackSize", 1) != 1:
        v.append({"id": iid, "rule": "NotStackable requires maxStackSize=1"})
    if inst.get("stackingPolicy") == "Stackable" and inst.get("maxStackSize", 0) < 2:
        v.append({"id": iid, "rule": "Stackable requires maxStackSize >= 2"})
    sc = inst.get("stackCount")
    if sc is not None:
        if sc < 1:
            v.append({"id": iid, "rule": "stackCount must be >= 1"})
        mx = inst.get("maxStackSize")
        if isinstance(mx, int) and sc > mx:
            v.append({"id": iid, "rule": "stackCount must be <= maxStackSize"})
    cd = inst.get("currentDurability")
    if cd is not None:
        if cd < 0:
            v.append({"id": iid, "rule": "currentDurability must be >= 0"})
        md = inst.get("maxDurability")
        if isinstance(md, int) and cd > md:
            v.append({"id": iid, "rule": "currentDurability must be <= maxDurability"})
    if inst.get("enhancementLevel") is not None and inst.get("enhancementLevel") < 0:
        v.append({"id": iid, "rule": "enhancementLevel must be >= 0"})
    loc = inst.get("location")
    loc_type = loc.get("locationType") if isinstance(loc, dict) else None
    if inst.get("isEquipped") is True and loc_type != "Equipment":
        v.append({"id": iid, "rule": "isEquipped=true requires location.locationType=Equipment"})
    if inst.get("bindingType") == "QuestBound":
        if inst.get("destroyable") is not False:
            v.append({"id": iid, "rule": "QuestBound requires destroyable=false"})
        if inst.get("tradable") is not False:
            v.append({"id": iid, "rule": "QuestBound requires tradable=false"})
        if inst.get("sellable") is not False:
            v.append({"id": iid, "rule": "QuestBound requires sellable=false"})
    if inst.get("isUnique") is True and inst.get("maxCarryCount", 1) != 1:
        v.append({"id": iid, "rule": "isUnique=true requires maxCarryCount=1"})
    if inst.get("tradable") is False and loc_type == "AuctionHouse":
        v.append({"id": iid, "rule": "tradable=false cannot have location=AuctionHouse"})
    if (inst.get("buyPrice") or 0) > 0 and "ShopPurchase" not in _as_list(inst.get("acquirableFrom")):
        v.append({"id": iid, "rule": "buyPrice>0 requires acquirableFrom includes ShopPurchase"})
    cap_max = inst.get("capMax")
    if isinstance(cap_max, (int, float)) and cap_max > 0:
        amt = inst.get("amount")
        if isinstance(amt, (int, float)) and amt > cap_max:
            v.append({"id": iid, "rule": "amount must be <= capMax"})
    weekly_cap = inst.get("weeklyCap")
    if isinstance(weekly_cap, (int, float)) and weekly_cap > 0:
        we = inst.get("weeklyEarned")
        if isinstance(we, (int, float)) and we > weekly_cap:
            v.append({"id": iid, "rule": "weeklyEarned must be <= weeklyCap"})
    sockets = inst.get("sockets")
    socket_slots = inst.get("socketSlots")
    if isinstance(sockets, list) and isinstance(socket_slots, int) and len(sockets) != socket_slots:
        v.append({"id": iid, "rule": "sockets.length must equal socketSlots"})
    return v


def _inv_zone(inst: dict) -> list[Violation]:
    v: list[Violation] = []
    iid = inst.get("id", "?")
    if inst.get("zoneType") == "Raid" and inst.get("instanceMode") != "RaidInstance":
        v.append({"id": iid, "rule": "zoneType=Raid requires instanceMode=RaidInstance"})
    if inst.get("safetyLevel") == "Sanctuary" and inst.get("pvpRule") != "Disabled":
        v.append({"id": iid, "rule": "Sanctuary requires pvpRule=Disabled"})
    im = inst.get("instanceMode")
    if im is not None and im != "NotInstanced":
        if not inst.get("instanceId"):
            v.append({"id": iid, "rule": "instanceMode != NotInstanced requires non-empty instanceId"})
    if im == "RaidInstance":
        owner = inst.get("ownerId")
        if not (isinstance(owner, str) and owner.startswith("raid.")):
            v.append({"id": iid, "rule": "RaidInstance requires ownerId of form raid.*"})
    rl = inst.get("requiredLevel")
    rmax = inst.get("recommendedLevelMax")
    if isinstance(rl, int) and isinstance(rmax, int) and rl > rmax:
        v.append({"id": iid, "rule": "requiredLevel must be <= recommendedLevelMax"})
    reset = inst.get("resetPolicy")
    if isinstance(reset, dict) and reset.get("mode") == "Never" and reset.get("schedule") not in (None, "", []):
        v.append({"id": iid, "rule": "resetPolicy.mode=Never requires empty schedule"})
    for ev in _as_list(inst.get("activeEvents")):
        if isinstance(ev, dict):
            st, en = ev.get("startTime"), ev.get("endTime")
            if st is not None and en is not None and not (st < en):
                v.append({"id": iid, "rule": "activeEvents entry requires startTime < endTime"})
                break
    return v


def _inv_quest(inst: dict) -> list[Violation]:
    v: list[Violation] = []
    iid = inst.get("id", "?")
    if inst.get("frequency") == "Daily":
        exp = inst.get("expiresAt")
        if exp is None or exp == 0:
            v.append({"id": iid, "rule": "frequency=Daily requires expiresAt != 0"})
    if (inst.get("timeLimit") or 0) > 0 and "OnTimeout" not in _as_list(inst.get("failureModes")):
        v.append({"id": iid, "rule": "timeLimit>0 requires failureModes includes OnTimeout"})
    for r in _as_list(inst.get("rewards")):
        if isinstance(r, dict) and r.get("rewardType") == "ItemChoice":
            if len(_as_list(r.get("choices"))) < 2:
                v.append({"id": iid, "rule": "ItemChoice reward requires >= 2 choices"})
                break
    if inst.get("state") == "Completed":
        for o in _as_list(inst.get("objectives")):
            if isinstance(o, dict) and not o.get("isOptional") and not o.get("isComplete"):
                v.append(
                    {"id": iid, "rule": "state=Completed requires all non-optional objectives isComplete=true"}
                )
                break
    if inst.get("isAbandonable") is False and inst.get("state") == "Abandoned":
        v.append({"id": iid, "rule": "isAbandonable=false cannot transition to Abandoned"})
    for o in _as_list(inst.get("objectives")):
        if isinstance(o, dict):
            rc = o.get("requiredCount")
            if rc is not None and rc <= 0:
                v.append({"id": iid, "rule": "objectives[].requiredCount must be > 0"})
                break
    cc = inst.get("currentCount")
    rc = inst.get("requiredCount")
    if isinstance(cc, int):
        if cc < 0:
            v.append({"id": iid, "rule": "ObjectiveProgress.currentCount must be >= 0"})
        if isinstance(rc, int) and cc > rc:
            v.append({"id": iid, "rule": "ObjectiveProgress.currentCount must be <= requiredCount"})
    if inst.get("category") == "Achievement" and inst.get("frequency") not in (None, "OneTime"):
        v.append({"id": iid, "rule": "category=Achievement requires frequency=OneTime"})
    return v


def _inv_interaction(inst: dict) -> list[Violation]:
    v: list[Violation] = []
    iid = inst.get("id", "?")
    if inst.get("executionMode") == "Channeled" and inst.get("cancelableWhileCasting") is not True:
        v.append({"id": iid, "rule": "Channeled requires cancelableWhileCasting=true"})
    if inst.get("type") == "Irreversible" and _as_list(inst.get("effectsOnCancel")):
        v.append({"id": iid, "rule": "type=Irreversible requires empty effectsOnCancel"})
    for c in _as_list(inst.get("costs")):
        if isinstance(c, dict) and c.get("consumedOn") == "OnStart" and "refundable" not in c:
            v.append({"id": iid, "rule": "costs[].consumedOn=OnStart requires refundable defined"})
            break
    fail_codes = {
        r.get("code") for r in _as_list(inst.get("failReasons")) if isinstance(r, dict)
    }
    for p in _as_list(inst.get("preconditions")):
        if isinstance(p, dict):
            reason = p.get("reason")
            if reason is None:
                continue
            if isinstance(reason, str) and reason.startswith("System."):
                continue
            if reason not in fail_codes:
                v.append(
                    {"id": iid, "rule": f"preconditions[].reason {reason!r} missing from failReasons"}
                )
                break
    if inst.get("targetSelectionMode") == "NoTarget":
        for p in _as_list(inst.get("parameters")):
            if isinstance(p, dict):
                name = p.get("name", "")
                if isinstance(name, str) and "target" in name.lower():
                    v.append(
                        {"id": iid, "rule": "NoTarget cannot have target-related parameters"}
                    )
                    break
    for s in _as_list(inst.get("sideEffects")):
        if isinstance(s, dict) and s.get("trigger") == "OnInstanceEnter" and inst.get("category") != "Instance":
            v.append({"id": iid, "rule": "OnInstanceEnter sideEffect requires category=Instance"})
            break
    if _as_list(inst.get("failReasons")):
        fb = inst.get("feedback")
        if not (isinstance(fb, dict) and fb.get("onFail")):
            v.append({"id": iid, "rule": "non-empty failReasons requires feedback.onFail defined"})
    flow = inst.get("InteractionFlow") or inst.get("interactionFlow")
    if isinstance(flow, dict):
        orders = [
            s.get("stepOrder")
            for s in _as_list(flow.get("steps"))
            if isinstance(s, dict) and s.get("stepOrder") is not None
        ]
        if len(orders) != len(set(orders)):
            v.append({"id": iid, "rule": "InteractionFlow.steps.stepOrder must be unique"})
        if orders:
            srt = sorted(orders)
            if srt != list(range(srt[0], srt[0] + len(srt))):
                v.append({"id": iid, "rule": "InteractionFlow.steps.stepOrder must be consecutive integers"})
    for c in _as_list(inst.get("costs")):
        if isinstance(c, dict) and c.get("currencyType") is not None and c.get("costType") != "Currency":
            v.append({"id": iid, "rule": "costs[].currencyType only meaningful when costType=Currency"})
            break
    return v


def _inv_ui(inst: dict) -> list[Violation]:
    v: list[Violation] = []
    iid = inst.get("id", "?")
    if inst.get("layerType") == "Modal" and inst.get("inputBlockingMode") != "FullBlock":
        v.append({"id": iid, "rule": "layerType=Modal requires inputBlockingMode=FullBlock"})
    for t in _as_list(inst.get("transitions")):
        if isinstance(t, dict):
            fs = t.get("fromScreenId")
            if fs is not None and fs != iid:
                v.append({"id": iid, "rule": "transitions[].fromScreenId must equal self id"})
                break
    bindings = [
        (b.get("source"), b.get("inputKey"), tuple(_as_list(b.get("modifiers"))))
        for b in _as_list(inst.get("inputBindings"))
        if isinstance(b, dict)
    ]
    seen: dict[tuple, int] = {}
    for b in _as_list(inst.get("inputBindings")):
        if not isinstance(b, dict):
            continue
        key = (b.get("source"), b.get("inputKey"), tuple(_as_list(b.get("modifiers"))))
        prio = b.get("priority")
        if key in seen:
            # duplicate key — require both to have priority
            if prio is None or seen[key] is None:
                v.append({"id": iid, "rule": "duplicate input binding requires priority on every entry"})
                break
        else:
            seen[key] = prio
    if inst.get("screenType") == "LoadingScreen":
        for b in _as_list(inst.get("inputBindings")):
            if isinstance(b, dict) and b.get("action") not in (None, "Cancel"):
                v.append({"id": iid, "rule": "LoadingScreen inputBindings only allow Cancel"})
                break
    if inst.get("screenType") == "Modal" and "cancelableByEscKey" not in inst:
        v.append({"id": iid, "rule": "screenType=Modal requires cancelableByEscKey defined"})
    flow = inst.get("NavigationFlow") or inst.get("navigationFlow")
    if isinstance(flow, dict):
        orders = [
            s.get("stepOrder")
            for s in _as_list(flow.get("steps"))
            if isinstance(s, dict) and s.get("stepOrder") is not None
        ]
        if orders:
            srt = sorted(orders)
            if srt != list(range(1, len(srt) + 1)):
                v.append({"id": iid, "rule": "NavigationFlow.steps.stepOrder must be consecutive 1..N"})
    for db in _as_list(inst.get("dataBindings")):
        if isinstance(db, dict):
            src = db.get("source")
            if isinstance(src, str) and src.startswith("Shop.") and inst.get("screenCategory") != "Shop":
                v.append({"id": iid, "rule": "dataBindings.source=Shop.* requires screenCategory=Shop"})
                break
    return v


INVARIANT_FNS = {
    "skill": _inv_skill,
    "state": _inv_state,
    "monster": _inv_monster,
    "item": _inv_item,
    "zone": _inv_zone,
    "quest": _inv_quest,
    "interaction": _inv_interaction,
    "ui": _inv_ui,
}


def check_invariants(instances: dict[str, list[dict]]) -> list[Violation]:
    out: list[Violation] = []
    for kind, items in instances.items():
        fn = INVARIANT_FNS.get(kind)
        if not fn:
            continue
        for inst in items:
            out.extend(fn(inst))
    return out


# ---------------------------------------------------------------------------
# Enum membership check (orthogonal to invariants)
# ---------------------------------------------------------------------------

def check_enum_membership(instances: dict[str, list[dict]]) -> list[dict]:
    problems: list[dict] = []
    for kind, items in instances.items():
        schema = SCHEMAS / SCHEMA_FILES.get(kind, "")
        axes = extract_axes(schema)
        if not axes:
            continue
        for inst in items:
            iid = inst.get("id", "?")
            for axis_name, values in axes.items():
                field = axis_name[0].lower() + axis_name[1:]
                if field not in inst:
                    continue
                for v in _as_list(inst.get(field)):
                    if v is None:
                        continue
                    if str(v) not in values:
                        problems.append(
                            {
                                "id": iid,
                                "field": field,
                                "value": v,
                                "allowed": values,
                            }
                        )
    return problems


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def write_index(payload: dict[str, Any]) -> None:
    INDEX.mkdir(exist_ok=True)
    (INDEX / "by-axis.json").write_text(
        json.dumps(payload["by_axis"], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (INDEX / "by-archetype.json").write_text(
        json.dumps(payload["by_archetype"], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (INDEX / "hubs.json").write_text(
        json.dumps(payload["hubs"], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def cmd_build_index(_args) -> int:
    inst = load_instances()
    idx = build_index(inst)
    write_index(idx)
    counts = {k: len(v) for k, v in inst.items() if v}
    print(f"indexed: {counts}")
    print(f"wrote: {INDEX}/by-axis.json, by-archetype.json, hubs.json")
    return 0


def cmd_check_refs(_args) -> int:
    inst = load_instances()
    probs = check_refs(inst)
    INDEX.mkdir(exist_ok=True)
    (INDEX / "ref-integrity.json").write_text(
        json.dumps(probs, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if probs:
        print(f"[FAIL] {len(probs)} dangling reference(s):")
        for p in probs[:20]:
            print(f"  {p['from']} @ {p['path']} -> {p['missingId']}  ({p['fromFile']})")
        return 1
    print("[OK] all references resolve")
    return 0


def cmd_check_coverage(_args) -> int:
    inst = load_instances()
    report = check_coverage(inst)
    INDEX.mkdir(exist_ok=True)
    (INDEX / "coverage.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    gaps = 0
    for kind, axes in report.items():
        for field, info in axes.items():
            if info["missing"]:
                gaps += len(info["missing"])
    print(f"[coverage] {gaps} axis-value(s) have zero instances - see index/coverage.json")
    return 0  # coverage is informational, not a failure


def cmd_check_invariants(_args) -> int:
    inst = load_instances()
    viols = check_invariants(inst)
    enum_probs = check_enum_membership(inst)
    INDEX.mkdir(exist_ok=True)
    (INDEX / "invariant-violations.json").write_text(
        json.dumps({"invariants": viols, "enum": enum_probs}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    fail = 0
    if viols:
        fail += len(viols)
        print(f"[FAIL] {len(viols)} invariant violation(s):")
        for v in viols[:20]:
            print(f"  {v['id']}: {v['rule']}")
    if enum_probs:
        fail += len(enum_probs)
        print(f"[FAIL] {len(enum_probs)} enum value(s) outside schema:")
        for p in enum_probs[:20]:
            print(f"  {p['id']}.{p['field']} = {p['value']!r} (allowed: {p['allowed']})")
    if not fail:
        print("[OK] no invariant or enum violations")
    return 1 if fail else 0


def cmd_list(args) -> int:
    inst = load_instances()
    kind = args.entity.rstrip("s")  # skills -> skill
    if kind not in inst:
        print(f"unknown entity: {args.entity}", file=sys.stderr)
        return 2
    for x in inst[kind]:
        print(x.get("id", "?"))
    return 0


def cmd_query(args) -> int:
    inst = load_instances()
    kind = args.entity.rstrip("s")
    if kind not in inst:
        print(f"unknown entity: {args.entity}", file=sys.stderr)
        return 2

    # --filter field=value  (equality; list fields match if any element equals)
    filters: list[tuple[str, str]] = []
    for f in args.filter or []:
        if "=" not in f:
            print(f"bad filter (need key=value): {f}", file=sys.stderr)
            return 2
        k, v = f.split("=", 1)
        filters.append((k, v))

    # --empty listField       (listField must be absent or length 0)
    empties: list[str] = args.empty or []

    # --missing-in listField.subField=value
    #   (list must not contain any element whose subField equals value)
    missings: list[tuple[str, str, str]] = []
    for m in args.missing_in or []:
        if "=" not in m or "." not in m.split("=", 1)[0]:
            print(
                f"bad --missing-in (need listField.subField=value): {m}",
                file=sys.stderr,
            )
            return 2
        lhs, val = m.split("=", 1)
        list_field, sub_field = lhs.split(".", 1)
        missings.append((list_field, sub_field, val))

    hits = []
    for item in inst[kind]:
        ok = True
        for k, v in filters:
            actual = item.get(k)
            if not any(str(x) == v for x in _as_list(actual)):
                ok = False
                break
        if ok:
            for fld in empties:
                if _as_list(item.get(fld)):
                    ok = False
                    break
        if ok:
            for list_field, sub_field, val in missings:
                entries = _as_list(item.get(list_field))
                if any(
                    isinstance(e, dict) and str(e.get(sub_field)) == val
                    for e in entries
                ):
                    ok = False
                    break
        if ok:
            hits.append(item.get("id"))
    for h in hits:
        print(h)
    return 0


def cmd_all(_args) -> int:
    rc = 0
    rc |= cmd_build_index(_args) << 0
    rc |= cmd_check_refs(_args) << 1
    rc |= cmd_check_invariants(_args) << 2
    rc |= cmd_check_coverage(_args) << 3
    return 1 if rc else 0


def main() -> int:
    p = argparse.ArgumentParser(prog="wiki-tool")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("build-index").set_defaults(func=cmd_build_index)
    sub.add_parser("check-refs").set_defaults(func=cmd_check_refs)
    sub.add_parser("check-coverage").set_defaults(func=cmd_check_coverage)
    sub.add_parser("check-invariants").set_defaults(func=cmd_check_invariants)
    sub.add_parser("all").set_defaults(func=cmd_all)

    pl = sub.add_parser("list")
    pl.add_argument("entity", help="skills | states | monsters | ...")
    pl.set_defaults(func=cmd_list)

    pq = sub.add_parser("query")
    pq.add_argument("entity")
    pq.add_argument("--filter", "-f", action="append", help="field=value, repeatable")
    pq.add_argument(
        "--empty",
        "-e",
        action="append",
        help="listField (must be absent or empty), repeatable",
    )
    pq.add_argument(
        "--missing-in",
        "-m",
        action="append",
        help="listField.subField=value (no element matches), repeatable",
    )
    pq.set_defaults(func=cmd_query)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
