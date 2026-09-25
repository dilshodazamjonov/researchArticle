#!/usr/bin/env python3
"""Final self-checks of Prompt 3 (S1-S5, F1-F9; see CHANGES.md, "Files" and "Prompt 3").

Usage (from the repository root):
    python3 tools/check_p3.py [--compile-dir DIR | --log LOG] [-o REPORT.json]

Compares submission/manuscript.tex with baseline/. "Sections 1-8" is the span from
\\section{Introduction} to \\appendix, as in measure.py; the numbered-only figure is
reported beside it. Exit status 0 when every check passes.
"""
import argparse
import json
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import measure            # noqa: E402
import extract_tables     # noqa: E402
import check_p1           # noqa: E402
import check_p2           # noqa: E402

MAIN, SUPP, BMAIN = 'submission/manuscript.tex', 'submission/supplementary.tex', 'baseline/manuscript.tex'
LIMITS = {'materiality bar': 7, 'covariate-shift': 4, 'held-out rule': 0, 'development rule': 0,
          'development-rule': 0, 'most adversarial': 0}
MEASUREMENT = re.compile(r'522|matched (?:\w+ )?measurement|matched conditions')


def section_block(changes, heading_regex):
    """Text of every CHANGES.md section whose heading line matches heading_regex."""
    out = []
    for m in re.finditer(r'^(#{2,3}) (.+)$', changes, flags=re.M):
        if re.search(heading_regex, m.group(2)):
            level = len(m.group(1))
            nxt = re.compile(r'^#{2,%d} ' % level, flags=re.M).search(changes, m.end())
            out.append(changes[m.end():nxt.start() if nxt else len(changes)])
    return '\n'.join(out).replace('\u2212', '-')


def span_1_8(body):
    return body[body.index('\\section{Introduction}'):body.index('\\appendix')]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--compile-dir')
    ap.add_argument('--log')
    ap.add_argument('-o', '--output')
    a = ap.parse_args(argv)
    rep = {}
    bm = json.load(open('baseline/metrics.json'))
    raw, macros, body, verb = check_p2.src_of(MAIN)
    braw, bmacros, bbody, bverb = check_p2.src_of(BMAIN)
    changes = open('CHANGES.md', encoding='utf-8').read()
    new = measure.measure(MAIN)

    # S1
    codes, log = None, a.log
    if a.compile_dir:
        codes, log = check_p1.compile_twice(MAIN, a.compile_dir)
    lg = measure.parse_log(log)
    rep['S1'] = {'pass': (codes is None or codes == [0, 0]) and not lg['undefined_references']
                 and not lg['undefined_citations'] and not lg['there_were_undefined_references']
                 and lg['overfull_hbox'] <= bm['compile']['overfull_hbox'] + 2,
                 'pdflatex_exit_codes': codes, 'overfull_hbox': lg['overfull_hbox'],
                 'baseline_overfull_hbox': bm['compile']['overfull_hbox'], 'underfull_hbox': lg['underfull_hbox'],
                 'undefined_references': lg['undefined_references'], 'undefined_citations': lg['undefined_citations'],
                 'labels_may_have_changed_after_pass2': lg['labels_may_have_changed'], 'pages': lg['pages'],
                 'log': log}

    # S2
    missing = [k for k in bm['labels'] if k not in new['labels']]
    bib = check_p1.bibliography(MAIN) == check_p1.bibliography(BMAIN)
    rep['S2'] = {'pass': not missing and set(new['cite_keys']) == set(bm['cite_keys']) and bib and not new['labels_duplicated'],
                 'missing_labels': missing, 'new_labels': [k for k in new['labels'] if k not in bm['labels']],
                 'cite_keys_equal': set(new['cite_keys']) == set(bm['cite_keys']), 'thebibliography_identical': bib}

    # S3: table bodies against baseline, except the documented Prompt 1 additions
    bt = json.load(open('baseline/tables.json'))
    nt = {r['label']: (r['body'], r['colspec']) for p in (MAIN, SUPP) for r in extract_tables.extract(p)}
    diffs, bad = {}, []
    for lab in sorted(set(bt['tables']) | set(nt)):
        old = (bt['tables'].get(lab), bt['colspecs'].get(lab))
        if old == nt.get(lab):
            continue
        orows, nrows = check_p1.rows(old[0] or ''), check_p1.rows(nt.get(lab, ('', ''))[0])
        inserted = [r for r in nrows if r not in orows]
        kept = [r for r in nrows if r in orows] == orows
        diffs[lab] = {'rows_inserted': inserted, 'existing_rows_unchanged_and_in_order': kept,
                      'colspec_changed': old[1] != nt.get(lab, ('', ''))[1]}
        ok = (lab == 'tab:robustness' and kept and len(inserted) == 1 and inserted[0].startswith('\\addlinespace Five per-fold responses')
              and old[1] == nt[lab][1])
        if not ok:
            bad.append(lab)
    rep['S3'] = {'pass': not bad, 'tables_compared': len(set(bt['tables']) | set(nt)), 'differing': diffs,
                 'unexpected': bad, 'note': 'tab:response_spread received a table note only; its body is unchanged'}

    # S4
    supp = check_p2.src_of(SUPP)
    base_tokens = set(bm['numbers']['all_body']) | set(bm['supplement']['numbers_all_body'])
    new_tokens = set(new['numbers']['all_body']) | set(measure.all_body_numbers(supp[2], supp[3], supp[1]))
    absent = sorted(new_tokens - base_tokens)
    dn = section_block(changes, r'^Derived numbers')
    logged = {t: bool(re.search(r'(?<![\d.])' + re.escape(t) + r'(?![\d])', dn)) for t in absent}
    rep['S4'] = {'pass': all(logged.values()), 'tokens_absent_from_baseline': absent, 'logged': logged}

    # S5
    b5, n5 = check_p1.r6_blocks(BMAIN), check_p1.r6_blocks(MAIN)
    rep['S5'] = {'pass': all(b5[k] == n5.get(k) for k in b5) and all(b5.values()),
                 'differing': [k for k in b5 if b5[k] != n5.get(k)], 'blocks_compared': list(b5)}

    # F1
    w_incl = new['words']['sections_1_8']
    w_num = new['words']['sections_1_8_numbered_only']
    intro0 = [p['words'] for p in bm['words']['per_section'] if p['section'] == 'Introduction'][0]
    intro1 = [p['words'] for p in new['words']['per_section'] if p['section'] == 'Introduction'][0]
    r_incl = 100 * (1 - w_incl / bm['words']['sections_1_8'])
    r_num = 100 * (1 - w_num / bm['words']['sections_1_8_numbered_only'])
    r_intro = 100 * (1 - intro1 / intro0)
    rep['F1'] = {'pass': r_incl >= 25 and r_num >= 25 and r_intro >= 20,
                 'sections_1_8_words': [bm['words']['sections_1_8'], w_incl], 'reduction_percent': round(r_incl, 1),
                 'numbered_only_words': [bm['words']['sections_1_8_numbered_only'], w_num], 'numbered_only_reduction_percent': round(r_num, 1),
                 'introduction_words': [intro0, intro1], 'introduction_reduction_percent': round(r_intro, 1)}

    # F2: numeric tokens of the baseline abstract and Sections 1-8 (text, captions, notes, cells)
    babs = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', bbody, flags=re.S).group(1)
    btok = set(measure.all_body_numbers(babs + '\n\n' + span_1_8(bbody), bverb, bmacros))
    lost = sorted(btok - set(new['numbers']['all_body']))
    rd = section_block(changes, r'^Removed duplicates')
    lost_logged = {t: bool(re.search('`' + re.escape(t) + '`', rd)) for t in lost}
    rep['F2'] = {'pass': all(lost_logged.values()), 'baseline_tokens': len(btok), 'lost': lost, 'logged': lost_logged}

    # F3
    kw0 = set(bm['keywords']['list'])
    hl = new['highlights']
    rep['F3'] = {'pass': new['words']['abstract'] <= 250 and 3 <= len(hl) <= 5 and all(h['chars'] <= 85 for h in hl)
                 and set(new['keywords']['list']) == kw0 and new['keywords']['count'] == 7,
                 'abstract_words': new['words']['abstract'], 'highlights': [(h['chars'], h['text']) for h in hl],
                 'keywords': new['keywords']['list'], 'same_seven': set(new['keywords']['list']) == kw0}

    # F4: every number in the abstract, highlights and Conclusion traced in CHANGES.md
    abs_src = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', body, flags=re.S).group(1)
    concl_src = check_p2.section_text(body, 'Conclusion')
    tok = {'abstract': measure.numbers(measure.to_plain(abs_src, 'numbers', macros)),
           'highlights': [t for h in hl for t in measure.numbers(h['text'])],
           'conclusion': [t for p in measure.paragraphs(measure.running_text(concl_src))
                          for t in measure.numbers(measure.to_plain(p, 'numbers', macros))]}
    trace = section_block(changes, r'^Number trace')
    traced = {k: {t: bool(re.search('`' + re.escape(t) + '`', trace)) for t in sorted(set(v))} for k, v in tok.items()}
    rep['F4'] = {'pass': all(all(v.values()) for v in traced.values()), 'traced': traced}

    # F5: counts across the abstract and Sections 1-8
    s18 = span_1_8(body)
    run = measure.to_plain(abs_src, 'words', macros) + ' ' + ' '.join(check_p2.plain_paragraphs(s18, macros))
    cap = check_p2.float_text(s18, macros, with_cells=False)
    cells = check_p2.float_text(s18, macros, with_cells=True)
    c_cap = measure.count_phrases(run + ' ' + cap)
    c_all = measure.count_phrases(run + ' ' + cells)
    rep['F5'] = {'pass': all(c_cap[k] <= v for k, v in LIMITS.items()), 'limits': LIMITS,
                 'running_text': measure.count_phrases(run), 'text_captions_and_notes': c_cap,
                 'including_table_cells': c_all,
                 'over_limit_only_in_table_cells': {k: c_all[k] for k in LIMITS if c_all[k] > LIMITS[k] >= c_cap[k]}}

    # F6: the 522 s / 21 s measurement
    places, ok6 = [], True
    frags = [('abstract', abs_src)] + [((b['section'], b['subsection']), b['text']) for b in measure.split_blocks(body[body.index('\\section{Introduction}'):])]
    for where, frag in frags:
        for p in measure.paragraphs(measure.running_text(frag)):
            plain = measure.to_plain(p, 'words', macros)
            if MEASUREMENT.search(plain):
                has = 'unscreened 1,959-feature universe' in plain
                places.append({'where': where, 'has_522': '522' in plain, 'says_unscreened': has, 'text': plain[:120]})
                ok6 = ok6 and has
    with522 = [p['where'] for p in places if p['has_522']]
    allowed = all(w == 'abstract' or w == ('Introduction', None) or w == ('Results', 'Scalability and cost') for w in with522)
    intro_once = sum(1 for w in with522 if w == ('Introduction', None)) == 1
    rep['F6'] = {'pass': ok6 and allowed and intro_once and ('Results', 'Scalability and cost') in with522,
                 'paragraphs_citing_the_measurement': places, 'paragraphs_with_522': with522}

    # F7
    intro = check_p2.section_text(body, 'Introduction')
    enum = re.search(r'\\begin\{enumerate\}(.*?)\\end\{enumerate\}', intro, flags=re.S)
    items = re.split(r'\\item\b', enum.group(1))[1:] if enum else []
    item_sent = [len(measure.split_sentences(measure.to_plain(i, 'words', macros))) for i in items]
    c4 = 'univariate filter such as IV' in body and 'would shrink the mRMR pool by the same factor' in body
    c5 = 'did not measure how cost scales' in body and 'context-window' in body
    rep['F7'] = {'pass': bool(items) and len(items) <= 4 and all(n <= 2 for n in item_sent) and c4 and c5,
                 'contribution_items': len(items), 'sentences_per_item': item_sent,
                 'c4_sentence': c4, 'c5_paragraph': c5}

    # F8
    sents = check_p1.document_sentences(MAIN)
    immat = [{'where': w, 'sentence': s} for w, s in sents if 'immaterial' in s.lower()]
    over = [x for x in immat if re.search(r'all three datasets|all four|every case|all six', x['sentence'], re.I)
            and 'three of the four' not in x['sentence']]
    rep['F8'] = {'pass': not over, 'sentences_with_immaterial': immat, 'overclaiming': over}

    # F9
    over60 = [s for s in new['long_sentences']['sentences_over_60']]
    concl = [p['words'] for p in new['words']['per_section'] if p['section'] == 'Conclusion'][0]
    rep['F9'] = {'pass': not over60 and concl <= 380, 'sentences_over_60': over60,
                 'sentences_over_45': [(s['words'], s['section'], s['text'][:90]) for s in new['long_sentences']['sentences_over_45']],
                 'conclusion_words': concl}

    order = ['S1', 'S2', 'S3', 'S4', 'S5', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9']
    rep['all_pass'] = all(rep[k]['pass'] for k in order)
    if a.output:
        open(a.output, 'w', encoding='utf-8').write(json.dumps(rep, indent=1, ensure_ascii=False, default=str) + '\n')
    for k in order:
        print(k, 'PASS' if rep[k]['pass'] else 'FAIL')
    return 0 if rep['all_pass'] else 1


if __name__ == '__main__':
    sys.exit(main())
