#This is a convex hull algorithm that absorbs minimal separations, inputs the directed graph and sets of concerns, and obtains the convex hull.
import networkx as nx
from collections import deque

class Convex_hull_DAG:
    def __init__(self, graph):
        self.graph = graph

    def Ancestors(self,g, source): 
        G_pred = g.pred
        seen = set()
        nextlevel = source
        while nextlevel:
            thislevel = nextlevel
            nextlevel = set()
            for v in thislevel:
                if v not in seen:
                    seen.add(v)
                    nextlevel.update(G_pred[v])
        return seen
    
    def Rech(self,g, source, Re):
        """
        Efficient Bayes-ball reachability computation.
        Find all nodes reachable from `source` under conditioning on `Re`.
        """
        An_Re = self.Ancestors(g, Re)
        successors = g.successors
        predecessors = g.predecessors

        def _pass(e_in, v, e_out, n):
            if v not in An_Re:
                return not (e_in == 0 and e_out == 1)
            elif v in Re:
                return e_in == 0 and e_out == 1
            else:
                return True

        Q = deque()
        P = set()

        for ch in successors(source):
            Q.append((0, ch))  # 0 = from parent (i.e., down)
            P.add((0, ch))
        for pa in predecessors(source):
            Q.append((1, pa))  # 1 = from child (i.e., up)
            P.add((1, pa))

        while Q:
            direction_in, node = Q.popleft()

            for neighbor in successors(node):
                key = (0, neighbor)
                if key not in P and _pass(direction_in, node, 0, neighbor):
                    Q.append(key)
                    P.add(key)
            for neighbor in predecessors(node):
                key = (1, neighbor)
                if key not in P and _pass(direction_in, node, 1, neighbor):
                    Q.append(key)
                    P.add(key)
        return {v for (_, v) in P}

    def FCMS(self, g, u, v):

        ancestor_nodes = self.Ancestors(g, {u, v})
        An = g.subgraph(ancestor_nodes)

        preds_u = set(An.predecessors(u))
        succs_u = set(An.successors(u))

        mb_u = set()
        for child in succs_u:
            mb_u.update(An.predecessors(child))
        mb_u.update(preds_u)
        mb_u.update(succs_u)
        mb_u.discard(u)

        reach_v = self.Rech(g, v, mb_u)

        return mb_u & reach_v

    def CMDSA(self, r):
        g = self.graph
        h = r.copy()
        ang_nodes = self.Ancestors(g, r)
        ang = g.subgraph(ang_nodes).copy()
        mark = set()
        changed = True

        while changed:
            changed = False
            m = ang_nodes - h

            mb = nx.node_boundary(ang, m, h)
            h_ch_in_m = nx.node_boundary(ang, h, m)

            Q = set()
            for v in mb:
                Q.update(set(ang.predecessors(v)) & h)
            for v in h_ch_in_m:
                Q.update(set(ang.predecessors(v)) & h)
            Q.update(mb)

            if len(Q) > 1:
                Q_list = list(Q)
                for i in range(len(Q_list)):
                    for j in range(i + 1, len(Q_list)):
                        a, b = Q_list[i], Q_list[j]
                        edge_key = frozenset((a, b))
                        if edge_key in mark:
                            continue
                        mark.add(edge_key)
                        if not ang.has_edge(a, b) and not ang.has_edge(b, a):
                            S_a = self.FCMS(ang, a, b)
                            if not S_a:
                                continue
                            S_b = self.FCMS(ang, b, a)
                            S = S_a | S_b
                            if S - h:
                                h.update(S)
                                changed = True
                                break
                    if changed:
                        break
        return h
    
#from Convex_hull_DAG import *
#hull = Convex_hull_DAG(G)
#hull.CMDSA(R)