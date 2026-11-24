"""Read documented option tables emitted by cloud and embedded command-line clients."""

from bisect import bisect_right
import re


# Azure's column layouts omit metavariables. These effects on the three reviewed
# leaf routes consume one operand, including when invoked by a printed alias.
_AZURE_VALUES = frozenset("""
    --name --subscription --output --query --resource-group --vmss --container-name
    --auth-mode --delimiter --include --marker --num-results --prefix --timeout
    --account-key --account-name --blob-endpoint --connection-string --sas-token
""".split())
_AZURE_SWITCHES = frozenset("--debug --help --only-show-errors --verbose --show-details --show-next-marker".split())
_AZURE_ROUTES = {("account", "show"), ("vm", "list"), ("storage", "blob", "list")}


# The leaf lists the SDK-wide names and refers readers to root help. Only
# emitted names are activated, using the syntax of those common declarations.
_GOOGLE_GLOBALS = {
    "--access-token-file": ("ACCESS_TOKEN_FILE", "Read the access token from this file."),
    "--account": ("ACCOUNT", "Use this account for the invocation."),
    "--billing-project": ("BILLING_PROJECT", "Charge quota to this project."),
    "--configuration": ("CONFIGURATION", "Use this named CLI configuration."),
    "--flags-file": ("YAML_FILE", "Read flags from a YAML or JSON file."),
    "--flatten": ("[KEY,...]", "Flatten the selected output fields into separate records."),
    "--format": ("FORMAT", "Select the output format."),
    "--help": ("", "Display detailed command help."),
    "--impersonate-service-account": ("SERVICE_ACCOUNT_EMAILS", "Make API requests as a service account."),
    "--log-http": ("", "Log HTTP requests and responses."),
    "--project": ("PROJECT_ID", "Use this project for the invocation."),
    "--quiet": ("", "Disable interactive prompts."),
    "--trace-token": ("TRACE_TOKEN", "Attach a token for tracing requests."),
    "--user-output-enabled": ("", "Enable user-facing output."),
    "--verbosity": ("VERBOSITY", "Set the logging verbosity."),
}

def _azure_document(lines, source, summarize):
    """Read the declaration and explanation columns, preserving actual aliases and required labels."""
    rows, positions = [], []
    category = None
    for index, line in enumerate(lines):
        if line and not line[0].isspace():
            category = line.strip() if "Arguments" in line else None
            continue
        match = re.fullmatch(r"    ((?:--?[\w-]+\s+)*--?[\w-]+)(\s+\[Required\])?\s*:\s*(.*)", line)
        if not category or not match:
            continue
        names = match[1].split()
        body = [match[3]]
        for position in range(index + 1, len(lines)):
            next_line = lines[position]
            if not next_line.startswith("        "):
                break
            body.append(next_line.strip())
        description = "\n".join(body)
        required = "Required for this command.\n" if match[2] else ""
        if not set(names) & (_AZURE_VALUES | _AZURE_SWITCHES):
            required += "This help does not specify the operand requirement.\n"
        takes_value = bool(set(names) & _AZURE_VALUES)
        for name in names:
            rows.append({"flag": name, "argument": "VALUE" if takes_value else "", "category": category,
                         "summary": summarize(description, wrapped_table=True),
                         "detail": f"{required}{description}\nSource: {source}"})
            positions.append(index + 1)
    return {"options": rows, "option_lines": positions, "shared": []}


def _google_document(lines, source, parse):
    """Keep global-name indexes and options mentioned in prose out of local declarations."""
    globals_start = lines.index("GCLOUD WIDE FLAGS")
    result = parse("\n".join(lines[:globals_start]), source)
    # Local declarations have five spaces, or seven inside a mutually
    # exclusive group. More deeply indented option names are prose.
    declarations = [(row, at) for row, at in zip(result["options"], result["option_lines"])
                    if re.match(r"^(?: {5}| {7})-\S", lines[at - 1])]
    result["options"] = [row for row, _ in declarations]
    result["option_lines"] = [at for _, at in declarations]
    # Later sections can contain thousands of configuration properties. They
    # have a different grammar and never introduce selectable flags.
    end = next((n for n in range(globals_start + 1, len(lines))
                if lines[n] and lines[n][0].isupper()), len(lines))
    roster = "\n".join(lines[globals_start + 1:end]).strip()
    result["shared"].append({"source": source, "line": globals_start + 1, "section": "GCLOUD WIDE FLAGS",
                             "text": roster, "options": [], "association": "unassigned"})
    for flag in dict.fromkeys(re.findall(r"--[a-z][a-z-]*", roster)):
        if flag not in _GOOGLE_GLOBALS or any(row["flag"].rstrip("=") == flag for row, _ in declarations):
            continue
        arg, summary = _GOOGLE_GLOBALS[flag]
        result["options"].append({"flag": flag + ("=" if arg else ""), "argument": arg,
                                  "category": "GCLOUD WIDE FLAGS", "summary": summary,
                                  "detail": summary + "\nSDK-wide option. See gcloud help for the global declaration."
                                            + "\nSource: " + source})
        result["option_lines"].append(globals_start + 1)
    return result


def _rich_flash_document(lines, source, summarize):
    """Read Rich's two esptool option panels at their emitted widths, ignoring truncated names."""
    rows, positions = [], []
    panel = None
    for index, line in enumerate(lines):
        if line.startswith("╭"):
            match = re.match(r"╭─ (Flash options|Options) ─", line)
            panel = match[1] if match else None
        if not panel or not re.match(r"^│ --[\w-]+\s", line):
            continue
        # The last aligned field is the explanation. Its horizontal offset is
        # also the left edge of wrapped explanation cells on subsequent lines.
        fields = list(re.finditer(r"\S(?:.*?\S)?(?= {2,}|$)", line[2:-1].rstrip()))
        if len(fields) < 2:
            continue
        parts = [field[0] for field in fields]
        names = [parts.pop(0)]
        if parts and re.fullmatch(r"-[A-Za-z]+", parts[0]):
            names.append(parts.pop(0))
        if not parts:
            continue
        argument = "".join(parts[:-1])
        desc_at = fields[-1].start() + 2
        body = [parts[-1]]
        for position in range(index + 1, len(lines)):
            following = lines[position]
            if not following.startswith("│ ") or following.startswith("│ --"):
                break
            argument += following[2:desc_at].strip()
            if segment := following[desc_at:-1].strip():
                body.append(segment)
        description = "\n".join(body)
        count = 2 if argument.startswith("[<address> <filename>]") else 1
        for name in names:
            row = {"flag": name, "argument": argument, "category": panel,
                   "summary": summarize(description, wrapped_table=True),
                   "detail": description + "\nSource: " + source}
            if count > 1:
                row["argument_count"] = count
            rows.append(row)
            positions.append(index + 1)
    return {"options": rows, "option_lines": positions, "shared": []}


def _aws_document(lines, source, summarize):
    """Read typed AWS manual declarations in option sections, independently of synopsis and examples."""
    declarations = []
    synopsis = {}
    sections = set()
    scope = ""
    for index, line in enumerate(lines):
        if line.upper() in {"NAME", "DESCRIPTION", "SYNOPSIS", "OPTIONS", "GLOBAL OPTIONS",
                            "EXAMPLES", "OUTPUT", "SEE ALSO"}:
            scope = line.upper()
            sections.add(index)
        if scope == "SYNOPSIS" and line.lstrip().startswith("[--"):
            for flag in re.findall(r"--[a-z][a-z0-9-]+", line):
                synopsis[flag] = line.strip()
        if scope not in {"OPTIONS", "GLOBAL OPTIONS"}:
            continue
        match = re.match(r"^       (--[\w-]+(?:\s+\|\s+--[\w-]+)*)\s+\((\w+)\)\s*(.*)$", line)
        if match:
            declarations.append((index, scope, match))
    stops = sorted(sections | {i for i, _, _ in declarations} | {len(lines)})
    rows, positions = [], []
    for index, category, match in declarations:
        end = stops[bisect_right(stops, index)]
        body = [s.strip() for s in [match[3], *lines[index + 1:end]]]
        text = "\n".join(body).strip()
        for name in re.split(r"\s+\|\s+", match[1]):
            arg = "" if match[2] == "boolean" or name == "--version" else "(" + match[2] + ")"
            optional = name in {"--sse", "--sse-c", "--sse-c-copy-source", "--request-payer", "--generate-cli-skeleton"}
            summary = summarize(text, wrapped_table=True)
            if name == "--no-follow-symlinks":
                summary = "Skip symbolic links when uploading from the local file system."
            detail = text
            if name == "--version":
                detail += "\nThis version action exits without taking an operand."
            elif syntax := synopsis.get(name):
                detail += "\nSyntax: " + syntax
            if optional:
                detail += "\nThe option can also be supplied without a value."
            rows.append({"flag": name, "category": category.title(), "argument": arg, "argument_optional": optional,
                         "summary": summary, "detail": detail + "\nSource: " + source})
            positions.append(index + 1)
    return {"options": rows, "option_lines": positions, "shared": []}


def cloud_document(text, source, command, parse, summarize):
    """Dispatch only recognized native formats; return None for the general declaration reader."""
    if not command:
        return None
    lines = text.splitlines()
    name = command[0]
    if name == "az" and tuple(command[1:]) in _AZURE_ROUTES and "Global Arguments" in lines:
        return _azure_document(lines, source, summarize)
    if name == "gcloud" and "GCLOUD WIDE FLAGS" in lines and "SYNOPSIS" in lines:
        return _google_document(lines, source, parse)
    if name in {"esptool", "esptool.py"} and command[-1] == "write-flash" and any(
            line.startswith("╭─ Flash options ─") for line in lines):
        return _rich_flash_document(lines, source, summarize)
    if name == "aws" and {"OPTIONS", "GLOBAL OPTIONS", "SYNOPSIS"}.issubset(line.upper() for line in lines):
        return _aws_document(lines, source, summarize)
    if name in {"helm", "arduino-cli"} and any("Flags:" == line for line in lines):
        # Cobra prints the value's type followed by the default selected by a
        # bare flag. Explicit values use an equals sign in pflag's grammar.
        result = parse(text, source)
        for row, index in zip(result["options"], result["option_lines"]):
            match = re.match(r'^\s*--[\w-]+\s+(\w+)\[=([^\]]+)\]\s{2,}(.+)', lines[index - 1])
            if match:
                row.update(argument="[=" + match[1] + "]", argument_optional=True, argument_style="equals",
                           summary=summarize(match[3], wrapped_table=True),
                           detail=f"{match[3]}\nBare {row['flag']} supplies {match[2]}.\nSource: {source}")
        return result
    return None
