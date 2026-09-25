#!/usr/bin/env python3
"""Self-checks of Prompt 2 (S1-S5, P1-P8; see CHANGES.md, "Files" and "Prompt 2").

Usage (from the repository root):
    python3 tools/check_p2.py --p1-commit COMMIT [--compile-dir DIR | --log LOG] [-o REPORT.json]

Compares submission/manuscript.tex with baseline/ (S2, S4, S5, P1, P2) and with its state
at the Prompt 1 commit (S3, P8). "Sections 2-8" is the text from \\section{Related Work} to
the first unnumbered back-matter section (CRediT), i.e. the numbered sections 2 to 8.
Exit status 0 when every check passes.
"""
import argparse
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import measure            # noqa: E402
import extract_tables     # noqa: E402
import check_p1           # noqa: E402

MAIN, SUPP = 'submission/manuscript.tex', 'submission/supplementary.tex'
BMAIN = 'baseline/manuscript.tex'
LIMITS = {'materiality bar': 6, 'covariate-shift': 3, 'not adjusted': 4, 'descriptive': 6,
          'held-out rule': 0, 'development rule': 0, 'development-rule': 0, 'most adversarial': 0}
PROTECTED_FACTS = [r'\texttt{CODE\_GENDER} holds rank 3 in the mRMR logistic-regression subset',
                   'rank 14 in the RFE CatBoost subset', 'rank 10 in the pure LLM CatBoost subset',
                   r'\texttt{NAME\_FAMILY\_STATUS} holds rank 9 in the pure LLM CatBoost subset',
                   'rank 39 in the RFE CatBoost subset', 'ranks 1 and 6 of the CatBoost SHAP subset',
                   'no LLM-assisted subset contains one', 'LendingClub v2 headline subsets contain no such field',
                   'expert persona of the prompt did not exclude them unasked']


def src_of(path=None, text=None):
    raw = text if text is not None else open(path, encoding='utf-8').read()
    macros = measure.zero_arg_macros(raw)
    prot, verb = measure.protect_verbatim(raw)
    body = measure.body_of(measure.strip_comments(prot))
    return raw, macros, body, verb


def span_2_8(body):
    a = body.index('\\section{Related Work}')
    b = body.index('\\section*{CRediT')
    return body[a:b]


def section_text(body, title):
    """Raw LaTeX of one numbered \\section (or \\subsection) up to the next heading of that level."""
    m = re.search(r'\\(sub)?section\{' + re.escape(title) + r'\}', body)
    level = 'subsection' if m.group(1) else 'section'
    rest = body[m.end():]
    stop = re.search(r'\\section\*?\{' if level == 'section' else r'\\(sub)?section\*?\{', rest)
    return rest[:stop.start() if stop else len(rest)]


def plain_paragraphs(fragment, macros):
    return [measure.to_plain(p, 'words', macros) for p in measure.paragraphs(measure.running_text(fragment))]


def float_text(fragment, macros, with_cells):
    """Captions and table notes (and optionally tabular cells) of the floats in fragment, as plain text."""
    out = []
    for a, b in measure.env_spans(fragment, measure.FLOAT_ENVS):
        fl = fragment[a:b]
        if '\\caption' in fl:
            out.append(check_p1.brace_arg(fl, fl.index('\\caption')))
        m = re.search(r'\\begin\{tablenotes\}(.*?)\\end\{tablenotes\}', fl, flags=re.S)
        if m:
            out.append(m.group(1))
        if with_cells:
            for s, e in measure.env_spans(fl, ['tabular']):
                out.append(fl[s:e])
    return measure.to_plain(' '.join(out), 'words', macros)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--p1-commit', required=True)
    ap.add_argument('--compile-dir')
    ap.add_argument('--log')
    ap.add_argument('-o', '--output')
    a = ap.parse_args(argv)
    rep = {}
    bm = json.load(open('baseline/metrics.json'))
    p1_text = subprocess.run(['git', 'show', a.p1_commit + ':' + MAIN], capture_output=True, text=True).stdout
    raw, macros, body, verb = src_of(MAIN)
    braw, bmacros, bbody, bverb = src_of(BMAIN)
    praw, pmacros, pbody, pverb = src_of(text=p1_text)

    # S1
    codes, log = None, a.log
    if a.compile_dir:
        codes, log = check_p1.compile_twice(MAIN, a.compile_dir)
    if log:
        lg = measure.parse_log(log)
        rep['S1'] = {'pass': (codes is None or codes == [0, 0]) and not lg['undefined_references']
                     and not lg['undefined_citations'] and not lg['there_were_undefined_references']
                     and lg['overfull_hbox'] <= bm['compile']['overfull_hbox'] + 2,
                     'pdflatex_exit_codes': codes, 'overfull_hbox': lg['overfull_hbox'],
                     'baseline_overfull_hbox': bm['compile']['overfull_hbox'], 'underfull_hbox': lg['underfull_hbox'],
                     'undefined_references': lg['undefined_references'], 'undefined_citations': lg['undefined_citations'],
                     'labels_may_have_changed_after_pass2': lg['labels_may_have_changed'], 'pages': lg['pages']}

    # S2
    new = measure.measure(MAIN)
    missing = [k for k in bm['labels'] if k not in new['labels']]
    rep['S2'] = {'pass': not missing and set(new['cite_keys']) == set(bm['cite_keys'])
                 and check_p1.bibliography(MAIN) == check_p1.bibliography(BMAIN) and not new['labels_duplicated'],
                 'missing_labels': missing, 'new_labels': [k for k in new['labels'] if k not in bm['labels']],
                 'duplicated_labels': new['labels_duplicated'],
                 'cite_keys_equal': set(new['cite_keys']) == set(bm['cite_keys']),
                 'thebibliography_identical': check_p1.bibliography(MAIN) == check_p1.bibliography(BMAIN)}

    # S3: every table body equals its state after Prompt 1, matched by label
    before = {r['label']: r['body'] for r in extract_tables.extract(MAIN + '@' + a.p1_commit, text=p1_text) + extract_tables.extract(SUPP)}
    after = {r['label']: r['body'] for r in extract_tables.extract(MAIN) + extract_tables.extract(SUPP)}
    diff3 = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    rep['S3'] = {'pass': not diff3, 'tables_compared': len(set(before) | set(after)), 'differing': diff3}

    # S4
    base_tokens = set(bm['numbers']['all_body']) | set(bm['supplement']['numbers_all_body'])
    new_tokens = set(new['numbers']['all_body']) | set(measure.all_body_numbers(src_of(SUPP)[2], src_of(SUPP)[3], src_of(SUPP)[1]))
    absent = sorted(new_tokens - base_tokens)
    changes = open('CHANGES.md', encoding='utf-8').read()
    m_dn = re.search(r'^## Derived numbers\s*$(.*?)(?=^## )', changes, flags=re.M | re.S)
    dn = m_dn.group(1).replace('\u2212', '-') if m_dn else ''
    logged = {t: bool(re.search(r'(?<![\d.])' + re.escape(t) + r'(?![\d])', dn)) for t in absent}
    rep['S4'] = {'pass': all(logged.values()), 'tokens_absent_from_baseline': absent, 'logged': logged}

    # S5
    b5, n5 = check_p1.r6_blocks(BMAIN), check_p1.r6_blocks(MAIN)
    rep['S5'] = {'pass': all(b5[k] == n5.get(k) for k in b5) and all(b5.values()),
                 'differing': [k for k in b5 if b5[k] != n5.get(k)], 'blocks_compared': len(b5)}

    # P1
    def words_2_8(m):
        return sum(p['words'] for p in m['words']['per_section'] if not p['starred'] and p['section'] != 'Introduction')
    w0, w1 = words_2_8(bm), words_2_8(new)
    red = 100.0 * (1 - w1 / w0)
    rep['P1'] = {'pass': red >= 25.0, 'baseline_words_sections_2_8': w0, 'new_words_sections_2_8': w1,
                 'reduction_percent': round(red, 1), 'per_section': {p['section']: p['words'] for p in new['words']['per_section'] if not p['starred']}}

    # P2: numeric tokens of baseline Sections 2-8 (text, captions, notes, cells) must survive
    btok = set(measure.all_body_numbers(span_2_8(bbody), bverb, bmacros))
    doc_tokens = set(new['numbers']['all_body'])
    lost = sorted(btok - doc_tokens)
    m_rd = re.search(r'^### Removed duplicates\s*$(.*?)(?=^##)', changes, flags=re.M | re.S)
    rd = m_rd.group(1).replace('\u2212', '-') if m_rd else ''
    lost_logged = {t: bool(re.search(r'`' + re.escape(t) + r'`', rd)) for t in lost}
    rep['P2'] = {'pass': all(lost_logged.values()), 'baseline_tokens_sections_2_8': len(btok),
                 'tokens_no_longer_in_document': lost, 'logged_as_removed_duplicates': lost_logged}

    # P3
    s28 = span_2_8(body)
    run = ' '.join(plain_paragraphs(s28, macros))
    cap = float_text(s28, macros, with_cells=False)
    cells = float_text(s28, macros, with_cells=True)
    c_run = measure.count_phrases(run)
    c_cap = measure.count_phrases(run + ' ' + cap)
    c_all = measure.count_phrases(run + ' ' + cells)
    rep['P3'] = {'pass': all(c_cap[k] <= v for k, v in LIMITS.items()), 'limits': LIMITS,
                 'running_text': c_run, 'text_captions_and_notes': c_cap,
                 'including_table_cells': c_all,
                 'over_limit_only_in_table_cells': {k: c_all[k] for k in LIMITS if c_all[k] > LIMITS[k] >= c_cap[k]}}

    # P4
    i_app = body.index('\\appendix')
    lab_pos = {m.group(1): m.start() for m in re.finditer(r'\\label\{([^}]*)\}', body)}
    in_app = {k: lab_pos.get(k, -1) > i_app for k in ['tab:response_lists', 'tab:cost_structure']}
    refs_ok = None
    if log:
        refs_ok = not measure.parse_log(log)['undefined_references']
    rep['P4'] = {'pass': new['tables_before_appendix'] <= 11 and all(in_app.values()) and refs_ok is not False,
                 'tables_before_appendix': new['tables_before_appendix'], 'moved_tables_in_appendix': in_app,
                 'all_refs_resolve': refs_ok}

    # P5
    prim = [g for g in new['paragraphs_by_subsection'] if g['subsection'] == 'Headline comparison']
    pw = prim[0]['paragraph_words'] if prim else []
    disc = section_text(body, 'Discussion')
    facts = {f: f in disc for f in PROTECTED_FACTS}
    res = section_text(body, 'Results')
    rep['P5'] = {'pass': bool('\\label{subsec:dev_to_ho}' in raw and pw and max(pw) <= 120 and all(facts.values()))
                 and 'CODE\\_GENDER} holds rank' not in res,
                 'dev_to_ho_label': '\\label{subsec:dev_to_ho}' in raw, 'primary_results_paragraph_words': pw,
                 'protected_facts_in_discussion': facts, 'protected_paragraph_left_in_results': 'CODE\\_GENDER} holds rank' in res}

    # P6
    over45 = [s for s in new['long_sentences']['sentences_over_45'] if s['section'] not in ('Introduction',) and not s['section'].startswith(('CRediT', 'Funding', 'Disclaimer', 'Declaration', 'Data availability'))]
    over60 = [s for s in over45 if s['words'] > 60]
    rep['P6'] = {'pass': not over60, 'over_60': over60, 'over_45': over45}

    # P7
    concl = [p for p in new['words']['per_section'] if p['section'] == 'Conclusion'][0]['words']
    locs = []
    for blk in measure.split_blocks(s28):
        if '522' in measure.to_plain(measure.running_text(blk['text']), 'words', macros):
            locs.append((blk['section'], blk['subsection']))
    rep['P7'] = {'pass': bool(concl <= 350 and locs and all(l == ('Results', 'Scalability and cost') for l in locs)),
                 'conclusion_words': concl, 'locations_of_522_in_sections_2_8': locs}

    # P8
    def pieces(r, b):
        i = b.index('\\section{Introduction}')
        j = b.index('\\section{Related Work}')
        ab = re.search(r'\\begin\{abstract\}.*?\\end\{abstract\}', r, flags=re.S).group(0)
        kw = re.search(r'\\begin\{keyword\}.*?\\end\{keyword\}', r, flags=re.S).group(0)
        hl = re.search(r'% HIGHLIGHTS.*?\n% -{10,}', r, flags=re.S).group(0)
        return {'introduction': b[i:j], 'abstract': ab, 'keywords': kw, 'highlights': hl}
    pn, pp = pieces(raw, body), pieces(praw, pbody)
    rep['P8'] = {'pass': pn == pp, 'identical': {k: pn[k] == pp[k] for k in pn}}

    order = ['S1', 'S2', 'S3', 'S4', 'S5', 'P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8']
    rep['all_pass'] = all(rep[k]['pass'] for k in order if k in rep)
    if a.output:
        open(a.output, 'w', encoding='utf-8').write(json.dumps(rep, indent=1, ensure_ascii=False) + '\n')
    for k in order:
        if k in rep:
            extra = ''
            if k == 'P1':
                extra = ' (%s%%, %d -> %d words)' % (rep[k]['reduction_percent'], w0, w1)
            print(k, 'PASS' if rep[k]['pass'] else 'FAIL', extra)
    return 0 if rep['all_pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
