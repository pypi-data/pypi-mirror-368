# dirflex/cli.py
from __future__ import annotations
import argparse
import sys
from pathlib import Path
from .core import (
    detect_spaces_per_level, parse_lines_to_depth_name, path_components_from_structure,
    create_from_components, scan_dir_to_entries, render_entries_as_indented,
    render_entries_as_ascii, entries_to_json
)

def build_parser():
    p = argparse.ArgumentParser(prog="dirflex", description="dirflex - create or scan filesystem trees")
    sub = p.add_subparsers(dest="command", required=True)

    # create/generate subcommand
    gen = sub.add_parser("gen", help="Generate filesystem from tree text (alias: create)")
    gen.add_argument("-i","--input", nargs="+", default=["tree.txt"], help="Input file(s) or '-' for stdin")
    gen.add_argument("-t","--tree", help="Raw tree string (ignore --input)")
    gen.add_argument("-o","--output", required=True, help="Output root directory")
    gen.add_argument("-s","--spaces", type=int, help="Spaces per depth level (auto-detected if omitted)")
    gen.add_argument("--tab-size", type=int, default=4, help="Tab size in spaces")
    gen.add_argument("-m","--mode", choices=("skip","merge","overwrite"), default="skip", help="Mode for existing items")
    gen.add_argument("--force", action="store_true", help="Allow destructive replacements when used with overwrite")
    gen.add_argument("--dry-run", action="store_true", help="Preview only")
    gen.add_argument("--save-structure", help="Save parsed structure to file (.txt or .json)")
    gen.add_argument("--no-color", action="store_true", help="Disable colors")
    gen.add_argument("-v","--verbose", action="store_true", help="Verbose")

    # scan subcommand
    scan = sub.add_parser("scan", help="Scan an existing directory and emit tree text")
    scan.add_argument("root", help="Directory to scan")
    scan.add_argument("--ascii", action="store_true", help="Output ascii/tree characters (├──,│,└──)")
    scan.add_argument("--spaces", type=int, default=4, help="Spaces per indentation level for indented output")
    scan.add_argument("--tabs", action="store_true", help="Use tabs instead of spaces")
    scan.add_argument("--emoji", nargs=2, metavar=("FOLDER", "FILE"), help="Use emojis for folder/file lines: e.g. --emoji 📁 📄")
    scan.add_argument("--json", action="store_true", help="Output JSON representation")
    scan.add_argument("--follow-symlinks", action="store_true", help="Follow symlinks when scanning")
    scan.add_argument("--max-depth", type=int, help="Limit depth")
    scan.add_argument("--save", help="Save output to file")
    scan.add_argument("-v","--verbose", action="store_true", help="Verbose")

    return p

def read_inputs(input_paths):
    lines = []
    for p in input_paths:
        if p == "-":
            lines.extend(sys.stdin.read().splitlines())
        else:
            fp = Path(p)
            if not fp.exists():
                if p != "tree.txt":
                    print(f"Warning: input file not found, skipping: {p}", file=sys.stderr)
                continue
            lines.extend(fp.read_text(encoding="utf-8").splitlines())
    return lines

def cmd_gen(args):
    # collect raw lines
    if args.tree:
        raw_lines = args.tree.splitlines()
    else:
        raw_lines = read_inputs(args.input)
    if not raw_lines:
        print("No input lines found. Use -i or --tree or pipe via '-'")
        return 1
    spaces = args.spaces if args.spaces is not None else detect_spaces_per_level(raw_lines)
    if args.verbose:
        print(f"Using spaces per depth: {spaces}")
    entries_depth_name = parse_lines_to_depth_name(raw_lines, spaces, tab_size=args.tab_size)
    comps_and_flags = path_components_from_structure(entries_depth_name)
    # deduplicate preserving order
    seen=set(); unique=[]
    for comps,is_file in comps_and_flags:
        key=Path(*comps).as_posix()
        if key not in seen:
            seen.add(key); unique.append((comps,is_file))
    outroot = Path(args.output)
    if not args.dry_run and outroot.exists() and args.mode=="overwrite" and args.force:
        if args.verbose:
            print(f"Removing existing root (overwrite + force): {outroot}")
        import shutil; shutil.rmtree(outroot)
    created, skipped = create_from_components(unique, outroot, mode=args.mode, force=args.force, dry_run=args.dry_run, verbose=args.verbose, no_color=args.no_color)
    if args.save_structure:
        save_path = Path(args.save_structure)
        if save_path.suffix.lower()==".json":
            import json
            data=[{"path": Path(*c).as_posix(), "is_file": bool(f)} for c,f in unique]
            save_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        else:
            save_path.write_text("\n".join(str(Path(*c).as_posix()) for c,f in unique), encoding="utf-8")
    if args.dry_run:
        print("Preview complete.")
    else:
        print(f"Done. Created structure at: {outroot}")
    return 0

def cmd_scan(args):
    root = Path(args.root)
    if not root.exists():
        print(f"Root not found: {root}", file=sys.stderr)
        return 1
    entries = scan_dir_to_entries(root, follow_symlinks=args.follow_symlinks, max_depth=args.max_depth)
    if args.json:
        out = entries_to_json(entries)
    elif args.ascii:
        out_lines = render_entries_as_ascii(entries)
        out = "\n".join(out_lines)
    else:
        out_lines = render_entries_as_indented(entries, spaces=args.spaces, use_tabs=args.tabs, emoji=tuple(args.emoji) if args.emoji else None)
        out = "\n".join(out_lines)
    if args.save:
        Path(args.save).write_text(out, encoding="utf-8")
        if args.verbose: print(f"Saved to {args.save}")
    else:
        print(out)
    return 0

def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "gen":
        return cmd_gen(args)
    elif args.command == "create":
        return cmd_gen(args)
    elif args.command == "scan":
        return cmd_scan(args)
    else:
        parser.print_help()
        return 1
