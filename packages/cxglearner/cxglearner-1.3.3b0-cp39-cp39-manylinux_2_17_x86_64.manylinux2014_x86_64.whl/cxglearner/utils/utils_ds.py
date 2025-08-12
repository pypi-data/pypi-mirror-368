import networkx as nx
from typing import Union, Optional, List, Any, Tuple, Dict
from logging import Logger
from functools import reduce

import difflib
import cytoolz as cy


def lup_slots(candid: Any, mapper: Dict) -> List:
    return [mapper.get(cand[0], [cand[0]])[-1]
            if isinstance(cand, tuple) else mapper.get(cand, [cand])[-1] for cand in candid]


class CandidateTree(object):
    def __init__(self, data: Any):
        self.data = data if not isinstance(data, list) else tuple(data)
        self.childs = []

    def nodes_list(self) -> list:
        node_ls = []

        def _obtain_all_nodes(cur_node: CandidateTree):
            node_ls.append(cur_node.data)
            for child in cur_node.childs:
                _obtain_all_nodes(child)

        _obtain_all_nodes(self)
        return node_ls

    def no_childs(self):
        return len(self.childs) == 0

    def __str__(self):
        return '{}'.format(self.data)

    def __repr__(self):
        return self.__str__() + ': depth {}'.format(self.depth)

    def match_length(self, flattened: Any) -> int:
        from .utils_extractor import flatten_slots
        return max([match.size for match in difflib.SequenceMatcher(None, flatten_slots(self.data),
                                                                    flattened).get_matching_blocks()])

    @property
    def flatten_len(self) -> int:
        from .utils_extractor import flatten_slots
        return len(flatten_slots(self.data))

    def __len__(self):
        return self.flatten_len

    def to_graph(self, graph: nx.Graph) -> None:
        for child in self.childs:
            graph.add_edge(self.data, child.data, relation="father")
            graph.add_edge(child.data, self.data, relation="child")
            child.to_graph(graph)

    def dominates_to_graph(self, graph: nx.DiGraph, dominates: List[int]) -> None:
        from .utils_extractor import flatten_slots

        def add_dom_to_graph(parent_data: tuple, child_data: tuple):
            graph.add_edge(parent_data, child_data, relation="dom")
            graph.add_edge(child_data, parent_data, relation="domby")

        node_data = flatten_slots(self.data)
        for child in self.childs:
            child_data = flatten_slots(child.data)
            match = difflib.SequenceMatcher(
                None, node_data, child_data).get_matching_blocks()[0]
            # Avoid the occurrence of unexpected situations.
            if match.size == 0:
                return
            if len(child) == len(node_data):
                return
            # Add relations
            if match.a > 0 and match.a + match.size < len(node_data):
                if child_data[match.b] in dominates[match.a - 1] and node_data[match.a + match.size
                                                                               ] in dominates[match.a + match.size - 1]:
                    add_dom_to_graph(self.data, child.data)
            elif match.a == 0:
                if node_data[match.a + match.size] in dominates[match.a + match.size - 1]:
                    add_dom_to_graph(self.data, child.data)
            elif match.a + match.size == len(node_data):
                if child_data[match.b] in dominates[match.a - 1]:
                    add_dom_to_graph(self.data, child.data)
            child.dominates_to_graph(
                graph, dominates[match.a: match.a + match.size])

    def insert(self, data: Any, flattened: Optional[Any] = None, **kwargs) -> Union[bool]:
        from .utils_extractor import flatten_slots
        if flattened is None:
            flattened = flatten_slots(data)
        if len(flattened) >= len(self.data):
            return False
        match_length = self.match_length(flattened)
        if match_length == len(flattened):
            if self.no_childs():
                self.childs.append(CandidateTree(data))
                return True
            else:
                include = []
                for child in self.childs:
                    child_length = len(child)
                    if child.insert(data, flattened):
                        return True
                    if child.match_length(flattened) == child_length:
                        include.append(child)
                if len(include) == 0:
                    self.childs.append(CandidateTree(data))
                    return True
                else:
                    ct = CandidateTree(data)
                    for mover in include:
                        self.childs.remove(mover)
                        ct.childs.append(mover)
                    self.childs.append(ct)
                    return True
        else:
            return False

    @property
    def depth(self) -> int:
        if self.no_childs():
            return 1
        return max([child.depth for child in self.childs]) + 1


CTree = CandidateTree


class LTreeStatus:
    HIGH: int = 0
    LOW: int = 1
    NEUTRAL: int = 2
    ERROR: int = 3


class LevelTree(CTree):
    def compare_candidates(self, data: Any, t2b_mapper: dict) -> int:
        slot_relations = set()
        for index in range(len(data)):
            self_slot, insert_slot = self.data[index], data[index]
            if self_slot == insert_slot:
                continue
            if insert_slot in t2b_mapper and self_slot in set(dict(t2b_mapper[insert_slot]).keys()):
                slot_relations.add(LTreeStatus.HIGH)
            elif self_slot in t2b_mapper and insert_slot in set(dict(t2b_mapper[self_slot]).keys()):
                slot_relations.add(LTreeStatus.LOW)
            else:
                slot_relations.add(LTreeStatus.NEUTRAL)
        if len(slot_relations) == 1:
            return list(slot_relations)[0]
        else:
            return LTreeStatus.NEUTRAL

    def insert(self, data: Any, flattened: Optional[Any] = None, **kwargs) -> Union[bool]:
        t2b_mapper = kwargs["t2b"]
        if self.no_childs():
            self.childs.append(LevelTree(data))
        else:
            for chi in range(len(self.childs)):
                child = self.childs[chi]
                if len(child.data) != len(data):
                    return False
                status = child.compare_candidates(data, t2b_mapper)
                if status == LTreeStatus.LOW:
                    return child.insert(data, **kwargs)
                elif status == LTreeStatus.NEUTRAL:
                    self.childs.append(LevelTree(data))
                    return True
                elif status == LTreeStatus.HIGH:
                    sub_tree = LevelTree(data)
                    sub_tree.childs.append(child)
                    self.childs[chi] = sub_tree
                    return True
                else:
                    # Although this doesn't work, it serves as a placeholder for future features.
                    return False


LTree = LevelTree


class PrunerGraph(nx.DiGraph):
    def __init__(self, incoming_graph_data: Optional[dict] = None, logger: Optional[Logger] = None, **kwargs):
        super(PrunerGraph, self).__init__(incoming_graph_data, **kwargs)
        self.logger = logger

    def add_edge(self, u_of_edge, v_of_edge, **kwargs):
        """
        Overload the add_edge method
        """
        u, v = u_of_edge, v_of_edge
        # add nodes
        if u not in self._succ:
            if u is None:
                if self.logger is not None:
                    self.logger.error("None cannot be a node")
                raise ValueError("None cannot be a node")
            self._succ[u] = self.adjlist_inner_dict_factory()
            self._pred[u] = self.adjlist_inner_dict_factory()
            self._node[u] = self.node_attr_dict_factory()
        if v not in self._succ:
            if v is None:
                if self.logger is not None:
                    self.logger.error("None cannot be a node")
                raise ValueError("None cannot be a node")
            self._succ[v] = self.adjlist_inner_dict_factory()
            self._pred[v] = self.adjlist_inner_dict_factory()
            self._node[v] = self.node_attr_dict_factory()
        # add the edge
        datadict = self._adj[u].get(v, self.edge_attr_dict_factory())
        # Re-write update method
        for attr in kwargs:
            if attr not in ['index', 'begin', 'end']:
                del kwargs[attr]
        index = kwargs.pop("index", None)
        if index is not None:
            if 'index' in datadict.keys():
                datadict['index'].update({index: "inner"})
            else:
                datadict['index'] = {index: "inner"}
        begin = kwargs.pop("begin", False)
        end = kwargs.pop("end", False)
        if begin:
            datadict['index'][index] = "begin"
        if end:
            datadict['index'][index] = "end"
        self._succ[u][v] = datadict
        self._pred[v][u] = datadict

    def add_candidates(self, candidates: Union[list, tuple, List[list], List[tuple]],
                       candidate_indexes: Union[int, List[int]], **kwargs) -> None:
        from .utils_extractor import flatten_slots
        mapper = kwargs.pop("mapper", None)

        if len(candidates) > 0 and (isinstance(candidates[0], int) or isinstance(candidates, tuple)):
            candidates = [candidates]
        if isinstance(candidate_indexes, int):
            candidate_indexes = [candidate_indexes]
        for candidate_index, candidate in zip(candidate_indexes, candidates):
            try:
                if mapper is None:
                    candidate = flatten_slots(candidate)
                else:
                    candidate = lup_slots(candidate, mapper)
                for sid in range(1, len(candidate)):
                    if sid == 1:
                        self.add_edge(
                            candidate[sid - 1], candidate[sid], index=candidate_index, begin=True)
                    elif sid == len(candidate) - 1:
                        self.add_edge(
                            candidate[sid - 1], candidate[sid], index=candidate_index, end=True)
                    else:
                        self.add_edge(
                            candidate[sid - 1], candidate[sid], index=candidate_index)
            except Exception as e:
                if self.logger is not None:
                    self.logger.error(e)
                else:
                    print(e)
                continue

    def all_sub_candidates(self, candidate: Union[list, tuple], candidate_mapper: dict, reference: set
                           ) -> Tuple[CTree, List[tuple]]:
        """
        Acquire all sub candidates in the graph G from source to target.
        """
        from .utils_extractor import flatten_slots
        cluster = CTree(candidate)
        candidate = flatten_slots(candidate)
        st_eds = {'begin': set(), 'end': set()}
        for cid in range(1, len(candidate)):
            edge = self[candidate[cid - 1]][candidate[cid]]['index']
            for e in edge:
                if edge[e] == 'begin':
                    st_eds['begin'].add(e)
                if edge[e] == 'end':
                    st_eds['end'].add(e)
        # Find all possible sub-candidates
        sub_candidates = st_eds['begin'] & st_eds['end']
        # Insert and filter impossible candidates
        dup_index = []
        for cindex in sub_candidates:
            selected_candidate = candidate_mapper[cindex]
            if selected_candidate not in reference:
                continue
            sub_candidate = flatten_slots(selected_candidate)
            if cluster.insert(selected_candidate, sub_candidate):
                dup_index.append(selected_candidate)
        return cluster, dup_index

    def all_match_candidates(self, candidate: Union[list, tuple], candidate_mapper: dict, reference: set,
                             mapper_b2t: dict, mapper_t2b: dict) -> List[LTree]:
        """
        Acquire all candidates in the graph G from source to target.
        """
        cluster, possibles = LTree(None), set()

        def _obtain_candidate_slots(slot: int) -> set:
            slot_candidate = set()
            slot_candidate.add(slot)
            if slot in mapper_b2t:
                slot_candidate = slot_candidate.union(mapper_b2t[slot])
            # if slot in mapper_t2b: slot_candidate = slot_candidate.union(mapper_t2b[slot])
            # So Slow, deserted
            # Simultaneously removing the duplicate index judgment, the same result can be achieved.
            return slot_candidate

        def _find_tuple_candidates(node: int, slot: set[tuple], label="inner") -> set:
            available_candidate_ids = set()
            plain_slots = [sl if isinstance(sl, tuple) and not isinstance(
                sl[0], tuple) else sl[0] for sl in slot]
            set_available_nodes = set(
                cy.filter(lambda x: x[0] in self[node], plain_slots))
            for ava_node in set_available_nodes:
                available_set = set()
                ava_node = [node] + list(ava_node)
                for index in range(1, len(ava_node)):
                    cur_node, last_node = ava_node[index], ava_node[index - 1]
                    if cur_node not in self[last_node]:
                        break
                    edges = self[last_node][cur_node]["index"]
                    if index == 1:
                        if label == 'begin':
                            available_set = available_set.union(
                                set(cy.valfilter(lambda x: x == "begin", edges)))
                        else:
                            available_set = available_set.union(
                                set(cy.valfilter(lambda x: x == "inner", edges)))
                        continue
                    elif index == len(ava_node) - 1:
                        if label == 'end':
                            available_set = available_set.intersection(
                                set(cy.valfilter(lambda x: x == "end", edges)))
                            continue
                    available_set = available_set.intersection(
                        set(cy.valfilter(lambda x: x == "inner", edges)))
                available_candidate_ids = available_candidate_ids.union(
                    available_set)
            return available_candidate_ids

        # Process slots
        for cid in range(1, len(candidate)):
            cur_slot = candidate[cid]
            last_slot = candidate[cid - 1]
            cur_candidates = _obtain_candidate_slots(cur_slot)
            last_candidates = _obtain_candidate_slots(last_slot)
            slot_possibles = set()
            for node in last_candidates:
                if isinstance(node, tuple):
                    node = node[0]
                if isinstance(node, tuple):
                    start_sets = _find_tuple_candidates(
                        node[0], set(tuple([node[1:]])), label="begin")
                    pnode = node[-1]
                else:
                    start_sets = None
                    pnode = node
                cur_tuple_candidates = set(
                    cy.filter(lambda x: isinstance(x, tuple) and isinstance(x[0], tuple), cur_candidates))
                # Process single case
                cur_single_candidates = cur_candidates - cur_tuple_candidates
                cur_single_candidates = set([cand if isinstance(cand, int) else cand[0]
                                             for cand in cur_single_candidates])
                if pnode not in self.nodes:
                    continue
                available_single_nodes = cy.keyfilter(
                    lambda x: x in cur_single_candidates, self[pnode])
                available_single_edges = [_["index"]
                                          for _ in available_single_nodes.values()]
                if len(available_single_edges) == 0:
                    available_single_edges = set()
                else:
                    if len(available_single_edges) > 1:
                        available_single_edges = reduce(
                            lambda x, y: {**x, **y}, available_single_edges)
                    else:
                        available_single_edges = available_single_edges[0]
                    if cid == 1 and not isinstance(node, tuple):
                        available_single_edges = set(
                            list(cy.valfilter(lambda x: x == "begin", available_single_edges)))
                    elif cid == len(candidate) - 1:
                        available_single_edges = set(
                            list(cy.valfilter(lambda x: x == "end", available_single_edges)))
                    else:
                        available_single_edges = set(
                            list(cy.valfilter(lambda x: x == "inner", available_single_edges)))
                # Process tuple case
                available_tuple_edges = _find_tuple_candidates(
                    pnode, cur_tuple_candidates, label="begin" if cid == 1 and isinstance(
                        node, int) else "end"
                    if cid == len(candidate) - 1 else "inner"
                )
                available_edges = available_single_edges.union(
                    available_tuple_edges)
                if start_sets is not None:
                    available_edges = available_edges.intersection(start_sets)
                slot_possibles = slot_possibles.union(available_edges)
            if cid == 1:
                possibles = possibles.union(slot_possibles)
            else:
                possibles = possibles.intersection(slot_possibles)
        possibles = list(possibles)
        if len(possibles) <= 1:
            return list()
        # Insert and filter impossible candidates
        common_kwargs = {"t2b": mapper_t2b, "b2t": mapper_b2t}
        for candid in possibles:
            selected_candidate = candidate_mapper[candid]
            if selected_candidate not in reference:
                continue
            cluster.insert(selected_candidate, **common_kwargs)
        # Split
        clusters = [child for child in cluster.childs if len(child.childs) > 0]
        return clusters

    def all_related_dists(self, candidate: tuple, index: int, candidate_mapper: Dict, min_length: int) -> List:
        stored = []
        up_candidate = lup_slots(candidate, candidate_mapper)
        for ind in range(1, len(up_candidate)):
            temp = list(self[up_candidate[ind - 1]]
                        [up_candidate[ind]]["index"].keys())
            stored.extend(temp)
        related = list(cy.itemfilter(
            lambda x: x[0] > index and x[1] >= min_length - 2, cy.frequencies(stored)))
        related.sort()
        return related

    def all_simple_paths(self, source, target, cutoff=None) -> list:
        """
        <Overload>
        Generate all paths in the graph G from source to target.
        A simple path is a path with no repeated nodes.
        """
        def _all_simple_paths_graph(G, source, targets, cutoff):
            visited = [source]
            stack = [iter(G[source])]
            initial_set = []
            for node in G[source]:
                initial_set.extend(list(G[source][node]["index"].keys()))
            initial_set = set(initial_set)
            saved_set = [initial_set]
            while stack:
                children = stack[-1]
                child = next(children, None)
                if child is None:
                    stack.pop()
                    visited.pop()
                    saved_set.pop()
                elif len(visited) < cutoff:
                    if child in visited:
                        continue
                    if child in targets:
                        yield list(visited) + [child]
                    current_set = saved_set[-1] & set(
                        G[visited[-1]][child]["index"].keys())
                    if not current_set:
                        continue
                    visited.append(child)
                    saved_set.append(current_set)
                    if targets - set(visited):  # expand stack until find all targets
                        stack.append(iter(G[child]))
                    else:
                        visited.pop()
                        saved_set.pop()  # maybe other ways to child
                else:  # len(visited) == cutoff:
                    for target in (targets & (set(children) | {child})) - set(visited):
                        yield list(visited) + [target]
                    stack.pop()
                    visited.pop()
                    saved_set.pop()

        if source not in self:
            raise nx.NodeNotFound(f"source node {source} not in graph")
        if target in self:
            targets = {target}
        else:
            try:
                targets = set(target)
            except TypeError as err:
                raise nx.NodeNotFound(
                    f"target node {target} not in graph") from err
        if source in targets:
            return list()
        if cutoff is None:
            cutoff = len(self) - 1
        if cutoff < 1:
            return list()
        return list(_all_simple_paths_graph(self, source, targets, cutoff))


PGraph = PrunerGraph
