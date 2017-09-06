from lingpy import *
from pyconcepticon.api import Concepticon
from lingpy.compare.partial import Partial

def get_changer():
    changer = {
                "alignment": "Alignment",
                "doculect": "Language_name",
                "language_id": "Language_ID",
                "concept": "Parameter_name",
                "concepticon_id": "Parameter_ID",
                "original_entry": "Value",
                "ipa": "Form",
                "tokens": "Segments",
                "source": "Source",
                "morphemes": "Motivation_structure",
                "note": "Comment"
            }
    header = ['doculect', 'language_id', 'concept', 'concepticon_id',
            'original_entry',
        'ipa', 'tokens', 'morphemes', 'source', 'note']
    return header, changer

def make_base_list(wordlist, name):
    header, changer = get_changer()
    out = [['ID']+ [changer[h] for h in header]]
    
    langs = {a: b for a, b in csv2list('languages.tsv')}
    wordlist.add_entries('language_id', 'doculect', lambda x: langs[x])
    for k, lang, source in iter_rows(wordlist, 'doculect', 'source'):
        if lang == 'Old_Burmese':
            wordlist[k, 'source'] = 'Okell1971,Luce1985,Nishi1999'
        else:
            wordlist[k, 'source'] = 'Huang1992,Matisoff2015'
            
    for k in wordlist:
        tmp = [str(k)]
        for h in header:
            elm = wordlist[k, h]
            if isinstance(elm, list):
                elm = ' '.join([str(x) for x in elm])
            tmp += [elm]
        out += [tmp]
    with open(name, 'w') as f:
        for line in out:
            print(line)
            f.write('\t'.join(line)+'\n')

def make_cognates(wordlist, name):
    
    part = Partial(wordlist)
    part.add_cognate_ids('cogids', 'strictid')

    out = [['Word_ID', 'Form', 'Cognate_set_ID', 'Segments', 'Alignment', 'Doubt',
        'Cognate_detection_method', 'Cognate_source', 'Alignment_method',
        'Alignment_source']]
    for k, form, seg, cog, alm in iter_rows(part, 'ipa', 'tokens', 'strictid',
            'alignment'):
        out += [[str(k), form, str(cog), ' '.join(seg), ' '.join(alm), '', 'expert', 'Hill2017',
            'LingPy:SCA', '']]
    with open(name, 'w') as f:
        for line in out:
            f.write('\t'.join(line)+'\n')

def make_partial(wordlist, name):
    out = [['Word_ID', 'Form', 'Cognate_set_ID', 'Alignment', 'Doubt',
        'Cognate_detection_method', 'Cognate_source', 'Alignment_method',
        'Alignment_source', 'SegmentSlice']]
    for k, form, cogs, alm in iter_rows(wordlist, 'tokens', 'cogids',
            'alignment'):
        for i, cog in enumerate(cogs):
            out += [[str(k), ' '.join(form), str(cog), ' '.join(alm), '', 'expert', 'Hill2017',
                'LingPy:SCA', '', "{0},{1}".format(i, i+1)]]
    with open(name, 'w') as f:
        for line in out:
            f.write('\t'.join(line)+'\n')

if __name__ == "__main__":
    wl = Wordlist('d_bed.tsv')
    make_base_list(wl, 'cldf/forms.tsv')
    make_cognates(wl, 'cldf/cognates.tsv')
    make_partial(wl, 'cldf/partial.tsv')
