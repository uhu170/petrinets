# controller.py
from view import View
from petrinet import Petrinet
from petri_io import Parser
from PySide6.QtWidgets import QFileDialog
import os


class PetriNetController:
    def __init__(self):
        self.net = Petrinet()
        self.view = View(self)
        self.last_selected_place = None
        self.file_name = None
        self.open_file_dialog()


    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            None,
            "Netz laden",
            "",
            "PNML-Dateien (*.pnml);;Alle Dateien (*)"
        )
        if path:
            self.file_name = os.path.basename(path)
            self.new_net(path)
            self.view.status.showMessage(f"Aktuelle Datei: {self.file_name}")

    def new_net(self, file_path):
        self.last_selected_place = None

        self.view.petri_canvas.reset_petrinet_graph()

        parser = Parser()
        m, t = parser.parse(file_path)

        trans = []
        mark = []
        for tr in t:
            _, _, _, _, t_pre, t_post = tr
            trans.append((t_pre, t_post))
        for ma in m:
            _, _, _, _, val = ma
            mark.append(val)

        self.net.update_net(mark, trans)
        for i, p in enumerate(m):
            original_id, name, x, y, val = p
            self.view.petri_canvas.add_place(x, y, val, model_id=i, name=name)

        for i, t in enumerate(t):
            original_id, name, x, y, pre, post = t
            self.view.petri_canvas.add_trans(x, y, model_id=i + self.net.places, name=name)
            for j in range(self.net.places):
                if pre[j] > 0:
                    self.view.petri_canvas.add_edge(j, i + self.net.places, '')
                if post[j] > 0:
                    self.view.petri_canvas.add_edge(i + self.net.places, j, '')

        # reachability_graph
        reach_canvas_label = str(self.net.mark)
        self.view.reach_canvas.initialize_graph('(' + reach_canvas_label[1:-1] + ')')
        self.view.fit_all()


    def fire_trans(self, t_id):
        prev_mark = '(' + str(self.net.mark)[1:-1] + ')'
        if self.net.fire_trans(t_id):
            new_mark = '(' + str(self.net.mark)[1:-1] + ')'
            self.view.reach_canvas.update_graph(new_mark=new_mark, prev_mark=prev_mark, trans_original_id=str(t_id))
            self.view.petri_canvas.update_labels(self.net.mark)
            self.place_clicked(None, None)

    def add_token(self):
        if self.last_selected_place is not None:
            if self.net.change_mark(1, self.last_selected_place):
                self.view.petri_canvas.update_labels(self.net.mark)
                reach_canvas_label = str(self.net.mark)
                self.view.reach_canvas.initialize_graph('(' + reach_canvas_label[1:-1] + ')')


    def subtract_token(self):
        if self.last_selected_place is not None:
            if self.net.change_mark(-1, self.last_selected_place):
                self.view.petri_canvas.update_labels(self.net.mark)
                reach_canvas_label = str(self.net.mark)
                self.view.reach_canvas.initialize_graph('(' + reach_canvas_label[1:-1] + ')')

    def place_clicked(self, model_id, node=None):
        # If the clicked node is already selected, deselect it
        if self.last_selected_place == model_id:
            if node is not None:
                node.set_selected(False)
            self.last_selected_place = None
            return

        # Deselect previous node if it exists
        if self.last_selected_place is not None:
            prev_node = self.view.petri_canvas.nodes.get(self.last_selected_place, None)
            if prev_node is not None:
                prev_node.set_selected(False)

        # Select the new node
        if node is not None:
            node.set_selected(True)

        # Update last selected
        self.last_selected_place = model_id

    def load_marking_from_reach_graph(self, marking_str: str):
        new_mark = tuple(int(x) for x in marking_str[1:-1].split(','))
        self.net.set_mark(new_mark)
        self.view.petri_canvas.update_labels(new_mark)
        self.view.reach_canvas.highlight_marking(marking_str)

    def analyse(self):
        if self.net.mark is None:
            return

        self.net.analysis()

        # Determine dynamic width for filename column
        filename_width = max(9, len(self.file_name) + 2)
        bounded_width = 10  # fixed width for bounded column

        bounded = 'yes' if self.net.bounded else 'no'
        if self.net.bounded:
            stats = f"{self.net.marks} / {self.net.edges}"
        else:
            stats = f"{self.net.m_null} / {self.net.m_last}"

        # Dynamically adjust stats column width based on length of stats or header
        stats_header = 'Nodes / Edges resp. m, m\''
        stats_width = max(len(stats_header), len(stats) + 2)

        # Header and separator
        header = f"{'filename':<{filename_width}} | {'bounded':<{bounded_width}} | {stats_header:<{stats_width}}"
        separator = f"{'-' * filename_width} | {'-' * bounded_width} | {'-' * stats_width}"
        self.view.text_area.append(header)
        self.view.text_area.append(separator)

        line = f"{self.file_name:<{filename_width}} | {bounded:<{bounded_width}} | {stats:<{stats_width}}"
        self.view.text_area.append(line + '\n')

        # Build reachability graph for net
        g = self.net.g
        for mark in g:
            self.view.reach_canvas.add_marking(str(mark))
            for new_mark, t_id in g[mark]:
                self.view.reach_canvas.update_graph(new_mark=str(new_mark),
                                                    prev_mark=str(mark),
                                                    trans_original_id=str(t_id))

        self.load_marking_from_reach_graph(str(self.net.initial_mark))
        if not self.net.bounded:
            self.view.reach_canvas.highlight_unbounded(str(self.net.m_null), str(self.net.m_last))

    def reset_reachability_graph(self):
        if self.net.mark is None:
            return
        self.net.set_mark(self.net.initial_mark)
        self.view.petri_canvas.update_labels(self.net.mark)
        self.view.reach_canvas.reset_graph()
        reach_canvas_label = str(self.net.mark)
        self.view.reach_canvas.initialize_graph('(' + reach_canvas_label[1:-1] + ')')