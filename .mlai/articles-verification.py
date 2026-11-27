"""Reviewed customer-CI native verifier. Python stdlib + Playwright 1.58.0.

Repository commands receive only explicitly named environment values. Provider
credentials belong to the separate seal step, which never executes repository code.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
from importlib.metadata import version as package_version
import signal
import stat
import subprocess
import sys
import tempfile
import time
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

# BEGIN GENERATED PUBLISHING INPUT VALIDATOR
"""Portable input validator embedded verbatim into the reviewed native runner.

Only stdlib dependencies are permitted. The generated runner embeds its schema;
no repository-controlled helper participates in the verifier identity.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import PurePosixPath
import re
from urllib.parse import urlsplit

MAX_BYTES = 65536


class PublishingInputsError(ValueError):
    """A static error label without untrusted input contents."""


def canonical_bytes(value):
    """Finite UTF8 canonical JSON for the additive proof and input seal."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _shape(value, schema, document):
    """Validate the finite schema vocabulary without coercion or defaults."""
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/") or ref.count("/") != 2:
            return False
        return _shape(value, document["$defs"][ref.split("/")[-1]], document)
    if "anyOf" in schema and not any(_shape(value, child, document) for child in schema["anyOf"]):
        return False
    kinds = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool, "null": type(None)}
    if "type" in schema and type(value) is not kinds[schema["type"]]:
        return False
    if "const" in schema and (type(value) is not type(schema["const"]) or value != schema["const"]):
        return False
    if "enum" in schema and not any(type(value) is type(item) and value == item for item in schema["enum"]):
        return False
    if isinstance(value, dict):
        if set(schema.get("required", [])) - set(value) or len(value) > schema.get("maxProperties", 100):
            return False
        for key, item in value.items():
            child = schema.get("properties", {}).get(key, schema.get("additionalProperties", True))
            if child is False or isinstance(child, dict) and not _shape(item, child, document):
                return False
    elif isinstance(value, list):
        if not schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", 100):
            return False
        if any(not _shape(item, schema.get("items", {}), document) for item in value):
            return False
    elif isinstance(value, str):
        if not schema.get("minLength", 0) <= len(value) <= schema.get("maxLength", 4096):
            return False
        if "pattern" in schema and not re.fullmatch(schema["pattern"], value):
            return False
    elif type(value) is int:
        if not schema.get("minimum", -(2**63)) <= value <= schema.get("maximum", 2**63 - 1):
            return False
    return True


def _public_tree(value, *, depth=0, budget=None, argv=False):
    budget = [4000] if budget is None else budget
    budget[0] -= 1
    if depth > 16 or budget[0] < 0:
        raise PublishingInputsError("publishing_inputs_bounds")
    if isinstance(value, dict):
        if len(value) > 100:
            raise PublishingInputsError("publishing_inputs_bounds")
        for key, child in value.items():
            if (not isinstance(key, str) or len(key) > 100
                    or re.search(r"(?:^|_)(?:token|secret|password|credential|authorization|private_key|api_key)(?:$|_)", key, re.I)):
                raise PublishingInputsError("publishing_inputs_private_value")
            _public_tree(child, depth=depth + 1, budget=budget, argv=key == "command" or key.endswith("_command"))
    elif isinstance(value, list):
        if len(value) > 100:
            raise PublishingInputsError("publishing_inputs_bounds")
        for child in value:
            _public_tree(child, depth=depth + 1, budget=budget, argv=argv)
    elif isinstance(value, str):
        if len(value) > 4096 or any(ord(char) < 32 for char in value):
            raise PublishingInputsError("publishing_inputs_string")
        if re.search(r"https?://[^\s/@]+:[^\s/@]+@|github_pat_|gh[opsu]_[A-Za-z0-9]{16,}|sk-[A-Za-z0-9]{16,}|[?&](?:token|secret|api_key)=", value):
            raise PublishingInputsError("publishing_inputs_private_value")
        if argv and (re.search(r"(?:^|[\s=-])(?:authorization|password|token|api[-_]key|secret|private[-_]key)(?:[=:]|\s|$)", value, re.I)
                or re.search(r"(?:^|\s)[A-Z0-9_]*(?:TOKEN|PASSWORD|SECRET|API_KEY)\s*=", value, re.I)):
            raise PublishingInputsError("publishing_inputs_private_value")
    elif value is not None and type(value) not in {bool, int}:
        raise PublishingInputsError("publishing_inputs_scalar")


def _path(value, *, empty=False, slug=False, cwd=False):
    if empty and value == "":
        return
    expanded = value.replace("{slug}", "example") if slug else value
    if (not expanded or expanded == "." and not cwd or expanded != str(PurePosixPath(expanded)) or expanded.startswith("/")
            or any(part in {"..", ".git"} for part in expanded.split("/"))
            or "\\" in expanded or ":" in expanded or "{" in expanded or "}" in expanded):
        raise PublishingInputsError("publishing_inputs_path")


def _route(value, *, empty=False):
    if empty and value == "":
        return
    if (not value.startswith("/") or "//" in value or ".." in value.split("/") or "\\" in value
            or urlsplit(value).query or urlsplit(value).fragment):
        raise PublishingInputsError("publishing_inputs_route")


def _semantics(payload):
    target = payload["publishing"]["target"]
    verification = payload["verification"]
    execution, oracle = verification["execution"], verification["oracle"]
    react = target["kind"] == "react_article_system"
    if (target["delivery_adapter"] != ("react_component" if react else "stack_native")
            or target["registration_strategy"]["type"] != ("registry_seo_patch" if react else "stack_native_collection")
            or target["metadata_strategy"]["type"] != ("react_article_system" if react else "stack_native_collection")):
        raise PublishingInputsError("publishing_inputs_adapter")
    source = payload["publishing"]["source_selection"]
    if set(source) - {"branch", "app_root"} or "branch" in source and not source["branch"]:
        raise PublishingInputsError("publishing_inputs_source")
    if "app_root" in source:
        _path(source["app_root"], empty=True, cwd=True)
    if (target["runtime_family"] != execution["runtime_family"]
            or "app_root" in source and (source["app_root"] or ".") != execution["app_root"]
            or target["metadata_strategy"]["seo_path_template"] != target["route_template"]):
        raise PublishingInputsError("publishing_inputs_execution_mismatch")
    if target["kind"] == "stack_native_collection" and (
            canonical_bytes(target["metadata_strategy"]["static_source_materialization"]) != canonical_bytes(execution["static_source_materialization"])
            or target["registration_strategy"]["path"] != target["content_path_pattern"]):
        raise PublishingInputsError("publishing_inputs_materializer_mismatch")
    _path(target["content_path_pattern"], slug=True)
    _path(target["example_path"], empty=True)
    for key, value in target["registration_strategy"].items():
        if key.endswith("_path") or key == "path":
            _path(value, empty=key in {"author_registry_path", "author_alias_path"})
    for value in (target["route_template"], target["route_path"], target["metadata_strategy"]["seo_path_template"],
                  execution["route_template"], execution["listing_route"]):
        _route(value)
    for key in ("app_root", "install_cwd", "materialize_cwd", "build_cwd", "preview_cwd"):
        _path(execution[key], cwd=True)
    for path in execution["lockfiles"]:
        _path(path)
    if oracle["existing_seed_source"]:
        _path(oracle["existing_seed_source"]["path"])
    if "{slug}" not in execution["route_template"] or (execution["content_source_kind"] == "document_per_file" and "{slug}" not in execution["content_path_pattern"]):
        raise PublishingInputsError("publishing_inputs_slug")
    if (target["route_path"] != execution["listing_route"] or target["route_template"] != execution["route_template"]
            or target["content_path_pattern"] != execution["content_path_pattern"] or target["live_marker"]["value"] != oracle["artifact_digest"]):
        raise PublishingInputsError("publishing_inputs_mapping")
    routes = {execution["listing_route"], execution["route_template"].replace("{slug}", oracle["seed_slug"])}
    if set(oracle["artifact_marker_routes"]) - routes:
        raise PublishingInputsError("publishing_inputs_marker")
    commands = [execution[key] for key in ("install_command", "materialize_command", "build_command", "preview_command")]
    if not execution["build_command"] and not execution["verify_steps"]:
        raise PublishingInputsError("publishing_inputs_build")
    steps = list(execution["verify_steps"])
    baseline = execution["baseline"]
    if baseline["kind"] == "commands":
        commands.append(baseline["install_command"])
        _path(baseline["install_cwd"], cwd=True)
        steps.extend(baseline["verify_steps"])
    else:
        if execution["runtime_family"] != "static":
            raise PublishingInputsError("publishing_inputs_baseline")
        for path in baseline["paths"]:
            _path(path)
    for step in steps:
        commands.append(step["command"])
        _path(step["cwd"], cwd=True)
    static = execution["static_source_materialization"]
    if static:
        if (execution["runtime_family"] != "static" or static["materializer_command"] not in (execution["build_command"], execution["materialize_command"])
                or static["listing_source_path"].startswith(static["preview_output_dir"] + "/")
                or execution["content_path_pattern"].startswith(static["preview_output_dir"] + "/")
                or static["detail_source_path_pattern"] != str(PurePosixPath(static["listing_source_path"]).parent / "{slug}" / "index.html")):
            raise PublishingInputsError("publishing_inputs_materializer")
        for key in ("listing_source_path", "detail_source_path_pattern", "preview_output_dir"):
            _path(static[key], slug=key == "detail_source_path_pattern")
    if any(any(not arg for arg in command) for command in commands):
        raise PublishingInputsError("publishing_inputs_command")


def validate_execution_candidate(value, document):
    """Return an independent exact-shape candidate, without promoting any proof."""
    try:
        _public_tree(value)
        if len(canonical_bytes(value)) > MAX_BYTES or not _shape(value, document, document):
            raise ValueError("invalid_shape")
        _semantics(value["payload"])
        if hashlib.sha256(canonical_bytes(value["payload"])).hexdigest() != value["digest"]:
            raise ValueError("invalid_digest")
        return deepcopy(value)
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError):
        raise PublishingInputsError("publishing_inputs_candidate_invalid") from None


IDENTITY_FIELDS = frozenset({"repository_id", "github_repo", "website_connection_id", "connection_generation",
    "operation_id", "operation_attempt", "deletion_epoch", "target_id", "adapter_id", "adapter_version", "contract_digest"})
IDENTITY_INTEGERS = frozenset({"repository_id", "connection_generation", "operation_attempt", "deletion_epoch", "adapter_version"})
CHECK_FIELDS = frozenset({"content_loading", "listing", "detail", "unknown_slug_404", "canonical", "assets", "browser",
    "narrow_layout", "wide_layout"})
V3_FIELDS = IDENTITY_FIELDS | CHECK_FIELDS | {"schema_version", "source_sha", "source_tree_sha", "environment_fingerprint",
    "lockfile_digests", "artifact_digest", "baseline_build", "patched_build", "verified_routes", "evidence_digest",
    "publishing_inputs_digest", "baseline_source_sha", "verifier_sha256"}


def validate_execution_config(config, document, *, runner_sha256):
    """Bind every executable/oracle input before any subprocess or repository read."""
    try:
        allowed = {"schema_version", "execution_schema_version", "identity", "baseline_sha", "contract", "seed_slug",
            "seed_is_setup_example", "expected_h1", "artifact_digest", "port", "existing_seed_source",
            "artifact_marker_routes", "publishing_inputs_v1"}
        if type(config) is not dict or set(config) - allowed:
            raise ValueError("config_shape")
        if any(type(config.get(key)) is not int or config[key] != 1 for key in ("schema_version", "execution_schema_version")):
            raise ValueError("config_version")
        candidate = validate_execution_candidate(config["publishing_inputs_v1"], document)
        payload = candidate["payload"]
        target, verification = payload["publishing"]["target"], payload["verification"]
        identity = config["identity"]
        if type(identity) is not dict or set(identity) != IDENTITY_FIELDS:
            raise ValueError("identity_shape")
        for key in IDENTITY_INTEGERS:
            if type(identity[key]) is not int or identity[key] < (0 if key == "deletion_epoch" else 1):
                raise ValueError("identity_integer")
        if any(type(identity[key]) is not str or not 1 <= len(identity[key]) <= 500 for key in IDENTITY_FIELDS - IDENTITY_INTEGERS):
            raise ValueError("identity_string")
        if (not re.fullmatch(r"[a-f0-9]{64}", identity["contract_digest"])
                or identity["target_id"] != target["target_id"] or identity["adapter_id"] != target["delivery_adapter"]
                or identity["adapter_version"] != 1):
            raise ValueError("identity_target")
        execution = deepcopy(config["contract"])
        # The legacy generated native contract uses {} for absent materialization.
        if execution.get("static_source_materialization") == {}:
            execution["static_source_materialization"] = None
        for step in [*execution.get("verify_steps", []), *(execution.get("baseline") or {}).get("verify_steps", [])]:
            step.setdefault("name", "")
        if canonical_bytes(execution) != canonical_bytes(verification["execution"]):
            raise ValueError("execution_changed")
        oracle = verification["oracle"]
        for key, expected in oracle.items():
            actual = config.get(key)
            if key == "artifact_marker_routes" and key not in config:
                actual = [execution["listing_route"], execution["route_template"].replace("{slug}", oracle["seed_slug"])]
            if canonical_bytes(actual) != canonical_bytes(expected):
                raise ValueError("oracle_changed")
        if (config["baseline_sha"] != verification["baseline_policy"]["source_sha"]
                or runner_sha256 != verification["verifier"]["runner_sha256"]):
            raise ValueError("verifier_changed")
        return candidate
    except (KeyError, ValueError, TypeError, AttributeError, OverflowError, RecursionError):
        raise PublishingInputsError("publishing_inputs_execution_mismatch") from None


def validate_v3_receipt(proof):
    """Reject partial, coerced or unbounded schema3 results before sealing/consumption."""
    try:
        if type(proof) is not dict or set(proof) != V3_FIELDS or type(proof["schema_version"]) is not int or proof["schema_version"] != 3:
            raise ValueError("proof_shape")
        _public_tree(proof)
        if len(canonical_bytes(proof)) > MAX_BYTES:
            raise ValueError("proof_bounds")
        for key in IDENTITY_INTEGERS:
            if type(proof[key]) is not int or proof[key] < (0 if key == "deletion_epoch" else 1):
                raise ValueError("proof_integer")
        for key in IDENTITY_FIELDS - IDENTITY_INTEGERS:
            if type(proof[key]) is not str or not 1 <= len(proof[key]) <= 500:
                raise ValueError("proof_string")
        for key in CHECK_FIELDS:
            if proof[key] is not True:
                raise ValueError("proof_check")
        for key in ("source_sha", "source_tree_sha", "baseline_source_sha"):
            if type(proof[key]) is not str or not re.fullmatch(r"[a-f0-9]{40}(?:[a-f0-9]{24})?", proof[key]):
                raise ValueError("proof_source")
        for key in ("contract_digest", "environment_fingerprint", "publishing_inputs_digest", "verifier_sha256", "evidence_digest", "artifact_digest"):
            if type(proof[key]) is not str or not re.fullmatch(r"[a-f0-9]{64}", proof[key]):
                raise ValueError("proof_digest")
        if proof["baseline_build"] != "passed" or proof["patched_build"] != "passed":
            raise ValueError("proof_build")
        locks = proof["lockfile_digests"]
        if type(locks) is not dict or len(locks) > 20:
            raise ValueError("proof_locks")
        for name, digest in locks.items():
            _path(name)
            if type(digest) is not str or not re.fullmatch(r"[a-f0-9]{64}", digest):
                raise ValueError("proof_lock")
        routes = proof["verified_routes"]
        if type(routes) is not dict or set(routes) != {"listing", "detail", "unknown_slug"}:
            raise ValueError("proof_routes")
        for route in routes.values():
            if type(route) is not str or "{" in route or "}" in route:
                raise ValueError("proof_route")
            _route(route)
        if hashlib.sha256(canonical_bytes({key: value for key, value in proof.items() if key != "evidence_digest"})).hexdigest() != proof["evidence_digest"]:
            raise ValueError("proof_checksum")
        return deepcopy(proof)
    except (KeyError, ValueError, TypeError, OverflowError, RecursionError):
        raise PublishingInputsError("publishing_inputs_proof_invalid") from None


PUBLISHING_INPUT_SCHEMA = json.loads('{"$defs":{"BaselinePolicy":{"additionalProperties":false,"properties":{"kind":{"const":"fixed_setup_source","title":"Kind","type":"string"},"source_sha":{"pattern":"^[a-f0-9]{40}(?:[a-f0-9]{24})?$","title":"Source Sha","type":"string"}},"required":["kind","source_sha"],"title":"BaselinePolicy","type":"object"},"CommandBaseline":{"additionalProperties":false,"properties":{"install_command":{"items":{"maxLength":1000,"type":"string"},"maxItems":100,"title":"Install Command","type":"array"},"install_cwd":{"default":".","maxLength":1000,"title":"Install Cwd","type":"string"},"kind":{"const":"commands","title":"Kind","type":"string"},"verify_steps":{"items":{"$ref":"#/$defs/VerifyStep"},"maxItems":20,"minItems":1,"title":"Verify Steps","type":"array"}},"required":["kind","install_command","install_cwd","verify_steps"],"title":"CommandBaseline","type":"object"},"Execution":{"additionalProperties":false,"properties":{"app_root":{"default":".","maxLength":1000,"title":"App Root","type":"string"},"baseline":{"anyOf":[{"$ref":"#/$defs/CommandBaseline"},{"$ref":"#/$defs/StaticBaseline"}],"title":"Baseline"},"build_command":{"items":{"maxLength":1000,"type":"string"},"maxItems":100,"title":"Build Command","type":"array"},"build_cwd":{"default":".","maxLength":1000,"title":"Build Cwd","type":"string"},"content_path_pattern":{"maxLength":1000,"title":"Content Path Pattern","type":"string"},"content_source_kind":{"enum":["document_per_file","shared_collection"],"title":"Content Source Kind","type":"string"},"environment_names":{"items":{},"maxItems":0,"title":"Environment Names","type":"array"},"install_command":{"items":{"maxLength":1000,"type":"string"},"maxItems":100,"title":"Install Command","type":"array"},"install_cwd":{"default":".","maxLength":1000,"title":"Install Cwd","type":"string"},"listing_route":{"maxLength":1000,"title":"Listing Route","type":"string"},"lockfiles":{"items":{"maxLength":1000,"type":"string"},"maxItems":20,"title":"Lockfiles","type":"array"},"materialize_command":{"items":{"maxLength":1000,"type":"string"},"maxItems":100,"title":"Materialize Command","type":"array"},"materialize_cwd":{"default":".","maxLength":1000,"title":"Materialize Cwd","type":"string"},"package_manager":{"default":"","maxLength":1000,"title":"Package Manager","type":"string"},"preview_command":{"items":{"maxLength":1000,"type":"string"},"maxItems":100,"minItems":1,"title":"Preview Command","type":"array"},"preview_cwd":{"default":".","maxLength":1000,"title":"Preview Cwd","type":"string"},"route_template":{"maxLength":1000,"title":"Route Template","type":"string"},"runtime_family":{"enum":["node","python","static"],"title":"Runtime Family","type":"string"},"runtime_version":{"maxLength":1000,"title":"Runtime Version","type":"string"},"static_source_materialization":{"anyOf":[{"$ref":"#/$defs/StaticMaterialization"},{"type":"null"}],"default":null},"verify_steps":{"items":{"$ref":"#/$defs/VerifyStep"},"maxItems":20,"title":"Verify Steps","type":"array"}},"required":["app_root","runtime_family","runtime_version","package_manager","lockfiles","install_command","install_cwd","materialize_command","materialize_cwd","build_command","build_cwd","verify_steps","preview_command","preview_cwd","content_path_pattern","content_source_kind","route_template","listing_route","environment_names","baseline","static_source_materialization"],"title":"Execution","type":"object"},"Marker":{"additionalProperties":false,"properties":{"kind":{"const":"artifact_digest","title":"Kind","type":"string"},"meta_name":{"const":"mlai-artifact-digest","default":"mlai-artifact-digest","title":"Meta Name","type":"string"},"schema_version":{"const":1,"default":1,"title":"Schema Version","type":"integer"},"value":{"pattern":"^[a-f0-9]{64}$","title":"Value","type":"string"}},"required":["kind","value","meta_name","schema_version"],"title":"Marker","type":"object"},"Oracle":{"additionalProperties":false,"properties":{"artifact_digest":{"pattern":"^[a-f0-9]{64}$","title":"Artifact Digest","type":"string"},"artifact_marker_routes":{"items":{"maxLength":1000,"type":"string"},"maxItems":2,"minItems":1,"title":"Artifact Marker Routes","type":"array"},"existing_seed_source":{"anyOf":[{"$ref":"#/$defs/SourceWitness"},{"type":"null"}],"default":null},"expected_h1":{"maxLength":512,"minLength":1,"title":"Expected H1","type":"string"},"port":{"maximum":65535,"minimum":1024,"title":"Port","type":"integer"},"seed_is_setup_example":{"title":"Seed Is Setup Example","type":"boolean"},"seed_slug":{"maxLength":200,"minLength":1,"title":"Seed Slug","type":"string"}},"required":["seed_slug","seed_is_setup_example","expected_h1","artifact_digest","port","existing_seed_source","artifact_marker_routes"],"title":"Oracle","type":"object"},"Payload":{"additionalProperties":false,"properties":{"normalizer_version":{"const":1,"title":"Normalizer Version","type":"integer"},"publishing":{"$ref":"#/$defs/Publishing"},"verification":{"$ref":"#/$defs/Verification"}},"required":["normalizer_version","publishing","verification"],"title":"Payload","type":"object"},"Publishing":{"additionalProperties":false,"properties":{"source_selection":{"additionalProperties":false,"properties":{"app_root":{"maxLength":1000,"type":"string"},"branch":{"maxLength":1000,"minLength":1,"type":"string"}},"type":"object"},"target":{"$ref":"#/$defs/TargetInputs"}},"required":["target","source_selection"],"title":"Publishing","type":"object"},"ReactMetadata":{"additionalProperties":false,"properties":{"registry_slug_template":{"maxLength":1000,"title":"Registry Slug Template","type":"string"},"seo_path_template":{"maxLength":1000,"title":"Seo Path Template","type":"string"},"type":{"const":"react_article_system","title":"Type","type":"string"}},"required":["type","registry_slug_template","seo_path_template"],"title":"ReactMetadata","type":"object"},"ReactRegistration":{"additionalProperties":false,"properties":{"author_alias_path":{"default":"","maxLength":1000,"title":"Author Alias Path","type":"string"},"author_registry_path":{"default":"","maxLength":1000,"title":"Author Registry Path","type":"string"},"registry_path":{"maxLength":1000,"title":"Registry Path","type":"string"},"seo_config_path":{"maxLength":1000,"title":"Seo Config Path","type":"string"},"type":{"const":"registry_seo_patch","title":"Type","type":"string"}},"required":["type","registry_path","seo_config_path","author_registry_path","author_alias_path"],"title":"ReactRegistration","type":"object"},"SourceWitness":{"additionalProperties":false,"properties":{"path":{"maxLength":1000,"title":"Path","type":"string"},"sha256":{"pattern":"^[a-f0-9]{64}$","title":"Sha256","type":"string"}},"required":["path","sha256"],"title":"SourceWitness","type":"object"},"StaticBaseline":{"additionalProperties":false,"properties":{"kind":{"const":"static_source","title":"Kind","type":"string"},"paths":{"items":{"maxLength":1000,"type":"string"},"maxItems":100,"minItems":1,"title":"Paths","type":"array"}},"required":["kind","paths"],"title":"StaticBaseline","type":"object"},"StaticMaterialization":{"additionalProperties":false,"properties":{"app_root":{"const":"","title":"App Root","type":"string"},"detail_source_path_pattern":{"maxLength":1000,"title":"Detail Source Path Pattern","type":"string"},"listing_source_path":{"maxLength":1000,"title":"Listing Source Path","type":"string"},"materializer_command":{"items":{"maxLength":1000,"type":"string"},"maxItems":100,"title":"Materializer Command","type":"array"},"preview_output_dir":{"maxLength":1000,"title":"Preview Output Dir","type":"string"},"schema_version":{"const":1,"title":"Schema Version","type":"integer"}},"required":["schema_version","materializer_command","listing_source_path","detail_source_path_pattern","app_root","preview_output_dir"],"title":"StaticMaterialization","type":"object"},"StaticMetadata":{"additionalProperties":false,"properties":{"seo_path_template":{"maxLength":1000,"title":"Seo Path Template","type":"string"},"static_source_materialization":{"$ref":"#/$defs/StaticMaterialization"},"type":{"const":"stack_native_collection","title":"Type","type":"string"}},"required":["type","seo_path_template","static_source_materialization"],"title":"StaticMetadata","type":"object"},"StaticRegistration":{"additionalProperties":false,"properties":{"path":{"maxLength":1000,"title":"Path","type":"string"},"store_kind":{"const":"json_data_file","title":"Store Kind","type":"string"},"type":{"const":"stack_native_collection","title":"Type","type":"string"}},"required":["type","store_kind","path"],"title":"StaticRegistration","type":"object"},"TargetInputs":{"additionalProperties":false,"properties":{"build_tool":{"default":"unknown","maxLength":1000,"title":"Build Tool","type":"string"},"content_extension":{"default":"","maxLength":1000,"title":"Content Extension","type":"string"},"content_path_pattern":{"maxLength":1000,"title":"Content Path Pattern","type":"string"},"delivery_adapter":{"enum":["react_component","stack_native"],"title":"Delivery Adapter","type":"string"},"example_path":{"default":"","maxLength":1000,"title":"Example Path","type":"string"},"framework":{"default":"","maxLength":1000,"title":"Framework","type":"string"},"hook_config_path":{"const":"","default":"","title":"Hook Config Path","type":"string"},"input_format":{"const":"content_bundle_v1","default":"content_bundle_v1","title":"Input Format","type":"string"},"kind":{"enum":["react_article_system","stack_native_collection"],"title":"Kind","type":"string"},"language":{"default":"unknown","maxLength":1000,"title":"Language","type":"string"},"live_marker":{"$ref":"#/$defs/Marker"},"metadata_strategy":{"anyOf":[{"$ref":"#/$defs/ReactMetadata"},{"$ref":"#/$defs/StaticMetadata"}],"title":"Metadata Strategy"},"preferred_verifier_queue":{"default":"verify-static","maxLength":1000,"title":"Preferred Verifier Queue","type":"string"},"preview_discovery":{"default":null,"title":"Preview Discovery","type":"null"},"preview_strategy":{"const":"repo_preview","default":"repo_preview","title":"Preview Strategy","type":"string"},"publish_capability":{"const":"direct","default":"direct","title":"Publish Capability","type":"string"},"registration_strategy":{"anyOf":[{"$ref":"#/$defs/ReactRegistration"},{"$ref":"#/$defs/StaticRegistration"}],"title":"Registration Strategy"},"route_path":{"maxLength":1000,"title":"Route Path","type":"string"},"route_template":{"maxLength":1000,"title":"Route Template","type":"string"},"runtime_family":{"default":"unknown","maxLength":1000,"title":"Runtime Family","type":"string"},"supported":{"const":true,"default":true,"title":"Supported","type":"boolean"},"target_config":{"default":null,"title":"Target Config","type":"null"},"target_id":{"maxLength":200,"minLength":1,"title":"Target Id","type":"string"}},"required":["target_id","kind","supported","delivery_adapter","preview_strategy","content_path_pattern","route_template","metadata_strategy","registration_strategy","preview_discovery","framework","content_extension","example_path","runtime_family","language","build_tool","publish_capability","preferred_verifier_queue","hook_config_path","input_format","target_config","live_marker","route_path"],"title":"TargetInputs","type":"object"},"Verification":{"additionalProperties":false,"properties":{"baseline_policy":{"$ref":"#/$defs/BaselinePolicy"},"execution":{"$ref":"#/$defs/Execution"},"oracle":{"$ref":"#/$defs/Oracle"},"verifier":{"$ref":"#/$defs/Verifier"}},"required":["execution","oracle","baseline_policy","verifier"],"title":"Verification","type":"object"},"Verifier":{"additionalProperties":false,"properties":{"execution_schema_version":{"const":1,"title":"Execution Schema Version","type":"integer"},"playwright_version":{"const":"1.58.0","title":"Playwright Version","type":"string"},"profile":{"const":"native_ci_v1","title":"Profile","type":"string"},"python_version":{"pattern":"^\\\\d+\\\\.\\\\d+(?:\\\\.\\\\d+)?$","title":"Python Version","type":"string"},"runner_sha256":{"pattern":"^[a-f0-9]{64}$","title":"Runner Sha256","type":"string"}},"required":["profile","runner_sha256","execution_schema_version","python_version","playwright_version"],"title":"Verifier","type":"object"},"VerifyStep":{"additionalProperties":false,"properties":{"command":{"items":{"maxLength":1000,"type":"string"},"maxItems":100,"minItems":1,"title":"Command","type":"array"},"cwd":{"default":".","maxLength":1000,"title":"Cwd","type":"string"},"name":{"default":"","maxLength":1000,"title":"Name","type":"string"}},"required":["name","command","cwd"],"title":"VerifyStep","type":"object"}},"additionalProperties":false,"properties":{"canonicalization":{"const":"mlai_utf8_json_v1","title":"Canonicalization","type":"string"},"digest":{"pattern":"^[a-f0-9]{64}$","title":"Digest","type":"string"},"payload":{"$ref":"#/$defs/Payload"},"schema_version":{"const":1,"title":"Schema Version","type":"integer"}},"required":["schema_version","canonicalization","digest","payload"],"title":"Seal","type":"object"}')
# END GENERATED PUBLISHING INPUT VALIDATOR

CHECK_NAME = "MLAI articles native adapter verification"
# Vercel Analytics injects this optional same-origin loader, which only Vercel's
# edge serves: `next start` in CI answers 404 while every route renders. Mirrors
# harness.gate_classification.IGNORABLE_VERCEL_ANALYTICS_PATHS (path-exact; any
# other failed asset, including other `/_vercel/*` paths, still fails).
OPTIONAL_PLATFORM_ASSET_PATHS = {"/_vercel/insights/script.js"}
# Every link's resolved path, without trailing slashes, as the browser would follow it.
LINKED_PATHS_SCRIPT = r"""() => Array.from(document.querySelectorAll("a[href]"), (link) => {
  try { return new URL(link.href, document.baseURI).pathname.replace(/\/+$/, ""); } catch (error) { return ""; }
})"""
# La Vie (23 Oct 2026): a Cache Components detail route calls notFound() inside
# Suspense, after `next start` has flushed the shell with HTTP 200. Next then
# streams its not-found boundary with this digest and a noindex robots tag, and
# Vercel serves the same route as 404. Only that exact pair counts as not found.
NEXT_STREAMED_NOT_FOUND = "NEXT_HTTP_ERROR_FALLBACK;404"
NOINDEX_ROBOTS = re.compile(r'<meta\s+name="robots"\s+content="[^"]*\bnoindex\b', re.IGNORECASE)


def unknown_route_not_found(status, body):
    """HTTP 404, or Next's streamed not-found answer for an unknown article slug."""
    return status == 404 or (status == 200 and NEXT_STREAMED_NOT_FOUND in body and NOINDEX_ROBOTS.search(body) is not None)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha256(value):
    return hashlib.sha256(value).hexdigest()


def git_options():
    """The hosted proof controller reads only its selected workspace after uid changes."""
    return ["-c", "safe.directory="+str(Path.cwd())] if os.environ.get("CONTENT_FACTORY_SANDBOX_CHILD") == "1" else []


def git(*args):
    return subprocess.check_output(["git", *git_options(), *args], text=True).strip()


def child_environment(config):
    required = config["contract"].get("environment_names", [])
    if any(not os.environ.get(name) for name in required):
        raise ValueError("Declared build environment values are missing")
    return {"PATH": os.environ["PATH"], "HOME": str(Path.home()), "CI": "true",
            "PORT": str(config["port"]), "HOST": "127.0.0.1",
            **{name: os.environ[name] for name in required}}


def repository_options(cwd):
    """Hosted execution separates repository programs from the proof controller."""
    if os.environ.get("CONTENT_FACTORY_SANDBOX_CHILD") == "1":
        from harness.execution_sandbox import repository_process_options
        return repository_process_options(cwd)
    return {}


def run(command, cwd, env):
    if not command:
        raise ValueError("An explicit command is required")
    subprocess.run(command, cwd=cwd, env=env, check=True, timeout=900, **repository_options(cwd))


def lockfiles(root, contract):
    return {name: sha256((root / name).read_bytes()) for name in contract.get("lockfiles", [])}


def build(root, config, env, *, baseline=False):
    contract = config["contract"]
    before = lockfiles(root, contract)
    app_root = contract.get("app_root", ".")
    original = contract.get("baseline") if baseline else None
    if original and original["kind"] == "static_source":
        # The pristine static repository has no article materializer yet. This
        # is an explicit source smoke check, never a claim that the new build ran.
        from html.parser import HTMLParser
        for name in original["paths"]:
            path = static_path(root, name)
            if not path.is_file() or path.suffix.lower() not in {".html", ".htm"}:
                raise ValueError("Original static baseline source is missing")
            source = path.read_text()
            if not re.search(r"<html\b", source, re.I) or not re.search(r"<body\b", source, re.I):
                raise ValueError("Original static baseline is not an HTML document")
            HTMLParser().feed(source)
        return before
    execution = original or contract
    if execution.get("install_command"):
        run(execution["install_command"], root / execution.get("install_cwd", app_root), env)
    if not baseline and contract.get("materialize_command"):
        run(contract["materialize_command"], root / contract.get("materialize_cwd", app_root), env)
    steps = execution.get("verify_steps") or [{"command": execution.get("build_command"), "cwd": execution.get("build_cwd", app_root)}]
    for step in steps:
        run(step["command"], root / (step.get("cwd") or app_root), env)
    if lockfiles(root, contract) != before:
        raise ValueError("Frozen dependency inputs changed during verification")
    return before


def static_path(root, name, *, directory=False, missing=False):
    """Resolve regular static inputs/outputs without following symlink ancestors."""
    parts = PurePosixPath(name).parts
    if (not name or name == "." or name != str(PurePosixPath(name)) or name.startswith("/") or "\\" in name
            or any(part in {"..", ".git"} or part.startswith(".env") for part in parts)
            or any(ord(char) < 32 for char in name)):
        raise ValueError("Static paths must be canonical, nonreserved repository paths")
    base = root.resolve()
    path = base
    for index, part in enumerate(parts):
        path = path / part
        if not path.exists() and not path.is_symlink():
            if missing:
                continue
            raise ValueError("A declared static path is missing")
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode) or (index < len(parts) - 1 and not stat.S_ISDIR(mode)):
            raise ValueError("Static paths cannot contain symlinks or non-directory ancestors")
    if not path.resolve().is_relative_to(base):
        raise ValueError("Static path escapes the repository")
    if path.exists():
        mode = path.lstat().st_mode
        if not (stat.S_ISDIR(mode) if directory else stat.S_ISREG(mode)):
            raise ValueError("Declared static paths require regular files/directories")
    return path


def static_inventory(root):
    """Snapshot all source files, including ignored additions, without following links."""
    result = {}
    for parent, directories, files in os.walk(root, followlinks=False):
        directories[:] = [name for name in directories if name != ".git" or Path(parent) != root]
        for name in [*directories, *files]:
            path = Path(parent) / name
            if name == ".git" and Path(parent) == root:
                continue
            mode = path.lstat().st_mode
            if stat.S_ISREG(mode):
                content = sha256(path.read_bytes())
            elif stat.S_ISLNK(mode):
                content = os.readlink(path)
            elif stat.S_ISDIR(mode):
                content = None
            else:
                raise ValueError("Static source contains an unsupported filesystem entry")
            result[path.relative_to(root).as_posix()] = (mode, content)
    return result


def validate_static_outputs(root, config, allowed, before):
    """Check actual source HTML, modes and the complete materialized output tree."""
    static = config["contract"].get("static_source_materialization") or {}
    if not static:
        return
    static_path(root, config["contract"]["content_path_pattern"])
    for name in allowed:
        path = static_path(root, name)
        if path.lstat().st_mode & 0o111:
            raise ValueError("Generated static HTML cannot acquire executable permissions")
    output = static_path(root, static["preview_output_dir"], directory=True)
    for parent, directories, files in os.walk(output, followlinks=False):
        for name in directories:
            static_path(root, (Path(parent) / name).relative_to(root).as_posix(), directory=True)
        for name in files:
            static_path(root, (Path(parent) / name).relative_to(root).as_posix())
    after = static_inventory(root)
    prefix = static["preview_output_dir"].rstrip("/") + "/"
    for name in set(before) | set(after):
        if before.get(name) == after.get(name):
            continue
        if name in before and name in after and before[name][0] != after[name][0]:
            raise ValueError("Static materialization changed source filesystem modes")
        if name in allowed or name == prefix[:-1] or name.startswith(prefix):
            continue
        # Exact declared source files may create their necessary parent dirs.
        if name not in before and name in after and stat.S_ISDIR(after[name][0]) and any(path.startswith(name + "/") for path in allowed):
            continue
        raise ValueError("Repository commands changed or added files outside declared static outputs")


def declared_static_outputs(root, config):
    """Allow only declared HTML outputs for slugs in the immutable input collection."""
    contract = config["contract"]
    static = contract.get("static_source_materialization") or {}
    if not static:
        return set()
    static_path(root, static["listing_source_path"])
    static_path(root, static["preview_output_dir"], directory=True, missing=True)
    existing = config.get("existing_seed_source") or {}
    existing_detail = ""
    if existing:
        expected_detail = static["detail_source_path_pattern"].replace("{slug}", config["seed_slug"])
        if (set(existing) != {"path", "sha256"} or existing.get("path") != expected_detail
                or not re.fullmatch(r"[a-f0-9]{64}", str(existing.get("sha256") or ""))
                or sha256(static_path(root, expected_detail).read_bytes()) != existing["sha256"]):
            raise ValueError("The pinned existing detail source differs from its reviewed witness")
        existing_detail = expected_detail
    records = json.loads(static_path(root, contract["content_path_pattern"]).read_text())
    if not isinstance(records, list) or (not records and not existing) or any(not isinstance(record, dict) for record in records):
        raise ValueError("Static materialization requires a reviewed JSON-array collection")
    slugs = [record.get("slug") for record in records]
    if (any(not isinstance(slug, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", slug) for slug in slugs)
            or len(set(slugs)) != len(slugs)):
        raise ValueError("Static outputs require exact collection slugs including the seed")
    writable = []
    for record in records:
        if record.get("source") == "existing" or record.get("managed") is False:
            # Markers deny writes, rather than grant source ownership. A
            # captured detail must already exist; materializers cannot recreate
            # it as a new generated output or silently drop its source.
            static_path(root, static["detail_source_path_pattern"].replace("{slug}", record["slug"]))
        else:
            writable.append(record["slug"])
    if not existing and config["seed_slug"] not in writable:
        raise ValueError("Static outputs require a generated seed or a pinned existing witness")
    # Read-only adopted articles are source witnesses, never writable generated
    # outputs, including when a future registry capture points at this detail.
    outputs = {static["listing_source_path"], *(static["detail_source_path_pattern"].replace("{slug}", slug) for slug in writable)}
    return outputs - ({existing_detail} if existing_detail else set())


def optional_platform_asset(base, url):
    parts, origin = urlsplit(url), urlsplit(base)
    return (parts.scheme, parts.netloc) == (origin.scheme, origin.netloc) and parts.path in OPTIONAL_PLATFORM_ASSET_PATHS


def browser_proof(base, config):
    from playwright.sync_api import sync_playwright
    contract = config["contract"]
    listing = contract["listing_route"]
    detail = contract["route_template"].replace("{slug}", config["seed_slug"])
    if "{" in detail:
        raise ValueError("Every route placeholder needs a concrete reviewed value")
    errors, assets = [], []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("response", lambda response: assets.append(response.url) if response.status >= 400 and response.request.resource_type in {"script", "stylesheet", "image", "font"}
                and not optional_platform_asset(base, response.url) else None)
        for width in (1440, 390):
            page.set_viewport_size({"width": width, "height": 900})
            for route in (listing, detail):
                response = page.goto(base + route, wait_until="networkidle", timeout=60000)
                if response is None or response.status != 200:
                    raise ValueError("An article route did not return HTTP 200")
                if not page.locator("h1").count():
                    raise ValueError("An article route has no heading")
                setup_example = config.get("seed_is_setup_example") is True
                if (route == detail or not setup_example) and config["expected_h1"] not in page.locator("body").inner_text():
                    raise ValueError("The listing/detail did not load the seeded article")
                if route == detail and config["expected_h1"] not in page.locator("h1").first.inner_text():
                    raise ValueError("The detail route did not render the seeded heading")
                canonical_url = page.locator('link[rel="canonical"]').first.get_attribute("href") if page.locator('link[rel="canonical"]').count() else None
                if not canonical_url or urlsplit(canonical_url).path.rstrip("/") != route.rstrip("/"):
                    raise ValueError("Canonical route differs from the rendered article")
                marker = page.locator('meta[name="mlai-artifact-digest"]')
                marker_required = route in config.get("artifact_marker_routes", [listing, detail])
                if config.get("artifact_digest") and marker_required and (not marker.count() or marker.first.get_attribute("content") != config["artifact_digest"]):
                    raise ValueError("The rendered artifact differs from the reviewed integration")
                if not page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 2"):
                    raise ValueError("Article layout overflows its viewport")
                if route == listing:
                    # Compare link paths as a browser resolves them. A static listing can link
                    # its stories relatively with a trailing slash (TalaThrive: href="slug/").
                    seed_linked = detail.rstrip("/") in set(page.evaluate(LINKED_PATHS_SCRIPT))
                    if setup_example:
                        if seed_linked or config["expected_h1"] in page.locator("body").inner_text():
                            raise ValueError("A setup example leaked into the public listing")
                    elif not seed_linked:
                        raise ValueError("The listing does not link to the seeded detail")
                if route == detail and setup_example:
                    robots = page.locator('head meta[name="robots"]')
                    if not robots.count() or not {"noindex", "none"}.intersection(re.split(r"[,\s]+", (robots.first.get_attribute("content") or "").lower())):
                        raise ValueError("A setup example detail must be noindex")
        missing = contract["route_template"].replace("{slug}", "mlai-nonexistent-" + (config.get("artifact_digest") or config["identity"]["contract_digest"])[:12])
        unknown = page.request.get(base + missing)
        if not unknown_route_not_found(unknown.status, unknown.text() if unknown.status == 200 else ""):
            raise ValueError("An unknown article slug does not return HTTP 404")
        browser.close()
    if errors or assets:
        detail = [f"page error: {error.splitlines()[0][:200]}" for error in errors[:5]]
        detail += [f"failed asset: {urlsplit(url).path[:200]}" for url in sorted(set(assets))[:5]]
        raise ValueError("Browser errors or required asset failures occurred: " + "; ".join(detail))
    return {**{key: True for key in ("content_loading", "listing", "detail", "unknown_slug_404", "canonical", "assets", "browser", "narrow_layout", "wide_layout")},
            "verified_routes": {"listing": listing, "detail": detail, "unknown_slug": missing}}


def verify(config, output):
    if os.environ.get("MLAI_SEAL_TOKEN") or os.environ.get("GITHUB_TOKEN"):
        raise ValueError("Provider credentials must be confined to the separate sealing step")
    candidate = None
    runner_digest = sha256(Path(__file__).read_bytes())
    if "publishing_inputs_v1" in config:
        candidate = validate_execution_config(config, PUBLISHING_INPUT_SCHEMA, runner_sha256=runner_digest)
        declared_python = candidate["payload"]["verification"]["verifier"]["python_version"]
        if not (platform.python_version() == declared_python or platform.python_version().startswith(declared_python + ".")):
            raise ValueError("Verifier Python differs from the frozen execution profile")
    root = Path.cwd()
    source = git("rev-parse", "HEAD")
    tree = git("rev-parse", "HEAD^{tree}")
    if git("status", "--porcelain"):
        raise ValueError("Verification requires the exact clean repository source")
    identity = config["identity"]
    if identity.get("adapter_id") == "custom_contract_v1" and sha256(canonical(config["contract"])) != identity.get("contract_digest"):
        raise ValueError("CI commands differ from the reviewed canonical custom contract")
    if identity.get("adapter_id") == "custom_contract_v1" and (config.get("artifact_digest") or None) != config["contract"].get("artifact_digest"):
        raise ValueError("Custom live marker differs from the reviewed canonical contract")
    if os.environ.get("GITHUB_REPOSITORY", identity["github_repo"]) != identity["github_repo"]:
        raise ValueError("CI repository differs from the reviewed binding")
    if int(os.environ.get("GITHUB_REPOSITORY_ID", identity["repository_id"])) != identity["repository_id"]:
        raise ValueError("CI repository identity differs from the reviewed binding")
    env = child_environment(config)
    allowed_outputs = declared_static_outputs(root, config)
    source_inventory = static_inventory(root) if allowed_outputs else {}
    with tempfile.TemporaryDirectory(prefix="mlai-baseline-") as temporary:
        baseline = Path(temporary) / "source"
        subprocess.run(["git", *git_options(), "worktree", "add", "--detach", str(baseline), config["baseline_sha"]], check=True)
        try:
            baseline_source = subprocess.check_output(["git", "-c", "safe.directory=" + str(baseline), "-C", str(baseline), "rev-parse", "HEAD"], text=True).strip() if candidate else None
            if candidate and baseline_source != config["baseline_sha"]:
                raise ValueError("Baseline checkout differs from the frozen setup source")
            build(baseline, config, env, baseline=True)
        finally:
            subprocess.run(["git", *git_options(), "worktree", "remove", "--force", str(baseline)], check=True)
    locks = build(root, config, env)
    validate_static_outputs(root, config, allowed_outputs, source_inventory)
    preview = config["contract"]["preview_command"]
    preview_cwd = root / config["contract"].get("preview_cwd", config["contract"].get("app_root", "."))
    process = subprocess.Popen(preview, cwd=preview_cwd, env=env, start_new_session=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **repository_options(preview_cwd))
    base = "http://127.0.0.1:" + str(config["port"])
    try:
        for _ in range(60):
            if process.poll() is not None:
                raise ValueError("The declared preview command exited before verification")
            try:
                with urlopen(base + config["contract"]["listing_route"], timeout=1):
                    break
            except OSError:
                time.sleep(1)
        else:
            raise ValueError("The preview did not become ready")
        checks = browser_proof(base, config)
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
    # Reject file type/executable-bit changes even on permitted generated HTML.
    if any(line.split()[0].lstrip(":") != line.split()[1] for line in git("diff", "--raw", "HEAD").splitlines()):
        raise ValueError("Repository commands changed tracked source filesystem modes")
    changed = git("diff", "--name-only", "HEAD").splitlines()
    if set(changed) - allowed_outputs:
        raise ValueError("Repository commands changed tracked source outside declared static HTML outputs")
    validate_static_outputs(root, config, allowed_outputs, source_inventory)
    runtime = config["contract"]["runtime_family"]
    python_runtime = ["python3" if config.get("execution_schema_version") == 1 else sys.executable, "--version"]
    command = {"node": ["node", "--version"], "python": python_runtime, "static": python_runtime if config.get("execution_schema_version") == 1 else None, "ruby": ["ruby", "--version"], "php": ["php", "--version"], "go": ["go", "version"]}.get(runtime)
    runtime_output = subprocess.check_output(command, text=True).strip() if command else platform.python_version()
    runtime_match = re.search(r"(?:^|[^0-9])(\d+\.\d+(?:\.\d+)?)", runtime_output)
    declared = config["contract"]["runtime_version"].removeprefix("v")
    if command and (not runtime_match or not (runtime_match[1] == declared or runtime_match[1].startswith(declared + "."))):
        raise ValueError("Observed runtime differs from the reviewed version constraint")
    playwright_version = package_version("playwright")
    if playwright_version != "1.58.0":
        raise ValueError("Install the reviewed Playwright 1.58.0 verifier dependency")
    manager = config["contract"].get("package_manager") or ""
    manager_output = ""
    if runtime == "node" and manager:
        manager_name, _, expected_manager_version = manager.partition("@")
        manager_output = subprocess.check_output([manager_name, "--version"], text=True).strip()
        if expected_manager_version and manager_output != expected_manager_version:
            raise ValueError("Observed dependency manager differs from the reviewed exact version")
    environment = {"platform": platform.platform(), "runtime": runtime_output, "dependency_manager": manager_output, "python": platform.python_version(), "playwright": playwright_version}
    proof = {**identity, "schema_version": 2, "source_sha": source, "source_tree_sha": tree,
             "environment_fingerprint": sha256(canonical(environment)), "lockfile_digests": locks, "artifact_digest": config.get("artifact_digest") or None,
             "baseline_build": "passed", "patched_build": "passed", **checks}
    encoding = canonical
    if candidate:
        proof.update(schema_version=3, publishing_inputs_digest=candidate["digest"],
                     baseline_source_sha=baseline_source, verifier_sha256=runner_digest)
        encoding = canonical_bytes
    proof["evidence_digest"] = sha256(encoding(proof))
    if candidate:
        validate_v3_receipt(proof)
    Path(output).write_bytes(encoding(proof))


def seal(path):
    proof = json.loads(Path(path).read_text())
    if proof.get("schema_version") == 3:
        validate_v3_receipt(proof)
    encoding = canonical_bytes if proof.get("schema_version") == 3 else canonical
    expected = proof.pop("evidence_digest")
    if sha256(encoding(proof)) != expected:
        raise ValueError("Verifier receipt checksum differs")
    proof["evidence_digest"] = expected
    if proof["github_repo"] != os.environ["GITHUB_REPOSITORY"]:
        raise ValueError("Provider repository differs from verifier receipt")
    payload = {"name": CHECK_NAME, "head_sha": proof["source_sha"], "status": "completed", "conclusion": "success",
               "output": {"title": CHECK_NAME, "summary": "MLAI_ARTICLES_ATTESTATION:" + base64.b64encode(encoding(proof)).decode()}}
    request = Request("https://api.github.com/repos/" + proof["github_repo"] + "/check-runs", data=canonical(payload), method="POST",
                      headers={"Authorization": "Bearer " + os.environ["MLAI_SEAL_TOKEN"], "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})
    with urlopen(request, timeout=30) as response:
        receipt = json.load(response)
    Path("mlai-provider-receipt.json").write_bytes(canonical({"check_run_id": receipt["id"], "source_sha": proof["source_sha"], "evidence_digest": expected}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["verify", "seal"])
    parser.add_argument("--config", default=".mlai/articles-verification.json")
    parser.add_argument("--evidence", default="mlai-native-evidence.json")
    args = parser.parse_args()
    if args.action == "verify":
        verify(json.loads(Path(args.config).read_text()), args.evidence)
    else:
        seal(args.evidence)
