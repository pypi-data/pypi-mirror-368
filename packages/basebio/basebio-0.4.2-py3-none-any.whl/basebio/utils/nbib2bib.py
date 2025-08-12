import re

def parse_nbib_to_bibtex(nbib_content):
    entries = nbib_content.strip().split('\n\n')
    bib_entries = []

    for entry in entries:
        lines = entry.strip().split('\n')
        fields = {}
        current_tag = None

        for line in lines:
            if re.match(r'^[A-Z]{2,4}  - ', line):
                tag, value = line.split('  - ', 1)
                current_tag = tag
                fields.setdefault(tag, []).append(value.strip())
            elif line.startswith('      '):  # continuation line
                if current_tag:
                    fields[current_tag][-1] += ' ' + line.strip()

        # Generate BibTeX fields
        author_list = fields.get('AU', ['Unknown'])
        authors = ' and '.join(author_list)
        first_author_lastname = author_list[0].split(',')[0].lower() if author_list else 'unknown'
        year = fields.get('DP', ['n.d.'])[0][:4]

        # BibTeX key
        bibkey = f"{first_author_lastname}{year}"

        # Optional fields
        title = fields.get('TI', ['No Title'])[0]
        journal = fields.get('JT', ['Unknown Journal'])[0]
        doi = fields.get('LID', [''])[0].replace(' [doi]', '')
        url = f"https://doi.org/{doi}" if doi else ''
        volume = fields.get('VI', [''])[0]
        issue = fields.get('IP', [''])[0]
        pages = fields.get('PG', [''])[0]
        issn = fields.get('IS', [''])[0]
        month = 'may'  # You can customize this from DP if needed
        numpages = ''
        if pages and '–' in pages:
            start, end = pages.split('–', 1)
            try:
                numpages = str(int(end.strip()) - int(start.strip()) + 1)
            except:
                numpages = ''

        bib_entry = f"""@article{{{bibkey},
  author       = {{{authors}}},
  title        = {{{title}}},
  year         = {{{year}}},
  issue_date   = {{{fields.get('DP', [''])[0]}}},
  publisher    = {{Oxford University Press, Inc.}},
  address      = {{USA}},
  volume       = {{{volume}}},
  number       = {{{issue}}},
  issn         = {{{issn}}},
  url          = {{{url}}},
  doi          = {{{doi}}},
  journal      = {{{journal}}},
  month        = {{{month}}},
  pages        = {{{pages}}},
  numpages     = {{{numpages}}}
}}"""
        bib_entries.append(bib_entry)

    return '\n\n'.join(bib_entries)


def nbib2bibtex(nbib, bib):
    """
    nbib2bibtex is 

    Arges:
        nbib: input file 
        bib: output file
    Exemple:
        nbib2bibtex(nbib, bib)
    """

    try:
        with open(nbib, 'r', encoding='utf-8') as f:
            nbib_data = f.read()

        bib_output = parse_nbib_to_bibtex(nbib_data)

        with open(bib, 'w', encoding='utf-8') as f:
            f.write(bib_output)

        print(f"✅ 转换完成，已输出至 {bib}")
    except FileNotFoundError:
        print(f"❌ 文件未找到: {nbib}")