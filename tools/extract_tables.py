#!/usr/bin/env python3
"""Extract every table/table* environment, keyed by its \\label.

Usage:
    python3 tools/extract_tables.py FILE.tex [FILE2.tex ...] [-o OUT.json]

For each table or table* environment (comments removed) the tool records the first
\\label inside it and the body of every tabular, tabular*, tabularx or longtable
environment inside it: the text between the column specification and the matching
\\end, with every run of whitespace collapsed to one space. Several tabulars in one
table are joined with " ||| ". A table without a label is keyed "unlabelled:FILE:N".
The output is one JSON object:
    {"sources": [...], "tables": {label: body}, "colspecs": {label: spec},
     "envs": {label: env}, "files": {label: file}, "other_labels": {label: [...]}}
Only the Python standard library is used; see CHANGES.md ("Files").
"""
import argparse
import json
import re

TABULARS = ['tabular', 'tabular*', 'tabularx', 'longtable']


def match_brace(s, i):
    depth = 0
    j = i
    while j < len(s):
        c = s[j]
        if c == '\\':
            j += 2
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return j
        j += 1
    raise ValueError('unbalanced brace at offset %d' % i)


def strip_comments(s):
    return re.sub(r'(?<!\\)%[^\n]*(?:\n[ \t]*)?', '', s)


def env_spans(s, names):
    pat = re.compile(r'\\(begin|end)\{(' + '|'.join(re.escape(n) for n in names) + r')\}')
    spans, stack = [], []
    for m in pat.finditer(s):
        if m.group(1) == 'begin':
            stack.append((m.group(2), m.start(), m.end()))
        elif stack and stack[-1][0] == m.group(2):
            name, start, inner = stack.pop()
            if not stack:
                spans.append((name, start, inner, m.start(), m.end()))
    return spans


def collapse(s):
    return re.sub(r'\s+', ' ', s).strip()


def tabular_bodies(table_src):
    out = []
    for name, start, inner, inner_end, end in env_spans(table_src, TABULARS):
        j = inner
        nargs = 2 if name in ('tabular*', 'tabularx') else 1   # width argument first
        if name == 'longtable':
            while j < len(table_src) and table_src[j] in ' \t\n':
                j += 1
            if j < len(table_src) and table_src[j] == '[':
                j = table_src.index(']', j) + 1
        spec = []
        for _ in range(nargs):
            while table_src[j] in ' \t\n':
                j += 1
            e = match_brace(table_src, j)
            spec.append(table_src[j + 1:e])
            j = e + 1
        out.append((collapse(spec[-1]), collapse(table_src[j:inner_end])))
    return out


def extract(path, text=None):
    src = strip_comments(text if text is not None else open(path, encoding='utf-8').read())
    rows = []
    for n, (name, start, inner, inner_end, end) in enumerate(env_spans(src, ['table', 'table*']), 1):
        block = src[start:end]
        labels = re.findall(r'\\label\{([^}]*)\}', block)
        key = labels[0] if labels else 'unlabelled:%s:%d' % (path, n)
        bodies = tabular_bodies(block)
        rows.append({'label': key, 'env': name, 'file': path,
                     'colspec': ' ||| '.join(b[0] for b in bodies),
                     'body': ' ||| '.join(b[1] for b in bodies),
                     'other_labels': labels[1:]})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('tex', nargs='+')
    ap.add_argument('-o', '--output')
    a = ap.parse_args(argv)
    res = {'sources': a.tex, 'tables': {}, 'colspecs': {}, 'envs': {}, 'files': {}, 'other_labels': {}}
    for path in a.tex:
        for r in extract(path):
            if r['label'] in res['tables']:
                raise SystemExit('duplicate table label %s' % r['label'])
            res['tables'][r['label']] = r['body']
            res['colspecs'][r['label']] = r['colspec']
            res['envs'][r['label']] = r['env']
            res['files'][r['label']] = r['file']
            if r['other_labels']:
                res['other_labels'][r['label']] = r['other_labels']
    text = json.dumps(res, indent=1, ensure_ascii=False)
    if a.output:
        with open(a.output, 'w', encoding='utf-8') as fh:
            fh.write(text + '\n')
    else:
        print(text)


if __name__ == '__main__':
    main()
