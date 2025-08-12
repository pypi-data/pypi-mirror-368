from logilab.common.graph import get_cycles

try:
    (rtype,) = __args__
except ValueError:
    print("USAGE: cubicweb-ctl shell <instance> detect_cycle.py -- <relation type>")
    print()

graph = {}
for fromeid, toeid in rql(f"Any X,Y WHERE X {rtype} Y"):
    graph.setdefault(fromeid, []).append(toeid)

for cycle in get_cycles(graph):
    print("cycle", "->".join(str(n) for n in cycle))
