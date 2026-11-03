#!/usr/bin/env python3
"""Manuscript metrics for the Big Data Research revision.

Usage:
    python3 tools/measure.py MAIN.tex [--supplement SUPP.tex] [--log MAIN.log] [-o OUT.json]

Writes one JSON object (to OUT.json, or to stdout). The specification, and the
conventions used for words, sentences and numeric tokens, are given in CHANGES.md
under "Files". Only the Python standard library is used.
"""
import argparse
import hashlib
import json
import re
import sys
from collections import Counter

NBSP = '\u00a0'          # stands for ~ and "\ ": separates words, never ends a sentence
THOUSANDS = '\u0001'     # protects {,} in maths while ordinary maths commas are spaced

PHRASES = ['materiality bar', 'covariate-shift', 'not adjusted', 'descriptive',
           'held-out rule', 'development rule', 'development-rule', 'most adversarial']

FLOAT_ENVS = ['table', 'table*', 'figure', 'figure*']
DISPLAY_ENVS = ['equation', 'equation*', 'align', 'align*', 'gather', 'gather*',
                'multline', 'multline*', 'eqnarray', 'eqnarray*', 'displaymath']
DROP_ENVS = ['lstlisting', 'thebibliography', 'tikzpicture']

ABBREVIATIONS = {'al.', 'e.g.', 'i.e.', 'cf.', 'vs.', 'Eq.', 'Eqs.', 'Fig.', 'Figs.',
                 'Sec.', 'Secs.', 'No.', 'approx.', 'resp.', 'viz.'}

NUM_RE = re.compile(
    r'(?<![\w.,])'                       # not glued to a word, a decimal point or a comma
    r'([+\-\u2212]?)'                    # optional sign
    r'(\d{4}-\d{2}(?:-\d{2})?(?!\d)'     # ISO date or year-month, one token
    r'|\d{1,3}(?:,\d{3})+(?:\.\d+)?'     # thousands separators: 1,068 or 1,157,512
    r'|\d+(?:\.\d+)*)'                   # integer, decimal or dotted version number
    r'(?!\w)')


# --------------------------------------------------------------------------- basic parsing

def read(path):
    with open(path, encoding='utf-8') as fh:
        return fh.read()


def match_brace(s, i):
    """s[i] is '{'; return the index of its matching '}' (escaped braces are skipped)."""
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


def skip_optional(s, j):
    """Skip spaces and any [..] optional arguments starting at j; return the new index."""
    while True:
        k = j
        while k < len(s) and s[k] in ' \t\n':
            k += 1
        if k < len(s) and s[k] == '[':
            depth = 0
            while k < len(s):
                if s[k] == '[':
                    depth += 1
                elif s[k] == ']':
                    depth -= 1
                    if depth == 0:
                        break
                k += 1
            j = k + 1
        else:
            return j


def sub_command(s, names, fn, nargs=1):
    """Replace \\name[*][opt]{arg1}...{argN} by fn(list_of_args)."""
    pat = re.compile(r'\\(' + '|'.join(re.escape(n) for n in names) + r')(?![A-Za-z])\*?')
    out = []
    pos = 0
    while True:
        m = pat.search(s, pos)
        if not m:
            out.append(s[pos:])
            break
        j = skip_optional(s, m.end())
        args = []
        ok = True
        for _ in range(nargs):
            k = j
            while k < len(s) and s[k] in ' \t\n':
                k += 1
            if k >= len(s) or s[k] != '{':
                ok = False
                break
            e = match_brace(s, k)
            args.append(s[k + 1:e])
            j = e + 1
        if not ok:
            out.append(s[pos:m.end()])
            pos = m.end()
            continue
        out.append(s[pos:m.start()])
        out.append(fn(args))
        pos = j
    return ''.join(out)


def protect_verbatim(s):
    """Replace lstlisting blocks by placeholders; return (text, blocks)."""
    blocks = []

    def keep(m):
        blocks.append(m.group(0))
        return '\\VERBATIMBLOCK{%d}' % (len(blocks) - 1)
    return re.sub(r'\\begin\{lstlisting\}.*?\\end\{lstlisting\}', keep, s, flags=re.S), blocks


def strip_comments(s):
    """Remove % comments; like TeX, the end of line and the next line's indentation go too."""
    return re.sub(r'(?<!\\)%[^\n]*(?:\n[ \t]*)?', '', s)


def env_spans(s, names):
    """Top-level spans (start, end) of environments whose name is in names."""
    pat = re.compile(r'\\(begin|end)\{(' + '|'.join(re.escape(n) for n in names) + r')\}')
    spans, stack = [], []
    for m in pat.finditer(s):
        if m.group(1) == 'begin':
            stack.append((m.group(2), m.start()))
        elif stack and stack[-1][0] == m.group(2):
            _, start = stack.pop()
            if not stack:
                spans.append((start, m.end()))
    return spans


def remove_spans(s, spans, repl='\n'):
    out, pos = [], 0
    for a, b in spans:
        out.append(s[pos:a])
        out.append(repl)
        pos = b
    out.append(s[pos:])
    return ''.join(out)


def remove_envs(s, names, repl='\n'):
    return remove_spans(s, env_spans(s, names), repl)


def zero_arg_macros(src):
    """User macros defined with \\newcommand{\\X}{...} and no arguments."""
    macros = {}
    for m in re.finditer(r'\\(?:re)?newcommand\{\\([A-Za-z]+)\}\s*\{', src):
        e = match_brace(src, m.end() - 1)
        macros[m.group(1)] = src[m.end():e]
    return macros


def expand_macros(s, macros):
    for name, body in macros.items():
        s = re.sub(r'\\' + name + r'(?![A-Za-z])\s?', lambda _m, b=body: b + ' ', s)
    return s


# --------------------------------------------------------------------------- text conversion

def inline_math_split(s):
    """Yield (is_math, chunk) over s, splitting at unescaped $...$ and \\(...\\)."""
    parts, buf, i, in_math = [], [], 0, False
    while i < len(s):
        if s.startswith('\\(', i) and not in_math:
            parts.append((False, ''.join(buf))); buf = []; in_math = True; i += 2; continue
        if s.startswith('\\)', i) and in_math:
            parts.append((True, ''.join(buf))); buf = []; in_math = False; i += 2; continue
        c = s[i]
        if c == '\\' and i + 1 < len(s):
            buf.append(s[i:i + 2]); i += 2; continue
        if c == '$':
            parts.append((in_math, ''.join(buf))); buf = []; in_math = not in_math; i += 1; continue
        buf.append(c); i += 1
    parts.append((in_math, ''.join(buf)))
    return parts


def math_numbers_text(m):
    """Maths content reduced to something the number pattern can read."""
    m = m.replace('{,}', THOUSANDS).replace(',', ', ').replace(THOUSANDS, ',')
    m = re.sub(r'\\[A-Za-z]+', ' ', m)
    m = re.sub(r'\\.', ' ', m)
    m = re.sub(r'[{}^_&]', ' ', m)
    return ' ' + m + ' '


def text_commands(s):
    """Text-mode markup to plain text (after refs, cites, maths and verbatim are handled)."""
    s = s.replace('---', '\u2014').replace('--', '\u2013')
    s = s.replace('``', '"').replace("''", '"')
    s = re.sub(r'\\\\(\[[^\]]*\])?', ' ', s)                 # \\ and \\[2pt]
    s = re.sub(r'\\(newline|par|linebreak|noindent|clearpage|newpage|appendix|centering|'
               r'sloppy|raggedright|footnotesize|scriptsize|small|normalsize|tiny)(?![A-Za-z])',
               ' ', s)
    s = re.sub(r'\\[A-Za-z]+\s*=\s*-?[\d.]+[a-z]*', ' ', s)  # TeX assignments (\hbadness=10000)
    s = sub_command(s, ['setcounter', 'addtocounter', 'setlength', 'renewcommand'],
                    lambda a: ' ', nargs=2)
    s = sub_command(s, ['vspace', 'hspace', 'vskip', 'hskip', 'begin', 'end'], lambda a: ' ')
    s = s.replace('~', NBSP).replace('\\ ', NBSP).replace('\\,', NBSP)
    s = s.replace('\\-', '').replace('\\allowbreak', '').replace('\\slash', '/')
    for a, b in [('\\_', '_'), ('\\%', '%'), ('\\&', '&'), ('\\#', '#'), ('\\$', '$'),
                 ('\\{', '{'), ('\\}', '}')]:
        s = s.replace(a, b)
    s = re.sub(r'\\(ldots|dots)(?![A-Za-z])', '...', s)
    s = re.sub(r'\\[A-Za-z]+\*?', '', s)                        # any other command name
    s = s.replace('{', '').replace('}', '')
    return s


def to_plain(s, mode, macros):
    """LaTeX fragment -> plain text.

    mode 'words':   inline maths -> MATH, \\ref -> REF, \\url/\\path -> URL (one word each)
    mode 'numbers': inline maths kept (commands dropped, maths commas spaced), refs,
                    cites, labels, urls and paths removed.
    """
    s = expand_macros(s, macros)
    s = sub_command(s, ['label'], lambda a: '')
    s = sub_command(s, ['cite', 'citep', 'citet', 'citealp'], lambda a: '')
    ref = ' REF ' if mode == 'words' else ' '
    s = sub_command(s, ['ref', 'eqref', 'pageref', 'autoref', 'cref', 'Cref'], lambda a: ref)
    url = ' URL ' if mode == 'words' else ' '
    s = sub_command(s, ['url', 'path', 'nolinkurl'], lambda a: url)
    s = sub_command(s, ['href'], lambda a: a[1], nargs=2)
    out = []
    for is_math, chunk in inline_math_split(s):
        if is_math:
            out.append(' MATH ' if mode == 'words' else math_numbers_text(chunk))
        else:
            out.append(text_commands(chunk))
    s = ''.join(out)
    s = re.sub(r'[ \t\r\n]+', ' ', s)
    return s.strip(' ')


def words(text):
    return [t for t in re.split(r'[\s\u00a0]+', text) if re.search(r'[^\W_]', t)]


def split_sentences(text):
    sentences, start = [], 0
    for m in re.finditer(r'[.!?]["\u201d\u2019)\]]*( +)(?=[A-Z0-9(\[\u201c"\u2018\'`$])', text):
        head = text[start:m.start() + 1].split()
        last = head[-1] if head else ''
        if last in ABBREVIATIONS or re.fullmatch(r'[A-Z]\.', last):
            continue
        sentences.append(text[start:m.start(1)].strip())
        start = m.end()
    sentences.append(text[start:].strip())
    return [x for x in sentences if x]


def numbers(text):
    toks = []
    for m in NUM_RE.finditer(text):
        sign = m.group(1).replace('\u2212', '-')
        toks.append(sign + m.group(2))
    return toks


# --------------------------------------------------------------------------- document structure

HEAD_RE = re.compile(r'\\(section|subsection|subsubsection)(\*?)\s*\{')


def split_blocks(s):
    """Split s at \\section, \\subsection and \\subsubsection headings.

    Returns a list of dicts: section, starred, subsection, subsubsection, text.
    """
    blocks = []
    cur = {'section': '(before first heading)', 'starred': False, 'subsection': None,
           'subsubsection': None}
    pos = 0
    for m in HEAD_RE.finditer(s):
        if m.start() < pos:
            continue
        blocks.append(dict(cur, text=s[pos:m.start()]))
        e = match_brace(s, m.end() - 1)
        title = re.sub(r'\s+', ' ', s[m.end():e]).strip()
        level = m.group(1)
        if level == 'section':
            cur = {'section': title, 'starred': m.group(2) == '*', 'subsection': None,
                   'subsubsection': None}
        elif level == 'subsection':
            cur = dict(cur, subsection=title, subsubsection=None)
        else:
            cur = dict(cur, subsubsection=title)
        pos = e + 1
    blocks.append(dict(cur, text=s[pos:]))
    return [b for b in blocks if b['text'].strip() or b is blocks[-1]]


HOLE = '\u0002'   # marks removed material until the surrounding line breaks are settled


def close_holes(s, joiner):
    """A removed block on its own lines inside a paragraph must not leave a blank line."""
    s = re.sub(r'(?<!\n)\n[ \t]*' + HOLE + r'[ \t]*\n(?![ \t]*\n)', joiner, s)
    return s.replace(HOLE, ' ')


def running_text(s):
    """Remove floats, display maths, captions, verbatim, bibliography and TikZ."""
    s = close_holes(remove_envs(s, FLOAT_ENVS, HOLE), '\n')
    s = remove_envs(s, DISPLAY_ENVS, HOLE)
    s = re.sub(r'\\\[.*?\\\]', HOLE, s, flags=re.S)
    s = re.sub(r'\$\$.*?\$\$', HOLE, s, flags=re.S)
    s = close_holes(s, ' ')
    s = remove_envs(s, DROP_ENVS)
    s = sub_command(s, ['caption'], lambda a: ' ')
    s = re.sub(r'\\VERBATIMBLOCK\{\d+\}', '\n\n', s)
    return s


def paragraphs(s):
    """Running-text LaTeX -> list of paragraph fragments (blank lines, \\par and \\item split)."""
    s = sub_command(s, ['paragraph'], lambda a: '\n\n')      # run-in headings: title dropped
    s = re.sub(r'\\item(\[[^\]]*\])?', '\n\n', s)
    s = re.sub(r'\\(begin|end)\{(itemize|enumerate|description)\}', '\n\n', s)
    s = re.sub(r'\\par(?![A-Za-z])', '\n\n', s)
    return [p for p in re.split(r'\n[ \t]*\n', s) if p.strip()]


def count_phrases(text):
    low = re.sub(r'[\s\u00a0]+', ' ', text).lower()
    return {p: low.count(p) for p in PHRASES}


def all_body_numbers(body, verbatim, macros):
    """Numeric tokens of the whole body: floats, captions, maths, verbatim and figure code
    included; comments and the bibliography excluded."""
    s = remove_envs(body, ['thebibliography'])
    s = re.sub(r'\\VERBATIMBLOCK\{(\d+)\}', lambda m: '\n' + verbatim[int(m.group(1))] + '\n', s)
    # figure code: commas separate list items, as in maths
    s = re.sub(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}',
               lambda m: m.group(0).replace('{,}', THOUSANDS).replace(',', ', ').replace(THOUSANDS, '{,}'),
               s, flags=re.S)
    # display maths is read as maths
    for name in DISPLAY_ENVS:
        s = re.sub(r'\\begin\{' + re.escape(name) + r'\}(.*?)\\end\{' + re.escape(name) + r'\}',
                   lambda m: math_numbers_text(m.group(1)), s, flags=re.S)
    s = re.sub(r'\\\[(.*?)\\\]', lambda m: math_numbers_text(m.group(1)), s, flags=re.S)
    return numbers(to_plain(s, 'numbers', macros))


def body_of(src):
    a = src.find('\\begin{document}')
    b = src.rfind('\\end{document}')
    return src[a + len('\\begin{document}'):b] if a >= 0 else src


def highlights(raw):
    lines = raw.split('\n')
    out, on = [], False
    for line in lines:
        if re.match(r'\s*%\s*HIGHLIGHTS', line):
            on = True
            continue
        if on:
            m = re.match(r'\s*%\s*-\s+(.*\S)\s*$', line)
            if m:
                out.append(m.group(1))
            elif re.match(r'\s*%\s*-{3,}', line) or not line.strip().startswith('%'):
                break
    return [{'text': h, 'chars': len(h)} for h in out]


def keywords(body):
    m = re.search(r'\\begin\{keyword\}(.*?)\\end\{keyword\}', body, flags=re.S)
    if not m:
        return {'count': 0, 'list': []}
    items = [re.sub(r'\s+', ' ', k).strip() for k in m.group(1).split('\\sep')]
    items = [k for k in items if k]
    return {'count': len(items), 'list': items}


def parse_log(path):
    log = open(path, encoding='latin-1').read()
    joined = log.replace('\n', '')
    refs = sorted(set(re.findall(r"LaTeX Warning: Reference `([^']*)' on page", joined)))
    cites = sorted(set(re.findall(r"LaTeX Warning: Citation `([^']*)' on page", joined)))
    pages = re.search(r'Output written on .*?\((\d+) pages?', joined)
    return {
        'log': path,
        'overfull_hbox': len(re.findall(r'^Overfull \\hbox', log, flags=re.M)),
        'underfull_hbox': len(re.findall(r'^Underfull \\hbox', log, flags=re.M)),
        'overfull_vbox': len(re.findall(r'^Overfull \\vbox', log, flags=re.M)),
        'undefined_references': refs,
        'undefined_citations': cites,
        'there_were_undefined_references': 'There were undefined references' in joined,
        'labels_may_have_changed': 'Label(s) may have changed' in joined,
        'multiply_defined_labels': sorted(set(re.findall(r"Label `([^']*)' multiply defined", joined))),
        'pages': int(pages.group(1)) if pages else None,
    }


def sorted_counter(c):
    return dict(sorted(c.items(), key=lambda kv: (kv[0].lstrip('+-'), kv[0])))


# --------------------------------------------------------------------------- measurement

def measure(path):
    raw = read(path)
    macros = zero_arg_macros(raw)
    prot, verbatim = protect_verbatim(raw)
    src = strip_comments(prot)
    body = body_of(src)
    result = {'file': path, 'sha256': hashlib.sha256(raw.encode('utf-8')).hexdigest()}

    # abstract
    mabs = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', body, flags=re.S)
    abstract_src = mabs.group(1) if mabs else ''
    abstract = to_plain(abstract_src, 'words', macros)

    # Sections 1-8: \section{Introduction} to \appendix
    i0 = body.find('\\section{Introduction}')
    i1 = body.find('\\appendix')
    span = body[i0:i1] if i0 >= 0 and i1 > i0 else ''

    per_section, groups, long45, long60 = [], [], [], []
    total = numbered_total = 0
    running_all = []
    for blk in split_blocks(span):
        paras = paragraphs(running_text(blk['text']))
        wc = []
        for p in paras:
            plain = to_plain(p, 'words', macros)
            n = len(words(plain))
            if n == 0:
                continue
            wc.append(n)
            running_all.append(plain)
            for sent in split_sentences(plain):
                k = len(words(sent))
                rec = {'words': k, 'section': blk['section'], 'subsection': blk['subsection'],
                       'subsubsection': blk['subsubsection'], 'text': sent}
                if k > 45:
                    long45.append(rec)
                if k > 60:
                    long60.append(rec)
        n_blk = sum(wc)
        total += n_blk
        if not blk['starred']:
            numbered_total += n_blk
        if per_section and per_section[-1]['section'] == blk['section']:
            per_section[-1]['words'] += n_blk
        else:
            per_section.append({'section': blk['section'], 'starred': blk['starred'], 'words': n_blk})
        if wc:
            groups.append({'section': blk['section'], 'subsection': blk['subsection'],
                           'subsubsection': blk['subsubsection'], 'paragraph_words': wc,
                           'words': n_blk})

    running_s18 = ' '.join(running_all)
    all_s18 = to_plain(remove_envs(span, ['tikzpicture']), 'words', macros)

    # numeric tokens, running text
    def running_numbers(fragment):
        toks = []
        for p in paragraphs(running_text(fragment)):
            toks += numbers(to_plain(p, 'numbers', macros))
        return toks
    fm_end = body.find('\\end{frontmatter}')
    whole_running = abstract_src + '\n\n' + (body[fm_end:] if fm_end >= 0 else body)

    result.update({
        'words': {
            'sections_1_8': total,
            'sections_1_8_numbered_only': numbered_total,
            'per_section': per_section,
            'abstract': len(words(abstract)),
        },
        'paragraphs_by_subsection': groups,
        'long_sentences': {
            'over_45': len(long45),
            'over_60': len(long60),
            'sentences_over_45': long45,
            'sentences_over_60': long60,
        },
        'phrase_counts': {
            'running_text_sections_1_8': count_phrases(running_s18),
            'sections_1_8_including_floats_and_captions': count_phrases(all_s18),
        },
        'tables_before_appendix': len(re.findall(r'\\begin\{table\*?\}', body[:i1] if i1 >= 0 else body)),
        'labels': re.findall(r'\\label\{([^}]*)\}', src),
        'cite_keys': sorted({k.strip() for g in re.findall(r'\\cite[pt]?\*?(?:\[[^\]]*\])?\{([^}]*)\}', src)
                             for k in g.split(',') if k.strip()}),
        'numbers': {
            'running_text_whole_document': sorted_counter(Counter(running_numbers(whole_running))),
            'running_text_sections_1_8': sorted_counter(Counter(running_numbers(span))),
            'all_body': sorted_counter(Counter(all_body_numbers(body, verbatim, macros))),
        },
        'highlights': highlights(raw),
        'keywords': keywords(body),
    })
    dup = [k for k, v in Counter(result['labels']).items() if v > 1]
    result['labels_duplicated'] = dup
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('tex')
    ap.add_argument('--supplement', help='supplementary .tex: its numeric tokens are added')
    ap.add_argument('--log', help='pdflatex log of MAIN (final pass): overfull boxes, undefined refs/cites')
    ap.add_argument('-o', '--output')
    a = ap.parse_args(argv)
    res = measure(a.tex)
    if a.supplement:
        raw = read(a.supplement)
        macros = zero_arg_macros(raw)
        prot, verbatim = protect_verbatim(raw)
        body = body_of(strip_comments(prot))
        res['supplement'] = {
            'file': a.supplement,
            'sha256': hashlib.sha256(raw.encode('utf-8')).hexdigest(),
            'numbers_all_body': sorted_counter(Counter(all_body_numbers(body, verbatim, macros))),
        }
    if a.log:
        res['compile'] = parse_log(a.log)
    text = json.dumps(res, indent=1, ensure_ascii=False)
    if a.output:
        with open(a.output, 'w', encoding='utf-8') as fh:
            fh.write(text + '\n')
    else:
        print(text)


if __name__ == '__main__':
    main()
