import itertools
import networkx as nx

def _tokenize(f):
    token = []
    for line in f:
        if line == '\n':
            yield token
            token = []
        else:
            token.append(line)

def _filter_terms(tokens):
    for token in tokens:
        if token[0] == '[Term]\n':
            yield token[1:]

def _parse_terms(terms):
    for term in terms:
        obsolete = False
        node = {}
        parents = []
        for line in term:
            if line.startswith('id:'):
                id = line[4:-1]
            elif line.startswith('name:'):
                node['name'] = line[6:-1]
            elif line.startswith('namespace:'):
                node['namespace'] = line[11:-1]
            elif line.startswith('is_a:'):
                parents.append(line[6:16])
            elif line.startswith('relationship: part_of'):
                parents.append(line[22:32])
            elif line.startswith('is_obsolete'):
                obsolete = True
                break
        if not obsolete:
            edges = [(p, id) for p in parents] # will reverse edges later
            yield (id, node), edges
        else:
            continue

_filename = 'db/go-basic.obo'

def ontology(filename):
    O = nx.DiGraph()
    with open(filename) as f:
        tokens = _tokenize(f)
        terms = _filter_terms(tokens)
        entries = _parse_terms(terms)
        nodes, edges = zip(*entries)
        O.add_nodes_from(nodes)
        O.add_edges_from(itertools.chain.from_iterable(edges))
        O.graph['roots'] = {data['name'] : n for n, data in O.node.items()
                if data['name'] == data['namespace']}
    for root in O.graph['roots'].values():
        for n, depth in nx.shortest_path_length(O, root).items():
            node = O.node[n]
            node['depth'] = min(depth, node.get('depth', float('inf')))
    O.reverse(copy=False)
    return O
