#!/usr/bin/env python3
"""Self-checks S1-S7 of Prompt 1 (see CHANGES.md, "Files" and "Prompt 1").

Usage (from the repository root):
    python3 tools/check_p1.py --baseline-commit COMMIT [--compile-dir DIR] [-o REPORT.json]

Compares submission/manuscript.tex and submission/supplementary.tex with the copies in
baseline/, using tools/measure.py and tools/extract_tables.py. With --compile-dir the
main file is compiled twice with pdflatex into DIR and the final log is checked (S1).
S7 inspects the staged tree (git diff --cached) against the baseline commit, so the files
of the commit must be staged before the check is run. Exit status 0 when every check passes.
"""
import argparse
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True     # keep tools/ free of __pycache__
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import measure            # noqa: E402
import extract_tables     # noqa: E402

MAIN, SUPP = 'submission/manuscript.tex', 'submission/supplementary.tex'
BMAIN, BSUPP = 'baseline/manuscript.tex', 'baseline/supplementary.tex'
CHANGED_TABLES = {'tab:response_spread', 'tab:robustness'}
ALLOWED_PATHS = [MAIN, 'CHANGES.md', 'tools/', 'baseline/']
REQUIRED_EXTRA = ['metrics_after_p1.json']     # written by Step 3 itself


def raw(path):
    return open(path, encoding='utf-8').read()


# --------------------------------------------------------------------------- S1

def compile_twice(tex, outdir):
    os.makedirs(outdir, exist_ok=True)
    codes = []
    for _ in range(2):
        p = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error',
                            '-output-directory=' + outdir, tex],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        codes.append(p.returncode)
    base = os.path.splitext(os.path.basename(tex))[0]
    return codes, os.path.join(outdir, base + '.log')


# --------------------------------------------------------------------------- block extraction

def brace_arg(s, pos):
    i = s.index('{', pos)
    return s[i + 1:measure.match_brace(s, i)]


def section_star(src, title):
    """Raw text of \\section*{title...} up to the next \\section, \\appendix or \\begingroup."""
    i = src.find('\\section*{' + title)
    if i < 0:
        return None
    m = re.compile(r'\\section\*?\{|\\appendix|\\begingroup|\\begin\{thebibliography\}').search(src, i + 10)
    return src[i:m.start() if m else len(src)].strip()


def r6_blocks(path):
    src = raw(path)
    blocks = {
        'title': brace_arg(src, src.index('\\title')),
        'pdftitle': re.search(r'pdftitle=\{([^}]*)\}', src).group(1),
        'prompt_lstlisting': '\n=====\n'.join(re.findall(r'\\begin\{lstlisting\}.*?\\end\{lstlisting\}', src, flags=re.S)),
    }
    for t in ['Declaration of generative AI', 'CRediT authorship contribution statement', 'Funding',
              'Disclaimer', 'Declaration of competing interest', 'Data availability']:
        blocks['section: ' + t] = section_star(src, t)
    body = measure.strip_comments(src)
    for a, b in measure.env_spans(body, ['figure', 'figure*']):
        fig = body[a:b]
        label = re.search(r'\\label\{([^}]*)\}', fig).group(1)
        cap = brace_arg(fig, fig.index('\\caption'))
        notes = [x.strip() for x in re.findall(r'[^.]*AI assistance[^.]*\.[^.]*?\)?\.?', cap)]
        blocks['AI note in caption of ' + label] = ' '.join(notes)
    return blocks


def bibliography(path):
    src = raw(path)
    a = src.index('\\begin{thebibliography}')
    b = src.index('\\end{thebibliography}') + len('\\end{thebibliography}')
    return src[a:b]


# --------------------------------------------------------------------------- text helpers

def document_sentences(path):
    """(where, sentence) for the running text, captions and table notes of the whole body."""
    src = measure.read(path)
    macros = measure.zero_arg_macros(src)
    prot, _ = measure.protect_verbatim(src)
    body = measure.body_of(measure.strip_comments(prot))
    out = []
    for p in measure.paragraphs(measure.running_text(body)):
        for s in measure.split_sentences(measure.to_plain(p, 'words', macros)):
            out.append(('text', s))
    for a, b in measure.env_spans(body, measure.FLOAT_ENVS):
        fl = body[a:b]
        lab = re.search(r'\\label\{([^}]*)\}', fl)
        where = lab.group(1) if lab else 'float'
        pieces = []
        if '\\caption' in fl:
            pieces.append(brace_arg(fl, fl.index('\\caption')))
        m = re.search(r'\\begin\{tablenotes\}(.*?)\\end\{tablenotes\}', fl, flags=re.S)
        if m:
            pieces += re.split(r'\\item(?:\[[^\]]*\])?', m.group(1))
        for piece in pieces:
            for s in measure.split_sentences(measure.to_plain(piece, 'words', macros)):
                out.append((where, s))
    return out


def span_paragraphs(path, start_marker, end_marker=None):
    src = measure.read(path)
    macros = measure.zero_arg_macros(src)
    prot, _ = measure.protect_verbatim(src)
    body = measure.body_of(measure.strip_comments(prot))
    a = body.index(start_marker)
    b = body.index(end_marker) if end_marker else len(body)
    return [measure.to_plain(p, 'words', macros) for p in measure.paragraphs(measure.running_text(body[a:b]))]


def rows(body):
    body = re.sub(r'\\(toprule|midrule|bottomrule)', '', body)
    return [r.strip() for r in body.split('\\\\') if r.strip()]


# --------------------------------------------------------------------------- checks

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--baseline-commit', required=True)
    ap.add_argument('--compile-dir')
    ap.add_argument('--log', help='pdflatex log of the second pass (instead of --compile-dir)')
    ap.add_argument('-o', '--output')
    a = ap.parse_args(argv)
    rep = {}
    bm = json.load(open('baseline/metrics.json'))

    # S1
    codes = None
    log = a.log
    if a.compile_dir:
        codes, log = compile_twice(MAIN, a.compile_dir)
    lg = measure.parse_log(log)
    base_over = bm['compile']['overfull_hbox']
    s1 = (codes is None or codes == [0, 0]) and not lg['undefined_references'] \
        and not lg['undefined_citations'] and not lg['there_were_undefined_references'] \
        and lg['overfull_hbox'] <= base_over + 2
    rep['S1'] = {'pass': s1, 'pdflatex_exit_codes': codes, 'overfull_hbox': lg['overfull_hbox'],
                 'baseline_overfull_hbox': base_over, 'underfull_hbox': lg['underfull_hbox'],
                 'undefined_references': lg['undefined_references'],
                 'undefined_citations': lg['undefined_citations'],
                 'labels_may_have_changed_after_pass2': lg['labels_may_have_changed'],
                 'pages': lg['pages']}

    # S2
    new = measure.measure(MAIN)
    missing = [k for k in bm['labels'] if k not in new['labels']]
    added = [k for k in new['labels'] if k not in bm['labels']]
    cites_equal = set(new['cite_keys']) == set(bm['cite_keys'])
    bib_equal = bibliography(MAIN) == bibliography(BMAIN)
    rep['S2'] = {'pass': not missing and cites_equal and bib_equal and not new['labels_duplicated'],
                 'missing_labels': missing, 'new_labels': added, 'duplicated_labels': new['labels_duplicated'],
                 'cite_keys_equal': cites_equal, 'n_cite_keys': len(new['cite_keys']),
                 'thebibliography_identical': bib_equal}

    # S3
    bt = json.load(open('baseline/tables.json'))
    nt = {'tables': {}, 'colspecs': {}}
    for path in (MAIN, SUPP):
        for r in extract_tables.extract(path):
            nt['tables'][r['label']] = r['body']
            nt['colspecs'][r['label']] = r['colspec']
    s3_bad, s3_diffs = [], {}
    for lab in sorted(set(bt['tables']) | set(nt['tables'])):
        same = bt['tables'].get(lab) == nt['tables'].get(lab) and bt['colspecs'].get(lab) == nt['colspecs'].get(lab)
        if same:
            continue
        if lab not in CHANGED_TABLES:
            s3_bad.append(lab)
            continue
        old_rows, new_rows = rows(bt['tables'][lab]), rows(nt['tables'][lab])
        removed = [r for r in old_rows if r not in new_rows]
        inserted = [r for r in new_rows if r not in old_rows]
        order_kept = [r for r in new_rows if r in old_rows] == old_rows
        s3_diffs[lab] = {'colspec_changed': bt['colspecs'][lab] != nt['colspecs'][lab],
                         'rows_removed_or_edited': removed, 'rows_inserted': inserted,
                         'existing_rows_unchanged_and_in_order': order_kept and not removed}
        if removed or not order_kept or bt['colspecs'][lab] != nt['colspecs'][lab]:
            s3_bad.append(lab)
    rep['S3'] = {'pass': not s3_bad, 'tables_compared': len(set(bt['tables']) | set(nt['tables'])),
                 'unexpected_differences': s3_bad, 'differences_in_the_two_A1_tables': s3_diffs,
                 'identical_tables': sorted(k for k in bt['tables'] if bt['tables'][k] == nt['tables'].get(k))}

    # S4
    base_tokens = set(bm['numbers']['all_body']) | set(bm['supplement']['numbers_all_body'])
    supp_new = measure.all_body_numbers(
        measure.body_of(measure.strip_comments(measure.protect_verbatim(raw(SUPP))[0])),
        measure.protect_verbatim(raw(SUPP))[1], measure.zero_arg_macros(raw(SUPP)))
    new_tokens = set(new['numbers']['all_body']) | set(supp_new)
    absent = sorted(new_tokens - base_tokens)
    changes = raw('CHANGES.md')
    dn = changes.split('## Derived numbers', 1)[1].split('\n## ', 1)[0] if '## Derived numbers' in changes else ''
    logged = {t: bool(re.search(r'(?<![\d.])' + re.escape(t) + r'(?![\d])', dn)) for t in absent}
    increased = {k: [bm['numbers']['all_body'].get(k, 0), v] for k, v in new['numbers']['all_body'].items()
                 if v > bm['numbers']['all_body'].get(k, 0)}
    rep['S4'] = {'pass': all(logged.values()), 'tokens_absent_from_baseline': absent,
                 'logged_under_derived_numbers': logged,
                 'tokens_whose_count_rose (baseline, new)': increased}

    # S5
    b5, n5 = r6_blocks(BMAIN), r6_blocks(MAIN)
    diff5 = [k for k in b5 if b5[k] != n5.get(k)]
    rep['S5'] = {'pass': not diff5 and all(b5.values()), 'blocks_compared': list(b5), 'differing': diff5}

    # S6
    sents = document_sentences(MAIN)
    immat = [{'where': w, 'sentence': s} for w, s in sents if 'immaterial' in s.lower()]
    overclaim = [x for x in immat if re.search(r'all three datasets|all four|every case|all six', x['sentence'], re.I)
                 and not re.search(r'three of the four', x['sentence'])]
    src_new = raw(MAIN)
    stab = [s for w, s in sents if 'identity line' in s]
    stab_par = [p for p in span_paragraphs(MAIN, '\\subsubsection{Fold-to-fold') if 'identity line' in p]
    union_ok = bool(stab_par) and 'union' in stab_par[0]
    sec2 = span_paragraphs(MAIN, '\\section{Related Work}')
    runtime = [p for p in sec2 if re.search(r'522|matched measurement|matched conditions', p)]
    runtime_ok = all('unscreened 1,959-feature universe' in p for p in runtime) and len(runtime) > 0
    a5_file = open('priority_2/diversity_capped_ho_auc.csv').read()
    a5_arch = raw('archive/manuscript_v1_long.tex')
    a5 = {'capped_value_in_result_file': 'homecredit,lr,family_cap,mRMR,20,0.745693' in a5_file,
          'superseded_value_in_archived_v1_table': 'Full-pool mRMR & LR & $529\\rightarrow20$ & 0.745689' in a5_arch,
          'manuscript_values_unchanged': src_new.count('0.7457') == raw(BMAIN).count('0.7457'),
          'todo_comments': src_new.count('% TODO'),
          'evidence_recorded_in_CHANGES': '0.745693' in changes and '0.745689' in changes}
    a5_ok = a5['capped_value_in_result_file'] and a5['superseded_value_in_archived_v1_table'] \
        and a5['manuscript_values_unchanged'] and a5['evidence_recorded_in_CHANGES']
    rep['S6'] = {
        'pass': not overclaim and 'low end of the fold ranges' not in src_new and '0.14 to 0.42' not in src_new
        and union_ok and runtime_ok and a5_ok,
        'sentences_with_immaterial': immat,
        'overclaiming_sentences': overclaim,
        'low_end_of_the_fold_ranges_absent': 'low end of the fold ranges' not in src_new,
        '0.14_to_0.42_absent': '0.14 to 0.42' not in src_new,
        'identity_line_sentences': stab, 'identity_line_paragraph_mentions_union': union_ok,
        'runtime_measurement_paragraphs_sections_2_8_and_appendices': runtime,
        'every_runtime_mention_says_unscreened_1959': runtime_ok,
        'A5': a5,
    }

    # S7
    out = subprocess.run(['git', 'diff', '--cached', '--name-status', a.baseline_commit],
                         capture_output=True, text=True).stdout.split('\n')
    changed = [l.split('\t')[-1] for l in out if l.strip()]
    stat = subprocess.run(['git', 'diff', '--cached', '--stat', a.baseline_commit], capture_output=True, text=True).stdout
    outside = [p for p in changed if not any(p == x or (x.endswith('/') and p.startswith(x)) for x in ALLOWED_PATHS)]
    unexpected = [p for p in outside if p not in REQUIRED_EXTRA]
    unstaged = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True).stdout
    rep['S7'] = {'pass': not unexpected, 'changed_paths': changed, 'outside_allowed_list': outside,
                 'outside_but_required_by_step_3': [p for p in outside if p in REQUIRED_EXTRA],
                 'supplement_changed': SUPP in changed, 'diff_stat': stat,
                 'working_tree_status_not_part_of_commit': [l for l in unstaged.split('\n') if l and not l.startswith(('M ', 'A ', 'D ', 'R '))]}

    rep['all_pass'] = all(rep[k]['pass'] for k in ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7'])
    text = json.dumps(rep, indent=1, ensure_ascii=False)
    if a.output:
        open(a.output, 'w', encoding='utf-8').write(text + '\n')
    for k in ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7']:
        print(k, 'PASS' if rep[k]['pass'] else 'FAIL')
    return 0 if rep['all_pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
