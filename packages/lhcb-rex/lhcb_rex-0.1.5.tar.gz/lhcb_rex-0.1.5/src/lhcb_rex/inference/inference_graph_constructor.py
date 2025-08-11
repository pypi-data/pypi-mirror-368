import networkx as nx
import re
from collections import deque
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
import random


class GraphConstructor:
    def parse_decay_string_to_graph(self, topology):
        """
        Parses decay string like 'B+ -> { D0 -> K+ e- } pi+' into a graph
        Returns: (DiGraph, particle_labels)
        """

        # Replace {} with () to simplify
        topology = topology.replace("{", "(").replace("}", ")")

        # Tokenize: preserve nested structure and particles with * or ± signs
        token_pattern = r"\(|\)|->|[^\s()]+"
        raw_tokens = re.findall(token_pattern, topology)

        tokens = deque(raw_tokens)

        G = nx.DiGraph()
        particle_labels = {}
        particle_id_counter = 0

        def parse(tokens, parent=None):
            nonlocal particle_id_counter

            if not tokens:
                return

            head = tokens.popleft()
            if head == "(":
                # Nested decay
                head_particle = tokens.popleft()
                arrow = tokens.popleft()
                assert arrow == "->", f"Expected '->' in nested decay, got {arrow}"

                current_id = particle_id_counter
                particle_labels[current_id] = head_particle
                particle_id_counter += 1

                if parent is not None:
                    G.add_edge(parent, current_id)

                # Parse children
                while tokens[0] != ")":
                    if tokens[0] == "(":
                        parse(tokens, current_id)
                    else:
                        child_particle = tokens.popleft()
                        child_id = particle_id_counter
                        particle_labels[child_id] = child_particle
                        particle_id_counter += 1
                        G.add_edge(current_id, child_id)

                tokens.popleft()  # consume ')'

            else:
                # Top-level decay
                assert tokens.popleft() == "->", "Expected '->' in top-level decay"
                current_id = particle_id_counter
                particle_labels[current_id] = head
                particle_id_counter += 1
                parent = current_id

                while tokens:
                    tok = tokens.popleft()
                    if tok == "(":
                        tokens.appendleft(tok)
                        parse(tokens, parent)
                    else:
                        child_id = particle_id_counter
                        particle_labels[child_id] = tok
                        particle_id_counter += 1
                        G.add_edge(parent, child_id)

        parse(tokens)
        return G, particle_labels

    def get_particle_types(self, G):
        particle_types = {}
        for node in G.nodes:
            if G.in_degree(node) == 0:
                particle_types[node] = "mother"
            elif G.out_degree(node) == 0:
                particle_types[node] = "track"
            else:
                particle_types[node] = "intermediate"
        return particle_types

    def reindex_particle_types_by_class(self, particle_types):
        class_counters = {"mother": 0, "intermediate": 0, "track": 0}
        reindexed = {}

        for node_id in sorted(particle_types):  # ensure order by node ID
            p_type = particle_types[node_id]
            local_index = class_counters[p_type]
            reindexed[node_id] = (local_index, p_type)
            class_counters[p_type] += 1

        return reindexed

    def find_daughters(self, structure, idx, level=0, edge_index=None):
        if edge_index is None:
            edge_index = defaultdict(list)

        # Collect direct daughters of `idx`
        daughters = [(child, idx) for parent, child in structure if parent == idx]

        # Store unique daughters at this level
        for child_pair in daughters:
            if child_pair not in edge_index[level + 1]:
                edge_index[level + 1].append(child_pair)

        # Recurse for each daughter
        for child, _ in daughters:
            self.find_daughters(structure, child, level + 1, edge_index)

        return edge_index

    def get_edge_ID(self, edge, particle_labels, invert=False, direction="to"):
        if invert:
            return particle_labels[edge[1]], direction, particle_labels[edge[0]]
        else:
            return particle_labels[edge[0]], direction, particle_labels[edge[1]]

    def updated_indexes(self, edge, edge_ID, particle_types_indexed, Nfinalstate):
        return [particle_types_indexed[edge[0]][0], particle_types_indexed[edge[1]][0]]

    def generate_edge_index_tensor(
        self, edge_index, particle_types, particle_types_indexed, Nfinalstate
    ):
        edge_index_tensors_up = {}
        edge_index_tensors_up["track", "up", "intermediate"] = []
        edge_index_tensors_up["track", "up", "mother"] = []
        edge_index_tensors_up["intermediate", "up", "mother"] = []
        edge_index_tensors_up["intermediate", "up", "intermediate"] = []
        edge_index_tensors_down = {}
        edge_index_tensors_down["intermediate", "down", "track"] = []
        edge_index_tensors_down["mother", "down", "track"] = []
        edge_index_tensors_down["mother", "down", "intermediate"] = []
        edge_index_tensors_down["intermediate", "down", "intermediate"] = []
        for level in range(max(list(edge_index.keys())), 0, -1):
            edge_index_tensor_i = {}  # [[x, y], [x, z]]
            edge_index_tensor_i["track", "up", "intermediate"] = []
            edge_index_tensor_i["track", "up", "mother"] = []
            edge_index_tensor_i["intermediate", "up", "mother"] = []
            edge_index_tensor_i["intermediate", "up", "intermediate"] = []

            for edge in edge_index[level]:
                edge_id = self.get_edge_ID(edge, particle_types, direction="up")
                new_edge = self.updated_indexes(
                    edge, edge_id, particle_types_indexed, Nfinalstate=Nfinalstate
                )
                edge_index_tensor_i[edge_id].append(new_edge)
                # need to update indexes based on node type

            for key in edge_index_tensor_i:
                edge_index_tensors_up[key].append(edge_index_tensor_i[key])
        for level in range(1, max(list(edge_index.keys())) + 1):
            edge_index_tensor_i = {}  # [[x, y], [x, z]]
            edge_index_tensor_i["intermediate", "down", "track"] = []
            edge_index_tensor_i["mother", "down", "track"] = []
            edge_index_tensor_i["mother", "down", "intermediate"] = []
            edge_index_tensor_i["intermediate", "down", "intermediate"] = []

            for edge in edge_index[level]:
                edge_id = self.get_edge_ID(
                    edge, particle_types, invert=True, direction="down"
                )
                edge_invert = [edge[1], edge[0]]
                new_edge = self.updated_indexes(
                    edge_invert,
                    edge_id,
                    particle_types_indexed,
                    Nfinalstate=Nfinalstate,
                )
                edge_index_tensor_i[edge_id].append(new_edge)

            for key in edge_index_tensor_i:
                edge_index_tensors_down[key].append(edge_index_tensor_i[key])

        return edge_index_tensors_up, edge_index_tensors_down

    def plot_graph(
        self, edge_list, particle_labels=None, naming_scheme_dict=None, title=None
    ):
        G = nx.DiGraph()
        G.add_edges_from(edge_list)

        pos = {}
        pos[0] = (0.5, 1.05)  # Start with root node at the top center

        def position_nodes(
            graph, parent, y_pos, level_gap=0.15, h_spread=0.1, randomness=0.02
        ):
            children = list(graph.neighbors(parent))
            num_children = len(children)

            if not children:
                return

            parent_x = pos[parent][0]
            if num_children == 1:
                x_positions = [parent_x]
            else:
                start = parent_x - h_spread / 2
                end = parent_x + h_spread / 2
                x_positions = np.linspace(start, end, num_children)

            for i, child in enumerate(children):
                jitter_x = random.uniform(-randomness, randomness)
                jitter_y = random.uniform(-randomness, randomness)
                pos[child] = (x_positions[i] + jitter_x, y_pos - level_gap + jitter_y)
                position_nodes(
                    graph,
                    child,
                    y_pos - level_gap,
                    level_gap,
                    h_spread * 0.6,
                    randomness,
                )

        position_nodes(G, 0, 1.0)

        node_colors = []
        for node in G.nodes:
            if node == 0:
                node_colors.append("red")
            elif G.out_degree(node) > 0:
                node_colors.append("purple")
            else:
                node_colors.append("skyblue")

        # Use particle labels for node annotations if provided
        node_labels = {
            n: (
                f"{n} : {particle_labels[n]}"
                if particle_labels and n in particle_labels
                else str(n)
            )
            for n in G.nodes
        }

        plt.figure(figsize=(4, 4))
        nx.draw(
            G,
            pos,
            labels=node_labels,
            with_labels=True,
            node_size=200,
            node_color=node_colors,
            font_size=5,
            font_weight="bold",
            arrows=True,
        )
        if title:
            plt.title(title)

        plt.savefig("graph_structure.pdf", bbox_inches="tight")
        plt.close()

    def plot(self):
        edge_list = list(self.G.edges)
        self.plot_graph(edge_list, particle_labels=self.particle_labels)

    def count_total_descendants(self, G, particle_types):
        descendant_counts = {}

        def count_descendants(node):
            count = 0
            for child in G.successors(node):
                if particle_types[child] == "track":
                    count += 1
                elif particle_types[child] == "intermediate":
                    count += count_descendants(child)
            return count

        for node, p_type in particle_types.items():
            if p_type in ("mother", "intermediate"):
                descendant_counts[self.particle_labels[node]] = count_descendants(node)

        return descendant_counts


    def count_Ndaughters(self, G, particle_types):
        descendant_counts = {}

        def count_descendants(node):
            count = 0
            for child in G.successors(node):
                count += 1
            return count

        for node, p_type in particle_types.items():
            if p_type in ("mother", "intermediate"):
                descendant_counts[self.particle_labels[node]] = count_descendants(node)

        return descendant_counts

    def get_intermediate_particles_recipes(self, G, particle_types):
        recipes = {}

        def append_descendants(node):
            count = []
            for child in G.successors(node):
                if particle_types[child] == "track":
                    count.append(self.particle_labels[child])
                elif particle_types[child] == "intermediate":
                    count.append(self.particle_labels[child])
            return count

        for node, p_type in particle_types.items():
            if p_type in ("intermediate"):
                recipes[self.particle_labels[node]] = append_descendants(node)

        return recipes

    def __init__(self, reconstruction_topology):
        self.G, self.particle_labels = self.parse_decay_string_to_graph(
            reconstruction_topology
        )
        self.mother_name = self.particle_labels[0]

        particle_types = self.get_particle_types(self.G)

        self.daughter_counts = self.count_total_descendants(self.G, particle_types)
        self.Ndaughter_counts = self.count_Ndaughters(self.G, particle_types)


        self.intermediate_particles = self.get_intermediate_particles_recipes(
            self.G, particle_types
        )

        particle_types_indexed = self.reindex_particle_types_by_class(particle_types)

        self.N_nodes = {
            "mother": 1,
            "intermediate": list(particle_types.values()).count("intermediate"),
            "track": list(particle_types.values()).count("track"),
        }

        edge_index = self.find_daughters(structure=self.G.edges, idx=0)
        self.edge_index_tensors_up, self.edge_index_tensors_down = (
            self.generate_edge_index_tensor(
                edge_index,
                particle_types,
                particle_types_indexed,
                Nfinalstate=self.N_nodes["track"],
            )
        )
