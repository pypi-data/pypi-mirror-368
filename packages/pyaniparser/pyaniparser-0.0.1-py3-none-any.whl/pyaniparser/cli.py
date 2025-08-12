import argparse
import json
import sys

from .parser import parse, parse_batch


def main(argv = None) :
    ap = argparse.ArgumentParser(prog = "pyaniparse")
    ap.add_argument("titles", nargs = "*")
    ap.add_argument("--globalization", choices = ["Simplified", "Traditional", "NotChange"], default = "Simplified")
    ap.add_argument("--batch", action = "store_true")
    args = ap.parse_args(argv)

    if args.batch :
        titles = [line.strip() for line in sys.stdin if line.strip()]
        out = [r.__dict__ for r in parse_batch(titles, args.globalization)]
    else :
        out = [(p := parse(t, args.globalization)).__dict__ if p else None for t in args.titles]
        if len(out) == 1 : out = out[0]
    print(json.dumps(out, ensure_ascii = False, indent = 2))
