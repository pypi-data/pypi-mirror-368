# dirflex/core.py
from __future__ import annotations
import os
import re
import json
import shutil
from pathlib import Path
from typing import List, Tuple, Iterable, Optional

# ---- helpers for parsing (robust) ----

BOX_DRAWING_RE = re.compile(r'[\u2500-\u257F]')
TREE_CHARS_RE = re.compile(r'(^\s*[\|│\s]*)(?:[├└┐┬┤╰╭╮╯]\s*[-–—─]+\s*)?')

def normalize_line_for_parsing(line: str, tab_size: int = 4) -> str:
    line = line.replace("\t", " " * tab_size)
    cleaned = BOX_DRAWING_RE.sub(" ", line)
    cleaned = re.sub(r'[–—\-]{2,}', ' ', cleaned)
    m = TREE_CHARS_RE.match(cleaned)
    if m:
        prefix = m.group(1)
        rest = cleaned[len(prefix):]
        rest = re.sub(r'^[\s\-\└\├\─\┬\╰\╭\╮\╯\|]+', ' ', rest)
        return prefix + rest.lstrip()
    return cleaned

def detect_spaces_per_level(lines: Iterable[str]) -> int:
    indents = []
    for raw in lines:
        normalized = normalize_line_for_parsing(raw)
        if not normalized.strip(): 
            continue
        leading = len(normalized) - len(normalized.lstrip(" "))
        if leading > 0:
            indents.append(leading)
    if not indents:
        return 4
    base = min(indents)
    if base >= 8:
        for d in (4,2):
            if all((x % d == 0) for x in indents):
                return d
    return base or 4

def guess_is_file(name: str) -> bool:
    if not name:
        return False
    if name.endswith("/"): 
        return False
    simple = name.rstrip("/").strip()
    if simple.startswith(".") and simple.count(".") == 1:
        return False
    if re.search(r'\.[A-Za-z0-9][A-Za-z0-9_\-]*(?:$|\b|\))', simple):
        return True
    return False

def parse_lines_to_depth_name(lines: Iterable[str], spaces_per_level: int, tab_size:int=4) -> List[Tuple[int, str]]:
    entries: List[Tuple[int,str]] = []
    for raw in lines:
        if not raw.strip(): 
            continue
        normalized = normalize_line_for_parsing(raw, tab_size)
        leading = len(normalized) - len(normalized.lstrip(" "))
        depth = 0 if spaces_per_level == 0 else leading // spaces_per_level
        name = normalized.strip()
        if name == ".":
            continue
        entries.append((depth, name))
    return entries

def path_components_from_structure(entries: List[Tuple[int, str]]) -> List[Tuple[List[str], bool]]:
    stack: List[str] = []
    out = []
    for depth, name in entries:
        stack = stack[:depth]
        stack.append(name)
        comps = [c for c in stack if c and c != "."]
        is_file = guess_is_file(name)
        out.append((comps, is_file))
    return out

# ---- create on disk ----

def create_from_components(
    comps_and_fileflags: List[Tuple[List[str], bool]],
    output_root: Path,
    mode: str = "skip",
    force: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
    no_color: bool = False
) -> Tuple[int,int]:
    created = 0
    skipped = 0
    for comps, is_file in comps_and_fileflags:
        if not comps:
            continue
        target = output_root.joinpath(*comps)
        parent = target.parent

        if is_file:
            if dry_run:
                if verbose: print(f"[DRY] File: {target}")
                continue
            if parent.exists() and parent.is_file():
                if force:
                    parent.unlink()
                    parent.mkdir(parents=True, exist_ok=True)
                else:
                    if verbose: print(f"Conflict: parent is file: {parent}")
                    skipped += 1
                    continue
            else:
                parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                if target.is_dir():
                    if force:
                        shutil.rmtree(target)
                    else:
                        if verbose: print(f"Conflict: directory exists where file expected: {target}")
                        skipped += 1
                        continue
                if mode == "skip":
                    skipped += 1
                    if verbose: print(f"Skipped existing file: {target}")
                    continue
                elif mode == "merge":
                    if verbose: print(f"Kept existing file (merge): {target}")
                    continue
                elif mode == "overwrite":
                    target.write_text("", encoding="utf-8")
                    created += 1
                    if verbose: print(f"Overwrote file: {target}")
                    continue
            else:
                target.touch(exist_ok=True)
                created += 1
                if verbose: print(f"Created file: {target}")
        else:
            if dry_run:
                if verbose: print(f"[DRY] Dir: {target}")
                continue
            if target.exists():
                if target.is_file():
                    if force:
                        target.unlink()
                        target.mkdir(parents=True, exist_ok=True)
                        created += 1
                    else:
                        if verbose: print(f"Conflict: file exists where dir expected: {target}")
                        skipped += 1
                        continue
                else:
                    if mode == "overwrite" and force:
                        shutil.rmtree(target)
                        target.mkdir(parents=True, exist_ok=True)
                        created += 1
                        if verbose: print(f"Recreated directory: {target}")
                    else:
                        if verbose: print(f"Directory exists: {target}")
                        skipped += 1
                        continue
            else:
                target.mkdir(parents=True, exist_ok=True)
                created += 1
                if verbose: print(f"Created directory: {target}")
    return created, skipped

# ---- scan directory -> tree text ----

def _format_ascii_tree(lines: List[Tuple[int, str, bool]]) -> List[str]:
    # Given list of (depth, name, is_file), build ascii-tree style lines
    out = []
    last_at_depth = {}
    total = len(lines)
    for idx, (depth, name, is_file) in enumerate(lines):
        # determine connector char: last child vs not
        # find if next item at same or shallower depth exists to consider 'has sibling'
        has_sibling = False
        for j in range(idx+1, total):
            if lines[j][0] < depth:
                break
            if lines[j][0] == depth:
                has_sibling = True
                break
        prefix = ""
        if depth > 0:
            parts = []
            for d in range(depth):
                parts.append("│   " if any(l[0] > d and l[0] >= d+1 for l in lines) else "    ")
            prefix = "".join(parts)
            connector = "├── " if has_sibling else "└── "
        else:
            connector = ""
        out.append(f"{prefix}{connector}{name}")
    return out

def scan_dir_to_entries(root: Path, follow_symlinks: bool=False, max_depth: Optional[int]=None) -> List[Tuple[int,str,bool]]:
    entries: List[Tuple[int,str,bool]] = []
    root = root.resolve()
    base_parts = len(root.parts)
    for dirpath, dirnames, filenames in os.walk(root, followlinks=follow_symlinks):
        path = Path(dirpath)
        depth = len(path.parts) - base_parts
        rel = path.name if depth>=0 else str(path)
        # include directory itself (except root)
        if depth >= 0:
            entries.append((depth, path.name, False))
        # directories (sorted)
        for d in sorted(dirnames):
            entries.append((depth+1, d, False))
        for f in sorted(filenames):
            entries.append((depth+1, f, True))
        if max_depth is not None and depth >= max_depth:
            # prune from walking deeper
            dirnames[:] = []
    return entries

def render_entries_as_indented(entries: List[Tuple[int,str,bool]], spaces:int=4, use_tabs:bool=False, emoji:Optional[Tuple[str,str]]=None) -> List[str]:
    out = []
    for depth, name, is_file in entries:
        indent = ("\t" * depth) if use_tabs else (" " * (spaces * depth))
        if emoji:
            folder_emoji, file_emoji = emoji
            symbol = file_emoji if is_file else folder_emoji
            out.append(f"{indent}{symbol} {name}")
        else:
            out.append(f"{indent}{name}")
    return out

def render_entries_as_ascii(entries: List[Tuple[int,str,bool]]) -> List[str]:
    # Convert entries into (depth,name,is_file) list for ascii helper
    # The ascii helper expects ordered depth list. We will rebuild a simpler ordering:
    flat = []
    # We want to emulate 'tree' order: directory, then its children.
    # entries from scan_dir_to_entries already roughly in that order.
    for depth,name,is_file in entries:
        flat.append((depth, name, is_file))
    return _format_ascii_tree(flat)

def entries_to_json(entries: List[Tuple[int,str,bool]]) -> str:
    arr = [{"depth": d, "path": name, "is_file": is_file} for d,name,is_file in entries]
    return json.dumps(arr, indent=2, ensure_ascii=False)
