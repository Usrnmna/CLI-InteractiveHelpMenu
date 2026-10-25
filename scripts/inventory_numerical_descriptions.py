"""Inventory numerical-description work without probing or changing the runtime.

Only repository data and literal syntax declarations are inspected. The existing
pure help parsers identify observations, not authoritative command grammars.
Review decisions live separately from generated facts and never affect the menu.
"""

import argparse
import ast
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import sys


TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(TOOL_ROOT / "cli_help"))
from discovery import clean_output, parse_help, parse_option_line
from core import HelpError, validate_profile


REVIEW_PATH = Path("docs/numerical-inventory/review.json")
ARTIFACT_KIND = "numerical_description_inventory"
# These owners can change the meaning retained, displayed, edited, or checked.
# Snapshot readers inspect their text; none of the inspected modules is imported.
PROTECTED_SOURCES = (
    "cli_help/core.py", "cli_help/discovery.py", "cli_help/drivers.py",
    "cli_help/arguments.py", "cli_help/ui.py", "cli_help/main.py",
    "bash/interactive-help.bash", "cli_help/value_semantics.py",
    "cli_help/presentation.py", "cli_help/authoring.py", "cli_help/manual_import.py",
    "cli_help/bulk_scan.py", "cli_help/review.py", "cli_help/review_forms.py",
    "cli_help/collection.py", "scripts/inventory_numerical_descriptions.py",
    "scripts/check_numerical_coverage.py", "tests/run.sh", ".github/workflows/ci.yml",
)
CLASSIFICATIONS = {
    "quantity", "count", "identifier_or_index", "level_or_enumeration",
    "timestamp_or_duration_expression", "composite", "delegated_value",
    "nonnumerical", "unresolved",
}
REVIEW_FIELDS = {
    "classification", "reason", "disposition", "deficiency", "evidence",
    "applicability", "references", "proposed_action", "priority", "findings",
    "later_steps", "verification", "acceptance",
}
WORD = re.compile(r"[A-Za-z0-9_.+-]+")
NUMERIC_HINT = re.compile(
    r"\b(?:N|NUM|COUNT|SIZE|RATE|TIME|DURATION|SECONDS|DEPTH|JOBS|LENGTH|HEIGHT|"
    r"integer|float|double|uint|int|timeout|bandwidth|bitrate|bytes|percent|"
    r"frequency|baud|priority|buffer|limit|offset)\b", re.IGNORECASE)


def encoded(document, pretty=False):
    """Serialize portable, deterministic JSON without generation timestamps."""
    return json.dumps(document, ensure_ascii=False, sort_keys=True,
                      indent=2 if pretty else None, separators=None if pretty else (",", ":")) + "\n"


def digest(document):
    """Fingerprint facts independently of presentation order and source offsets."""
    return hashlib.sha256(encoded(document).encode("utf-8")).hexdigest()


def review_context(value):
    """Exclude source offsets, but preserve ordered requests and semantic facts."""
    if isinstance(value, list):
        return [review_context(item) for item in value]
    if not isinstance(value, dict):
        return value
    result = {key: review_context(item) for key, item in value.items()
              if key not in ("pointer", "line", "text_line")}
    if isinstance(result.get("associations"), list):
        result["associations"].sort(key=encoded)
    return result


def unique_object(pairs):
    """Reject duplicate JSON keys instead of silently losing review decisions."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def words(value):
    """Accept literal path words, never pending command lines or shell syntax."""
    items = value.split() if isinstance(value, str) else value
    if isinstance(items, list) and items and all(isinstance(x, str) and WORD.fullmatch(x) for x in items):
        return tuple(items)
    return None


def literal(node):
    """Read a small set of AST literal shapes; never eval, compile, or call source.

    The two recognized wrappers are spelling conventions for literal collections:
    frozenset(literal) and a literal string followed by .split(). New expressions
    require an explicit reader update rather than executing repository source.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, int, bool, type(None))):
        return node.value
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return [literal(item) for item in node.elts]
    if isinstance(node, ast.Dict):
        return {literal(key): literal(value) for key, value in zip(node.keys, node.values)}
    if isinstance(node, ast.Call) and not node.keywords:
        if isinstance(node.func, ast.Name) and node.func.id == "frozenset" and len(node.args) == 1:
            return literal(node.args[0])
        if (isinstance(node.func, ast.Attribute) and node.func.attr == "split" and not node.args
                and isinstance(node.func.value, ast.Constant) and isinstance(node.func.value.value, str)):
            return node.func.value.value.split()
    raise ValueError(f"Unsupported literal declaration at line {getattr(node, 'lineno', '?')}")


class Inventory:
    """Collect source observations and their relationships without target access."""

    def __init__(self, root):
        self.root = Path(root).resolve(strict=True)
        self.sources = {}
        self.entries = {}
        self.contexts = {}
        self.bindings = defaultdict(list)
        self.counts = Counter()
        self.diagnostics = []

    def issue(self, code, location, message):
        """Record an actionable inventory problem, separate from numerical defects."""
        self.diagnostics.append({"code": code, "location": location, "message": message})

    def read(self, relative, role):
        """Read a regular UTF-8 file below the root, rejecting symlink traversal."""
        relative = Path(relative)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Source must be repository-relative: {relative}")
        path = self.root / relative
        resolved = path.resolve(strict=True)
        if self.root not in resolved.parents:
            raise ValueError(f"Source leaves the inspected root: {relative.as_posix()}")
        for part in (path, *path.parents):
            if part == self.root:
                break
            if part.is_symlink() or getattr(part, "is_junction", lambda: False)():
                raise ValueError(f"Linked input is not inspected: {relative.as_posix()}")
        if not path.is_file():
            raise ValueError(f"Missing regular input: {relative.as_posix()}")
        text = path.read_text(encoding="utf-8")
        name = relative.as_posix()
        source = self.sources.setdefault(name, {
            "path": name, "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "roles": [], "disposition": "enumerated; source content is not independent semantic proof",
        })
        if role not in source["roles"]:
            source["roles"].append(role)
        return text

    def files(self, relative):
        """Enumerate all maintained files without following linked directories."""
        folder = self.root / relative
        if not folder.is_dir():
            raise ValueError(f"Missing input directory: {relative}")
        def unreadable(error):
            raise error

        for parent, directories, names in os.walk(folder, followlinks=False, onerror=unreadable):
            for name in list(directories):
                path = Path(parent) / name
                if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
                    raise ValueError(f"Linked input directory: {path.relative_to(self.root).as_posix()}")
            for name in sorted(names):
                yield (Path(parent) / name).relative_to(self.root)

    def json(self, relative, role):
        """Load JSON with duplicate detection and a recorded source identity."""
        return json.loads(self.read(relative, role), object_pairs_hook=unique_object)

    def add(self, kind, command, name, source, role, **facts):
        """Merge observations by stable logical identity, preserving each source."""
        command = tuple(command or ())
        identity = "|".join((kind, " ".join(command), name))
        entry = self.entries.setdefault(identity, {
            "id": identity, "kind": kind, "command": list(command), "name": name, "observations": [],
        })
        if "context" in facts:
            context = facts.pop("context")
            context_id = digest(context)
            self.contexts[context_id] = context
            facts["context_id"] = context_id
        observation = {"source": source, "role": role, **facts}
        if observation not in entry["observations"]:
            entry["observations"].append(observation)
        return entry

    def route(self, command, source, origin, **facts):
        """Keep routing declarations distinct from descriptions and help requests."""
        return self.add("route", command, "", source, origin, **facts)

    def option(self, command, option, source, role, **facts):
        """Keep aliases separate while reconciling trailing-equals spellings."""
        flag = option["flag"]
        kind = "keyword" if option.get("kind") == "keyword" else "option"
        fields = {key: value for key, value in option.items() if key != "category"}
        # Complete text stays in the source; the inventory retains a labeled excerpt.
        if len(fields.get("detail", "")) > 600:
            fields["detail_sha256"] = hashlib.sha256(fields["detail"].encode("utf-8")).hexdigest()
            fields["detail"] = fields["detail"][:600]
            fields["detail_excerpt"] = True
        return self.add(kind, command, flag.rstrip("="), source, role, option=fields, **facts)

    def profiles(self):
        """Enumerate authored content, including descriptions and positional parts."""
        for path in sorted(self.files(Path("profiles"))):
            if path.suffix != ".json":
                self.read(path, "profile_directory_context")
                continue
            doc = self.json(path, "bundled_profile")
            validate_profile(doc, path)
            command = words(doc.get("command"))
            if not command:
                raise ValueError(f"Invalid profile command: {path}")
            self.counts["bundled_profiles"] += 1
            context = {key: doc[key] for key in ("documentation", "identity", "stop_at_positional", "stop_at_options") if key in doc}
            self.route(command, {"path": path.as_posix(), "pointer": "/command"}, "bundled_profile")
            self.add("profile_description", command, "", {"path": path.as_posix(), "pointer": "/description"},
                     "authored_description", description=doc.get("description", ""), context=context)
            definitions = doc.get("value_definitions", {})
            if not isinstance(definitions, dict):
                self.issue("inventory_value_definitions", path.as_posix(),
                           "Shared definitions must be a mapping; inspect the numerical structural diagnostics.")
                definitions = {}
            for name, definition in sorted(definitions.items()):
                self.counts["profile_value_definitions"] += 1
                pointer = "/value_definitions/" + name.replace("~", "~0").replace("/", "~1")
                self.add("value_definition", command, name, {"path": path.as_posix(), "pointer": pointer},
                         "authored_value_definition", definition=definition, context=context)
            for ci, category in enumerate(doc["categories"]):
                self.counts["profile_categories"] += 1
                self.add("category", command, category["name"], {"path": path.as_posix(), "pointer": f"/categories/{ci}"},
                         "authored_category", description=category.get("description", ""))
                for oi, option in enumerate(category["options"]):
                    self.counts["profile_option_records"] += 1
                    self.counts["profile_value_records"] += bool(option.get("argument"))
                    self.counts["profile_optional_value_records"] += bool(option.get("argument_optional"))
                    self.counts["profile_keyword_records"] += option.get("kind") == "keyword"
                    self.option(command, option, {"path": path.as_posix(), "pointer": f"/categories/{ci}/options/{oi}"},
                                "bundled_option", category=category["name"], context=context)
            group = doc.get("positional_group")
            if group:
                self.counts["profile_positional_groups"] += 1
                self.add("positional_group", command, "", {"path": path.as_posix(), "pointer": "/positional_group"},
                         "authored_positional_group", group=group,
                         value_semantics=doc.get("positional_value_semantics"), context=context)
                for index, component in enumerate(group["argument"].split()):
                    self.add("positional_component", command, component,
                             {"path": path.as_posix(), "pointer": "/positional_group"},
                             "authored_positional_component", component=index, group=group, context=context)

    def declarations(self, command, flags, source, role, value):
        """Record arity without implying that an option has displayed help text."""
        for flag in flags:
            self.option(command, {"flag": flag}, source, role, takes_value=value, display_content=False)

    def routing(self):
        """Read routing literals through AST without executing inspected snapshots."""
        path = Path("cli_help/command_paths.py")
        tree = ast.parse(self.read(path, "builtin_route_declarations"))
        declarations = {node.targets[0].id: node for node in tree.body
                        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)}
        globals_by_kind = {name: literal(declarations[name].value) for name in ("GLOBAL_VALUES", "GLOBAL_FLAGS")}
        for program in globals_by_kind["GLOBAL_VALUES"]:
            source = {"path": path.as_posix(), "line": declarations["GLOBAL_VALUES"].lineno}
            self.route((program,), source, "builtin_root")
            for suffix in ("COMMANDS", "GROUPS"):
                node = declarations.get(program.upper() + "_" + suffix)
                if node is None:
                    if suffix == "GROUPS":
                        continue
                    raise ValueError(f"Missing static {program} {suffix} declaration")
                values = literal(node.value)
                location = {"path": path.as_posix(), "line": node.lineno}
                if suffix == "COMMANDS":
                    for child in values:
                        self.route((program, child), location, "builtin_explicit")
                else:
                    for group, children in values.items():
                        self.route((program, group), location, "builtin_explicit")
                        for child in children.split():
                            self.route((program, group, child), location, "builtin_explicit")
            for field, values in globals_by_kind.items():
                self.declarations((program,), values[program], source, "builtin_global_arity", field == "GLOBAL_VALUES")
        for file in sorted(self.files(Path("config/drivers.example"))):
            if file.suffix != ".json":
                self.read(file, "driver_directory_context")
                continue
            doc = self.json(file, "example_driver")
            program = doc["command"]
            self.counts["example_driver_files"] += 1
            source = {"path": file.as_posix(), "pointer": ""}
            self.route((program,), source, "implicit_driver_root",
                       condition="default root retained by load_driver_files; explicit routes can replace its request")
            for field in ("global_values", "global_flags"):
                self.declarations((program,), doc.get(field, []), source, "driver_global_arity", field == "global_values")
            for index, route in enumerate(doc["paths"]):
                command = (program, *route["command"])
                location = {"path": file.as_posix(), "pointer": f"/paths/{index}"}
                self.counts["example_driver_route_records"] += 1
                self.route(command, location, "driver_explicit", request=route.get("help", []), manual=route.get("man"),
                           boundaries={key: route[key] for key in ("stop_at_options", "stop_at_positional") if key in route})
                for field in ("option_values", "option_flags"):
                    self.declarations(command, route.get(field, []), location, "parent_arity", field == "option_values")
        self.module_routes()

    def module_routes(self):
        """Enumerate bounded interpreter/module forms from literal allowlists."""
        path = Path("cli_help/invocation.py")
        tree = ast.parse(self.read(path, "module_route_declarations"))
        assignments = {node.targets[0].id: node for node in tree.body
                       if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)}
        child_paths = literal(assignments["PIP_MODULE_COMMANDS"].value)
        sets = [literal(node) for node in ast.walk(tree) if isinstance(node, ast.Set)
                and all(isinstance(x, ast.Constant) and isinstance(x.value, str) for x in node.elts)]
        modules = next((items for items in sets if "pip" in items and "pytest" in items), None)
        interpreters = next((items for items in sets if "python" in items and "python3" in items), None)
        if modules is None or interpreters is None:
            raise ValueError("Interpreter/module allowlist syntax requires inventory-reader review")
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "module_driver")
        returns = [node for node in ast.walk(function) if isinstance(node, ast.Return) and isinstance(node.value, ast.Call)]
        arities = [literal(arg) for node in returns if len(node.value.args) == 3 for arg in node.value.args[1:]]
        for interpreter in sorted(interpreters):
            for module in sorted(modules):
                source = {"path": path.as_posix(), "line": function.lineno}
                for child in [(), *((item,) for item in sorted(child_paths))] if module == "pip" else [()]:
                    self.route((interpreter, "-m", module, *child), source, "module_invocation")
                if module == "pip" and len(arities) == 2:
                    for index, flags in enumerate(arities):
                        self.declarations((interpreter, "-m", module), flags, source, "module_global_arity", index == 0)
        self.counts["interpreter_flag_forms"] = len(literal(assignments["INTERPRETER_FLAGS"].value))

    def owner(self, doc, hint):
        """Resolve explicit capture ownership; documentation labels are not routes."""
        request = next((doc[key] for key in ("request", "argv", "source") if isinstance(doc.get(key), list)), [])
        if "-m" in request:
            index = request.index("-m")
            tail = []
            for word in request[index + 1:]:
                if word in ("help", "--help", "-h"):
                    continue
                if word.startswith("-"):
                    break
                tail.append(word)
            # The capture does not establish which executable spelling selected it.
            return ("<selected-python>", "-m", *tail) if tail else None
        command = words(doc.get("command"))
        if command:
            return command
        known = {tuple(e["command"]) for e in self.entries.values() if e["kind"] == "route"}
        matches = [item for item in known if hint in (" ".join(item), "-".join(item))]
        if len(matches) == 1:
            return matches[0]
        prefix = []
        for word in request:
            if word in ("--help", "-h", "-help", "help") or not WORD.fullmatch(word):
                break
            prefix.append(word)
        if prefix and prefix[0] not in ("man", "python", "python3"):
            return tuple(prefix)
        return words(hint) if hint and hint not in ("cases", "captures", "provenance") else None

    def bind(self, file, command, context):
        """Associate text files with explicit manifest evidence, never filename guesses."""
        if not file:
            return
        if context not in self.bindings[(file.as_posix(), command)]:
            self.bindings[(file.as_posix(), command)].append(context)

    def referenced_file(self, relative, value):
        """Resolve manifest paths within the maintained fixture tree."""
        if not isinstance(value, str):
            raise ValueError(f"Invalid fixture reference in {relative}")
        candidates = (relative.parent / value, Path("tests/fixtures/help") / value, Path(value))
        for candidate in candidates:
            if not candidate.is_absolute() and ".." not in candidate.parts and (self.root / candidate).is_file():
                if candidate.parts[:3] != ("tests", "fixtures", "help"):
                    raise ValueError(f"Fixture reference leaves maintained fixture tree: {value}")
                return candidate
        self.issue("missing_fixture", relative.as_posix(), f"Referenced fixture is missing: {value}")
        return None

    def manifest(self, value, path, pointer="", hint=""):
        """Discover cases, captures, external-file references, and editing scenarios."""
        if isinstance(value, list):
            for index, child in enumerate(value):
                self.manifest(child, path, f"{pointer}/{index}", hint)
            return
        if not isinstance(value, dict):
            return
        location = {"path": path.as_posix(), "pointer": pointer}
        body_key = next((key for key in ("text", "output") if isinstance(value.get(key), str)), None)
        structured = body_key or "fixture" in value or "file" in value or isinstance(value.get("flags"), dict) or "before" in value
        if not structured:
            for key, child in value.items():
                if isinstance(child, (dict, list)):
                    escaped = key.replace("~", "~0").replace("/", "~1")
                    self.manifest(child, path, f"{pointer}/{escaped}", key)
            return
        command = self.owner(value, hint)
        context = {key: value[key] for key in (
            "version", "module_version", "interpreter_version", "kind", "provenance", "source_url", "reference",
            "normalization", "source", "request", "argv", "source_program", "source_arguments", "platform", "scope") if key in value}
        if isinstance(value.get("flags"), dict) and command:
            self.counts["matrix_expectation_records"] += 1
            primary = path.as_posix() == "tests/fixtures/help/matrix.json"
            self.counts["primary_matrix_cases"] += primary
            self.route(command, location, "primary_matrix" if primary else "supplementary_matrix",
                       excluded=value.get("excluded", []), sentinels=value.get("live_flags", []),
                       expectations={key: value[key] for key in (
                           "argument_counts", "live_argument_counts", "optional", "profile_sentinels",
                           "keyword_sentinels", "version_sentinels", "allow_empty", "profile_only",
                           "profile", "curated_profile", "documentation_path") if key in value}, context=context)
            for flag, argument in value["flags"].items():
                self.counts["primary_matrix_flag_expectations"] += primary
                option = {"flag": flag, "argument": argument}
                if flag in value.get("argument_counts", {}):
                    option["argument_count"] = value["argument_counts"][flag]
                if flag in value.get("optional", []):
                    option["argument_optional"] = True
                self.option(command, option, location,
                            "matrix_expectation", display_content=False, context=context)
            for version, expectations in value.get("version_sentinels", {}).items():
                for flag in expectations.get("flags", []):
                    fields = {"flag": flag}
                    if flag in expectations.get("argument_counts", {}):
                        fields["argument_count"] = expectations["argument_counts"][flag]
                    self.option(command, fields, location, "version_expectation", display_content=False,
                                version_key=version, context=context)
        if "before" in value:
            if command and value.get("flag"):
                self.option(command, {"flag": value["flag"]}, location, "editing_scenario", display_content=False)
            self.counts["editing_scenarios"] += 1
        for field in ("fixture", "file", "raw_capture"):
            if field in value:
                target = self.referenced_file(path, value[field])
                if target:
                    self.bind(target, command, {"manifest": location, "field": field, **context})
        if body_key:
            self.counts["embedded_help_sources"] += 1
            body_location = {"path": path.as_posix(), "pointer": pointer + "/" + body_key}
            self.help_text(value[body_key], command, body_location, "captured_help", context)

    def help_text(self, text, command, location, role, context):
        """Parse only supplied text, retaining parser limits and alias observations."""
        entries = parse_help(text, "inventory source")
        cleaned = clean_output(text).splitlines()
        declarations = defaultdict(list)
        for index, line in enumerate(cleaned, 1):
            parsed = parse_option_line(line)
            if parsed:
                aliases = [option["flag"] for option in parsed[0]]
                for flag in aliases:
                    declarations[flag.rstrip("=")].append((index, aliases))
        if not command and entries:
            self.issue("unassigned_help_source", location["path"], "Parsed options lack explicit command ownership; add a reviewed manifest association.")
        for option in entries:
            matches = declarations.get(option["flag"].rstrip("="), [])
            line, aliases = matches[0] if matches else (None, [])
            source = dict(location)
            if line:
                source["text_line" if "pointer" in location else "line"] = line
            owner = command or ("unassigned:" + location["path"],)
            option = dict(option)
            option.pop("category", None)
            option["detail"] = option.get("detail", "").removesuffix("\nSource: inventory source")
            self.option(owner, option, source, role, aliases=aliases, context=context)
            self.counts["parsed_help_option_observations"] += 1
        return len(entries)

    def fixtures(self):
        """Inspect every fixture input, not just matrix sentinels or named captures."""
        files = sorted(self.files(Path("tests/fixtures/help")))
        if Path("tests/fixtures/help/matrix.json") not in files:
            self.issue("missing_primary_matrix", "tests/fixtures/help/matrix.json", "The maintained compatibility matrix is missing.")
        for path in files:
            if path.suffix == ".json":
                self.manifest(self.json(path, "fixture_manifest"), path)
        for path in files:
            if path.suffix == ".txt":
                text = self.read(path, "maintained_help_text")
                bindings = [(command, contexts) for (name, command), contexts in self.bindings.items() if name == path.as_posix()]
                if not bindings:
                    bindings = [(None, [])]
                for command, contexts in bindings:
                    self.help_text(text, command, {"path": path.as_posix()}, "fixture_help", {"associations": contexts})
            elif path.suffix != ".json":
                self.read(path, "unrendered_manual" if path.suffix == ".1" else "fixture_context")

    def finish(self):
        """Freeze observations and reconcile explicit paths without additive totals."""
        for path in PROTECTED_SOURCES:
            self.read(Path(path), "protected_runtime_contract_context")
        for path in sorted(self.files(Path("tests/fixtures/value-semantics"))):
            self.read(path, "numerical_reference_fixture")
        for name, source in sorted(self.sources.items()):
            source["roles"].sort()
            self.add("source", (), name, {"path": name}, "input_source", roles=source["roles"], text_sha256=source["text_sha256"])
        for entry in self.entries.values():
            entry["observations"].sort(key=encoded)
            facts = []
            for observation in entry["observations"]:
                item = dict(observation)
                # Offsets can move when unrelated options are inserted or reordered.
                item["source"] = {"path": observation["source"]["path"]}
                if "context_id" in item:
                    context = self.contexts[item.pop("context_id")]
                    item["context_fingerprint"] = digest(review_context(context))
                facts.append(item)
            entry["fingerprint"] = digest(sorted(facts, key=encoded))
            text = " ".join(str(obs.get("option", {})) for obs in entry["observations"])
            entry["candidate_hints"] = sorted(set(NUMERIC_HINT.findall(text)))
            if entry["kind"] == "option":
                entry["numeric_fixed_spelling"] = bool(re.fullmatch(r"-\d+", entry["name"]))
            if entry["kind"] == "route":
                command = entry["command"]
                entry["has_explicit_children"] = any(other["kind"] == "route" and len(other["command"]) > len(command)
                                                     and other["command"][:len(command)] == command for other in self.entries.values())
                entry["maintained_option_content"] = any(other["kind"] in ("option", "keyword") and other["command"] == command
                    and any(obs["role"] in ("bundled_option", "fixture_help", "captured_help") for obs in other["observations"])
                    for other in self.entries.values())
        origins = defaultdict(set)
        for entry in self.entries.values():
            if entry["kind"] == "route":
                for observation in entry["observations"]:
                    origins[observation["role"]].add(tuple(entry["command"]))
        explicit = set().union(*(origins[key] for key in ("builtin_root", "builtin_explicit", "driver_explicit", "bundled_profile", "primary_matrix")))
        self.counts.update({
            "builtin_paths_including_roots": len(origins["builtin_root"] | origins["builtin_explicit"]),
            "explicit_named_path_union": len(explicit),
            "explicit_paths_outside_primary_matrix": len(explicit - origins["primary_matrix"]),
            "module_invocation_paths": len(origins["module_invocation"]),
            "implicit_driver_roots": len(origins["implicit_driver_root"]),
            "implicit_only_driver_roots": len(origins["implicit_driver_root"] - origins["driver_explicit"] - origins["builtin_root"]),
            "input_files": len(self.sources),
            "canonical_option_and_keyword_entries": sum(e["kind"] in ("option", "keyword") for e in self.entries.values()),
            "numeric_fixed_spelling_entries": sum(e.get("numeric_fixed_spelling", False) for e in self.entries.values()),
            "inventory_entries": len(self.entries),
        })
        return {"artifact_kind": ARTIFACT_KIND, "format_version": 1,
                "boundary": "Repository-only Step 1 planning inventory. Parser observations are not complete option grammars or verified numerical semantics. Generic discovery remains open-ended.",
                "counts": dict(sorted(self.counts.items())), "sources": list(self.sources.values()),
                "contexts": dict(sorted(self.contexts.items())),
                "entries": sorted(self.entries.values(), key=lambda item: item["id"]), "diagnostics": self.diagnostics}


def reconcile(report, reviews):
    """Attach explicit review groups and report missing, stale, or conflicting data.

    This validates inventory annotations only. It is not a production numerical
    metadata validator and does not interpret or reject target argument values.
    """
    if not isinstance(reviews, dict) or not isinstance(reviews.get("groups", []), list):
        raise ValueError("Review annotations require an object with a groups list")
    entries = {entry["id"]: entry for entry in report["entries"]}
    assignments = {}
    diagnostics = report["diagnostics"]
    groups = reviews.get("groups", [])
    group_ids = set()
    for group in groups:
        if not isinstance(group, dict) or not isinstance(group.get("entries", {}), dict):
            raise ValueError("Each review group requires an object with an entries map")
        group_id = group.get("id", "")
        if group_id in group_ids or not group_id:
            diagnostics.append({"code": "review_group_duplicate", "location": group_id, "message": "Review group IDs must be nonempty and unique."})
        group_ids.add(group_id)
        text_fields = ("reason", "disposition", "deficiency", "evidence", "applicability", "proposed_action", "priority", "verification", "acceptance")
        if (REVIEW_FIELDS - group.keys() or group.get("classification") not in CLASSIFICATIONS
                or any(not isinstance(group.get(key), str) or not group[key].strip() for key in text_fields)
                or any(not isinstance(group.get(key), list) for key in ("references", "findings", "later_steps"))):
            diagnostics.append({"code": "review_group_invalid", "location": group_id, "message": "Missing review fields or unsupported planning classification."})
        for identity, expected in group.get("entries", {}).items():
            if identity in assignments:
                diagnostics.append({"code": "review_duplicate", "location": identity, "message": f"Assigned by {assignments[identity]} and {group_id}."})
                previous = next(item for item in groups if item.get("id") == assignments[identity])
                if any(previous.get(field) != group.get(field) for field in REVIEW_FIELDS):
                    diagnostics.append({"code": "review_conflict", "location": identity, "message": "Duplicate assignments contain different decisions."})
            assignments[identity] = group_id
            if identity not in entries:
                diagnostics.append({"code": "review_orphan", "location": identity, "message": "Reviewed entry no longer exists."})
            elif expected != entries[identity]["fingerprint"]:
                diagnostics.append({"code": "review_stale", "location": identity, "message": "Source facts changed; reassess before updating its fingerprint."})
    for identity, entry in entries.items():
        entry["review_group"] = assignments.get(identity)
        if identity not in assignments:
            diagnostics.append({"code": "review_missing", "location": identity, "message": "New entry needs an explicit review disposition."})
    report["review_groups"] = [{key: value for key, value in group.items() if key != "entries"} for group in groups]
    report["acceptance_criteria"] = reviews.get("acceptance_criteria", [])
    report["system_work_items"] = reviews.get("system_work_items", [])
    report["review_summary"] = {
        "assigned_entries": sum(identity in assignments for identity in entries),
        "diagnostic_counts": dict(sorted(Counter(item["code"] for item in diagnostics).items())),
        "classifications": dict(sorted(Counter(group.get("classification", "invalid") for identity in entries
            for group in groups if group.get("id") == assignments.get(identity)).items())),
        "dispositions": dict(sorted(Counter(group.get("disposition", "invalid") for identity in entries
            for group in groups if group.get("id") == assignments.get(identity)).items())),
    }
    report["diagnostics"].sort(key=encoded)
    return report


def build_inventory(root, reviews=None):
    """Build facts from explicit repository sources; perform no output writes."""
    inventory = Inventory(root)
    inventory.profiles()
    inventory.routing()
    inventory.fixtures()
    return reconcile(inventory.finish(), {"groups": []} if reviews is None else reviews)


def write_output(root, output, report, review_file):
    """Write only an explicitly selected artifact; protect inputs and other files."""
    output = Path(output)
    for path in (output, *output.parents):
        if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
            raise ValueError("Output must not traverse a link")
    destination = output.resolve()
    protected = {(Path(root) / item["path"]).resolve() for item in report["sources"]}
    if destination in protected or destination == Path(review_file).resolve():
        raise ValueError("Output cannot replace an inspected source or review annotations")
    for relative in ("profiles", "cli_help", "config", "tests/fixtures/help", "scripts"):
        folder = (Path(root) / relative).resolve()
        if destination == folder or folder in destination.parents:
            raise ValueError("Output must be outside source input directories")
    if destination.exists():
        previous = json.loads(destination.read_text(encoding="utf-8"))
        if not isinstance(previous, dict) or previous.get("artifact_kind") != ARTIFACT_KIND:
            raise ValueError("Existing output is not an inventory artifact")
    destination.parent.mkdir(parents=True, exist_ok=True)
    # The human guide owns prose; compact JSON avoids duplicating a large corpus
    # as hundreds of thousands of formatted lines in a machine-facing artifact.
    destination.write_text(encoded(report), encoding="utf-8", newline="\n")


def main(argv=None):
    """Default to stdout; --output is the sole file-writing operation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=TOOL_ROOT, help="Repository snapshot to inspect")
    parser.add_argument("--reviews", type=Path, help="Separate curated review annotations")
    parser.add_argument("--output", type=Path, help="Explicit generated JSON destination; otherwise stdout only")
    parser.add_argument("--summary", action="store_true", help="Print counts and annotation diagnostic totals only")
    parser.add_argument("--check", action="store_true", help="Return failure for inventory/review reconciliation problems")
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve(strict=True)
        review_file = args.reviews or root / REVIEW_PATH
        reviews = json.loads(review_file.read_text(encoding="utf-8"), object_pairs_hook=unique_object) if review_file.exists() else {"groups": []}
        report = build_inventory(root, reviews)
        if args.output:
            write_output(root, args.output, report, review_file)
        print(encoded({"counts": report["counts"], "review_summary": report["review_summary"]} if args.summary else report, pretty=True), end="")
        return 1 if args.check and report["diagnostics"] else 0
    except (OSError, ValueError, KeyError, TypeError, SyntaxError, HelpError) as error:
        print(f"Inventory input/output error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
