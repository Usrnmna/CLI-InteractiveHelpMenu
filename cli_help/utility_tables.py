"""Read the declaration columns in fixed media, transfer and archive help responses."""

import re


SPELLING = r"--?[A-Za-z0-9][\w+-]*"
DECLARATION = re.compile(rf"({SPELLING}(?:,\s*{SPELLING})*)(?:\s+(.+))?$")
YT_LEGACY = {"Almost redundant options", "Redundant options", "Not recommended", "Developer options", "Old aliases"}


def _layout(name, text):
    """Identify complete, known layouts so historical fragments still use generic discovery."""
    if name in {"magick", "convert"} and text.startswith("Version: ImageMagick ") and "Image Settings:" in text:
        return "image"
    if name == "vlc" and "Options-styles:" in text and " core program (core)" in text:
        return "vlc"
    if name == "yt-dlp":
        if text.startswith("Usage: yt-dlp ") and "\nOptions:" in text:
            return "video"
        if text.startswith("yt-dlp(1)") and "\nOPTIONS\n" in text:
            return "video-man"
    if name in {"rclone", "restic"} and "\nFlags:\n" in text and "Usage:\n" in text:
        return "flags"
    if name == "borg" and text.startswith("usage: borg create ") and "\nCommon options:" in text:
        return "borg"
    if name in {"7z", "7zz"} and "\n<Switches>\n" in text and "\n7-Zip " in text:
        return "archive"
    return None


def _table_lines(layout, lines):
    """Yield source line numbers, current categories, declaration cells and their continuations."""
    active = False
    section = ""
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if layout == "image" and indent == 0:
            active = stripped.endswith(":") and not stripped.startswith("Usage:")
            section = stripped.rstrip(":")
        elif layout == "vlc" and indent in (1, 3) and stripped and not stripped.startswith(("-", ":")):
            active = True
            section = stripped.rstrip(":")
        elif layout == "video" and indent == 2 and stripped.endswith(":"):
            section = stripped[:-1]
            active = section != "Preset Aliases"
        elif layout == "video-man" and stripped and indent in (0, 3):
            if indent == 0:
                active = stripped == "OPTIONS"
                section = ""
            elif stripped.endswith(":") and active:
                section = stripped[:-1]
                active = section != "Preset Aliases"
            elif stripped in YT_LEGACY:
                section, active = stripped, True
            elif not stripped.endswith(":"):
                active = False
        elif layout in ("flags", "borg") and stripped and not indent:
            active = stripped.casefold().endswith(("flags:", "options:"))
            section = stripped[:-1]
        elif layout == "archive" and stripped == "<Switches>":
            active, section = True, "Switches"
        if not active:
            continue

        legacy = layout == "video-man" and section in YT_LEGACY
        margin = {"image": (2,), "vlc": (2, 6), "video": (4,), "video-man": (14,) if legacy else (7,),
                  "flags": (2, 6), "borg": (2,), "archive": (2, 4)}[layout]
        if indent in margin and stripped.startswith("-"):
            if layout == "archive":
                syntax, _, effect = stripped.partition(" : ")
            elif layout == "vlc":
                match = re.fullmatch(rf"({SPELLING}(?:, {SPELLING})*(?: (?:<[^>]+>|\{{[^}}]+\}}))?)(?:\s+(.*))?", stripped)
                if not match:
                    continue
                syntax, effect = match[1], match[2] or ""
            elif layout == "image":
                # The ImageMagick table uses a 21-character field. Longer terms
                # continue on the next line, even when the terms contain spaces.
                if "  -word-break type " in line and line.startswith("  -write-mask filename "):
                    # In this release two adjacent printf strings lack a newline.
                    first, second = line.split("  -word-break type ", 1)
                    yield number, section, "-write-mask filename", first[23:].strip()
                    yield number, section, "-word-break type", second.strip()
                    continue
                syntax, effect = (line[:23].strip(), line[23:].strip()) if line[22:23] == " " else (stripped, "")
            elif layout == "video-man" and not legacy:
                syntax, effect = stripped, ""
            else:
                cells = re.split(r"\s{2,}", stripped, maxsplit=1)
                syntax, effect = cells[0], cells[1] if len(cells) == 2 else ""
            if layout == "image" and effect in {"geometry", "args"} and number < len(lines) and lines[number].startswith(" " * 23):
                syntax, effect = stripped, ""
            yield number, section, syntax, effect
        elif indent > max(margin) and stripped:
            yield number, section, None, stripped


def utility_table_document(command, text, source, summarize):
    """Parse supported fixed tables, retaining their literal syntax and option-specific prose."""
    name = command[0]
    layout = _layout(name, text)
    if layout is None:
        return None
    lines = text.splitlines()
    groups = []
    for n, section, syntax, effect in _table_lines(layout, lines):
        if syntax is not None:
            groups.append((n, section, syntax, [effect] if effect else []))
        elif groups and section == groups[-1][1]:
            groups[-1][-1].append(effect)
    options, positions = [], []
    for n, section, syntax, body in groups:
        fields = {}
        if layout == "archive":
            # Compound templates require the separate reviewed extraction grammar.
            # Bare literals and optional attached suffixes are unambiguous here.
            match = re.fullmatch(r"(-[A-Za-z0-9]+)(\[[^\[\]{}]+\])?", syntax)
            if not match:
                continue
            names, operand = [match[1]], match[2] or ""
            if operand:
                fields.update(argument_optional=True, argument_style="attached_only")
        else:
            match = DECLARATION.fullmatch(syntax)
            if not match:
                continue
            names = re.split(r",\s*", match[1])
            operand = match[2] or ""
        if layout == "image" and lines[0].startswith("Version: ImageMagick 7.1.2-18 "):
            # Both front ends print -view but reject it on an image. Two
            # compatibility switches work only through the older convert CLI.
            if names == ["-view"] or name == "magick" and names[0] in {"-support", "-perceptible"}:
                continue
        if layout == "image" and names == ["-view"] and not operand:
            # The command option table declares one value although the fixed
            # help omits its metavar.
            operand = "string"
        if not body:
            continue
        prose = " ".join(body)
        if layout == "video-man" and names == ["--srt-lang"] and section == "Old aliases":
            prose += " This prefix selects --srt-langs, the legacy alias for --sub-langs."
        if layout.startswith("video"):
            # A wrap at a hyphen may split a literal alias across two lines.
            for alias in re.findall(r"\(Alias:\s*(--[\w-]+(?:-\s+[\w-]+)?)\)", prose):
                names.append(alias.replace(" ", ""))
        count = len(operand.split()) if layout in ("image", "video", "video-man") else int(bool(operand))
        if count > 1:
            fields["argument_count"] = count
        if layout == "flags" and "--verbose" in names and (operand == "count" or "--verbose=n" in prose):
            operand = "[=LEVEL]"
            fields.update(argument_optional=True, argument_style="equals")
        for flag in dict.fromkeys(names):
            summary = summarize(prose, wrapped_table=True)
            if layout == "vlc" and flag.startswith("--no-"):
                summary = f"Disable --{flag[5:]}."
            if layout == "video-man" and section in YT_LEGACY:
                summary = f"{section}: {prose}"
            value, detail = operand, prose
            if layout == "vlc" and flag == "-v" and "--verbose" in names:
                value = ""
                summary = "Increase verbosity by one level."
                detail = "Repeat -v for more verbosity. --verbose takes an integer level."
            options.append(dict(flag=flag, argument=value, category=section or "Options", summary=summary,
                                detail=f"{detail}\nSyntax: {syntax}\nSource: {source}", **fields))
            positions.append(n)
    return {"options": options, "option_lines": positions, "shared": []}
