"""Schema grader -- deterministic contract validation against
packages/contracts/tool_contracts/*.schema.json.

Hand-rolled minimal validator (type / required / additionalProperties /
enum / const), same choice V2 made in its own schema_grader.py ("reuses a
hand-rolled validator... not a copy") -- avoids taking an unpinned
`jsonschema` dependency in a repo with no packaging yet (Stage 20's job).
Covers the subset our contracts actually use; not a general JSON Schema
implementation.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_DIR = ROOT / "packages" / "contracts" / "tool_contracts"


def _validate(value, schema, path="$"):
    errors = []
    t = schema.get("type")
    if t == "object":
        if not isinstance(value, dict):
            return [f"{path}: expected object"]
        props = schema.get("properties", {})
        for req in schema.get("required", []):
            if req not in value:
                errors.append(f"{path}: missing required property {req!r}")
        if schema.get("additionalProperties") is False:
            extra = set(value.keys()) - set(props.keys())
            if extra:
                errors.append(f"{path}: additionalProperties violation: {sorted(extra)}")
        for k, v in value.items():
            if k in props:
                errors.extend(_validate(v, props[k], f"{path}.{k}"))
    elif t == "array":
        if not isinstance(value, list):
            return [f"{path}: expected array"]
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: fewer than minItems={schema['minItems']}")
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(value):
                errors.extend(_validate(item, item_schema, f"{path}[{i}]"))
    elif t == "string":
        if not isinstance(value, str):
            errors.append(f"{path}: expected string")
        elif "enum" in schema and value not in schema["enum"]:
            errors.append(f"{path}: {value!r} not in enum {schema['enum']}")
    elif t == "integer":
        if not isinstance(value, int) or isinstance(value, bool):
            errors.append(f"{path}: expected integer")
        elif "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: below minimum {schema['minimum']}")
    elif t in ("number",):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(f"{path}: expected number")
    elif t == "boolean":
        if not isinstance(value, bool):
            errors.append(f"{path}: expected boolean")

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: {value!r} != const {schema['const']!r}")

    if "anyOf" in schema:
        # union-of-types (used for nullable fields, e.g. ["string", "null"])
        pass

    return errors


def load_schema(relative_path):
    """relative_path like 'batch_reconcile.schema.json#/output', or the
    same with a full repo-relative prefix (packages/contracts/tool_contracts/...)
    -- only the filename is used, since CONTRACTS_DIR already points there."""
    file_part, _, pointer = relative_path.partition("#")
    filename = Path(file_part).name
    doc = json.loads((CONTRACTS_DIR / filename).read_text(encoding="utf-8"))
    if pointer:
        node = doc
        for part in pointer.strip("/").split("/"):
            node = node[part]
        return node
    return doc


def grade_schema(response, schema_ref):
    """schema_ref: e.g. 'batch_reconcile.schema.json#/output', or an
    already-loaded schema dict (for abstention_contract / non-file refs,
    which don't correspond to a Stage-11 tool contract)."""
    if isinstance(schema_ref, dict):
        schema = schema_ref
    elif schema_ref in ("abstention_contract",):
        # Not a Stage-11 tool schema -- abstention is a terminal-state shape
        # shared across all three graphs (langgraph_design.md), not a tool
        # output. Minimal inline contract, kept here rather than inventing
        # a file this stage doesn't otherwise need.
        schema = {
            "type": "object",
            "required": ["terminal_state", "abstention_reason"],
            "properties": {
                "terminal_state": {"type": "string", "enum": ["abstained"]},
                "abstention_reason": {"type": "string"},
            },
            "additionalProperties": True,
        }
    else:
        schema = load_schema(schema_ref)
    errors = _validate(response, schema)
    reason = "schema_valid" if not errors else "; ".join(errors)
    return {"pass": not errors, "reason": reason, "errors": errors}
