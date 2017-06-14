"""
Partial Colexification Analysis of Burmish Languages


"""

from lingpy import *
from lingpy.sequence.sound_classes import _split_syllables, syllabify, tokens2morphemes
import networkx as nx
from collections import defaultdict
from tabulate import tabulate
import itertools
import pickle, html, codecs

def show_stuff(data, language):
    """helper function for interactive sessions"""
    dt = data[language]
    for k in sorted(dt, key=lambda x: len(dt[x]), reverse=False):
        out = []
        if len(dt[k]) > 1:
            for a, b, c, d in dt[k]:
                out += [[k, a, b, c, d]]
            print(tabulate(out))

def save_network(filename, graph, dump=False):
    """ save network in html form to not loose characters """
    if dump:
        with open(filename[:-3]+'bin', 'wb') as f:
            pickle.dump(graph, f)
    with codecs.open(filename, 'w', 'utf-8') as f:
        for line in nx.generate_gml(graph):
            f.write(html.unescape(line)+'\n')

# load the data
wl = Wordlist('d_bed.tsv')
# bipartite graph
G = nx.Graph()

# dictionaries to store the data
D = {l: defaultdict(list) for l in wl.taxa}
S = {l: [] for l in wl.taxa}
cid = 1

# start iteration, this time over cognate ids and morphemes
for idx, tks, lng, cnc, mps, cids in iter_rows(wl, 'tokens', 'doculect', 'concept',
        'morphemes', 'cogids'):
    segments = [' '.join(x) for x in tokens2morphemes(tks)]
    morphemes = mps or []
    if len(morphemes) != len(segments):
        morphemes = ['{0}-{1}'.format(cid, i) for i in range(len(segments))]
        cid += 1
    for i, m in enumerate(morphemes):
        if not m.strip() and not m.replace('?', ''):
            morphemes[i] = '{0}-{1}'.format(cid, i)

    cogids = [int(x) for x in cids]    
    for i, s in enumerate(segments):
        new_string = [x for x in segments]
        new_string[i] = '< '+new_string[i]+' >'
        new_string = ' + '.join(new_string)
        D[lng][s] += [(cnc, morphemes[i], cogids[i], new_string)]

# make bipartite graph now
for l in wl.taxa:
    dt = D[l]
    for k, v in dt.items():
        if len(v) > 1:
            S[l] += [sorted(set([x[0] for x in v]))]
            node = '{0}-{1}'.format(l, k)
            G.add_node(node, type=1)
            for line in v:
                try:
                    G.node[line[0]]
                except:
                    G.add_node(line[0], type=2)
                G.add_edge(node, line[0])

# try to find twins in the data
twins = defaultdict(list)
for node, data in G.nodes(data=True):
    if data['type'] == 1:
        pals = '//'.join(sorted(G.edge[node]))
        twins[pals] += [node]
for twin, nodes in sorted(twins.items(), key=lambda x: len(x[0].split('//'))):
    if len(nodes) > 1:
        print(', '.join(twin.split('//')))
        print(len(twin.split('//')), ', '.join(nodes))
nodes1 = [n for n, d in G.nodes(data=True) if d['type'] == 2]

# save bipartite network
save_network('o_bipartite.gml', G)


