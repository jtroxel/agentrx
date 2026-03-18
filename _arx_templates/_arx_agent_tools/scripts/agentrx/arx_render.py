#!/usr/bin/env python3
"""
ARX Multi-Pass Evaluator (Reference Implementation)
Processes ARX-style Markdown tags: <ARX [[expr]] />
Compatible with standard Markdown and both Programmatic/Agentic evaluators.
"""

import re
import json
import sys
import argparse
import os

# Tag pattern: <ARX [[expression]] />
# Matches variables, blocks, etc.
# Group 1: Expression (e.g. [[var]])
TAG_PATTERN = re.compile(r'<ARX\s+\[\[(.+?)\]\]\s*/>', re.DOTALL)

def resolve_dot_notation(data, path):
    """
    Look up 'user.profile.name' in data dictionary.
    """
    keys = path.split('.')
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list):
            try:
                current = current[int(key)]
            except (IndexError, ValueError):
                return None
        else:
            return None
    return current

def render_arx(content, data):
    """
    Renders ARX tags in content using provided data.
    Punts (preserves) tags where data is missing.
    """
    def replacer(match):
        expr = match.group(1).strip()
        
        # Sigil Handling (TODO: Full Logic)
        if expr.startswith('#'):
            # If Block opener
            pass 
            
        val = resolve_dot_notation(data, expr)
        
        if val is not None:
            # Handle standard escaping or {raw} interpolation
            if expr.startswith('{') and expr.endswith('}'):
                # Raw (no interpolation)
                return str(val)
            else:
                # Standard (Placeholder for future escaping)
                return str(val).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Data missing: Punt (preserve tag)
        return match.group(0)

    return TAG_PATTERN.sub(replacer, content)

def main():
    parser = argparse.ArgumentParser(description="ARX Templating Evaluator")
    parser.add_argument("file", help="Markdown file to process")
    parser.add_argument("--data", help="JSON data string for interpolation")
    parser.add_argument("--data-file", help="Path to JSON file for interpolation")
    parser.add_argument("--output", help="Output file path (default: stdout)")

    args = parser.parse_args()

    # Load data
    context = {}
    if args.data_file:
        with open(args.data_file, 'r') as f:
            context.update(json.load(f))
    if args.data:
        context.update(json.loads(args.data))

    # Read content
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)
        
    with open(args.file, 'r') as f:
        content = f.read()

    # Render
    output = render_arx(content, context)

    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
    else:
        sys.stdout.write(output)

if __name__ == "__main__":
    main()
