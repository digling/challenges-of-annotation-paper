"""
Scripts compares the data in the BED with the cognate annotations in STEDT.

# Usage
$ python3 compare.py

# Output

Statistics in form of B-Cubed scores (indicating similarities in terms of
cognate judgments), as well as statistics on coverage.

# Requires

lingpy

"""
from lingpy import *
from lingpy.compare.partial import Partial
from lingpy.evaluate.acd import partial_bcubes


wl1 = Wordlist('d_bed.tsv')
wl2 = Wordlist('d_stedt.tsv')

# get original taxa in burmish.tsv
bed2stedt, stedt2bed = {}, {}
for idx, taxon, otax in iter_rows(wl1, 'doculect', 'original_taxname'):
    bed2stedt[taxon] = otax.replace(' TBL', '')
    stedt2bed[otax] = taxon

# start comparison
counts = 0
analyses = {}
nfound = 0
new_rns = {}
new_id = 10000
etym_count, pcog_count = 0, 0
bed_words = 0
for t1, t2 in bed2stedt.items():
    idxsA = wl1.get_list(col=t1, flat=True)
    if t1 != 'Old_Burmese':
        idxsB = wl2.get_list(col=t2, flat=True)

        # now get the tbl ids
        tmp = {wl2[idx, 'srcid'].split('.')[0]: (idx, wl2[idx, 'analysis'].strip()) for idx in
                idxsB}
        for idx in idxsA:
            bed_words += 1
            srcid = wl1[idx, 'stedt_srcid'].split('.')[0]
            if srcid in tmp:
                if tmp[srcid][1]:
                    stedt = tmp[srcid][1].split(',')
                    for i, m in enumerate(stedt):
                        if not m.isdigit():
                            stedt[i] = str(new_id)
                            new_id += 1
                        else:
                            etym_count += 1
                        pcog_count += 1
                    counts += 1
                    analyses[idx] = ' '.join(stedt)
                else:
                    analyses[idx] = ''
                new_rns[idx] = tmp[srcid][0]
            else:
                print('not found', srcid, wl1[idx, 'doculect'], wl1[idx, 'concept'])
                nfound += 1
                analyses[idx] = ''
                new_rns[idx] = ''
    else:
        for idx in idxsA:
            analyses[idx] = ''
            new_rns[idx] = ''

# output results
print("Annotated (STEDT):        ", counts)
print("Words (BED):              ", bed_words)
print("Missing links to STEDT:   ", nfound)
print("Unannotated (STEDT):      ", '{0:.2f}'.format(counts / bed_words))
print("Partial Cognates (total)  ", pcog_count)
print("Analyzed Cognates (STEDT):", 
        '{0} ({1:.2f}%)'.format(etym_count, etym_count/pcog_count))

# compare similarities of cognates now
wl1.add_entries('stedt_analysis', analyses, lambda x: x)
wl1.add_entries('stedt_id', new_rns, lambda x: str(x))
wl1.output('tsv', filename='burmish-compare', ignore='all', prettify=False)
wl1.output('tsv', filename='t_bed-stedt', ignore='all', prettify=False,
        subset=True, rows=dict(stedt_analysis = '!= ""'))

# new word list, only matches
wl = Wordlist('t_bed-stedt.tsv')
for idx, stedt in iter_rows(wl, 'stedt_analysis'):
    wl[idx, 'stedt_analysis'] = [int(x) for x in stedt.split(' ')]
blacklist = []
for idx, stedt, cogids, concept, language, word in iter_rows(wl,
        'stedt_analysis', 'cogids', 'concept', 'doculect', 'ipa'):
    if len(stedt) != len(cogids):
        blacklist += [idx]
    else:
        for i, (c1, c2) in enumerate(zip(stedt, cogids)):
            if c1 > 9999:
                wl[idx, 'cogids'][i] = c1+30000

wl.output('tsv', filename='t_bed-stedt-2', subset=True, rows=dict(
    ID = 'not in '+str(blacklist)))

wl = Wordlist('t_bed-stedt-2.tsv')
for idx, stedt in iter_rows(wl, 'stedt_analysis'):
    wl[idx, 'stedt_analysis'] = [int(x) for x in stedt.split(' ')]
print("Words left for comparison: ", len(wl))
print('---')
p, r, f = partial_bcubes(wl, 'cogids', 'stedt_analysis', pprint=False)
print('Precision: {0:.2f}\nRecall:    {1:.2f}\nF-Score:   {2:.2f}'.format(p, r, f))
