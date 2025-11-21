# reachability_graph.py
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView
from PySide6.QtGui import QBrush, QPainter, QColor
from graphic_items import Edge, MarkingNode


class ReachabilityGraphView(QGraphicsView):
    def __init__(self, controller, parent=None):
        self.scene = QGraphicsScene()
        super().__init__(self.scene, parent)
        self.controller = controller
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.current_marking = None
        self.nodes = {}
        self.edges = {}
        self.parents = {}  # child_marking -> list of parent markings
        self.layer_nodes = {}  # layer -> list of marking strings
        self.layers = {}
        self.layer_counts = {}

    def initialize_graph(self, mark: str):
        self.reset_graph()
        self.add_marking(mark)
        self.layers[mark] = 0
        self.layer_counts[0] = 0
        self.layer_nodes[0] = [mark]
        m = self.nodes[mark]
        m.setPos(0, 0)
        self.highlight_marking(mark)

    def update_graph(self, new_mark, prev_mark, trans_original_id):
        self.add_marking(marking_str=new_mark)
        # Register parent relation
        if new_mark not in self.parents:
            self.parents[new_mark] = []
        if prev_mark not in self.parents[new_mark]:
            self.parents[new_mark].append(prev_mark)

        # Determine layer assignment
        if new_mark not in self.layers and prev_mark in self.layers:
            new_layer = self.layers[prev_mark] + 1
            self.layers[new_mark] = new_layer

            if new_layer not in self.layer_nodes:
                self.layer_nodes[new_layer] = []
            self.layer_nodes[new_layer].append(new_mark)

            sortable = []
            for mark in self.layer_nodes[new_layer]:
                px = []
                for p in self.parents.get(mark, []):
                    if p in self.nodes:
                        px.append(self.nodes[p].x())
                if px:
                    px.sort()
                    median_x = px[len(px) // 2]
                else:
                    median_x = 0
                sortable.append((median_x, mark))
            sortable.sort(key=lambda t: t[0])

            self.layer_nodes[new_layer] = [t[1] for t in sortable]
            spacing = 200
            total = len(self.layer_nodes[new_layer])
            offset = -((total - 1) * spacing) / 2  # center the layer

            for idx, m_id in enumerate(self.layer_nodes[new_layer]):
                x = offset + idx * spacing
                y = new_layer * 120
                self.nodes[m_id].setPos(x, y)
        self.add_edge(prev_mark, new_mark, trans_original_id=trans_original_id)
        self.highlight_marking(new_mark)

    def add_marking(self, marking_str):
        if marking_str in self.nodes:
            return
        marking = MarkingNode(0, 0, marking_str, on_click=lambda m=marking_str: self.controller.load_marking_from_reach_graph(m))
        self.scene.addItem(marking)
        self.scene.update()
        self.viewport().update()
        self.nodes[marking_str] = marking


    def add_edge(self, source_item_id, target_item_id, trans_original_id):
        edge_id = source_item_id + trans_original_id + target_item_id
        if edge_id in self.edges:
            return
        edge = Edge(self.nodes[source_item_id], self.nodes[target_item_id], edge_id)
        self.edges[edge_id] = edge
        self.scene.addItem(edge)


    def wheelEvent(self, event):
        zoom_in_factor = 1.01
        zoom_out_factor = 0.99
        pos = event.position().toPoint()
        cursor_scene_pos = self.mapToScene(pos)
        zoom_factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor
        self.scale(zoom_factor, zoom_factor)
        new_cursor_pos = self.mapToScene(pos)
        delta = new_cursor_pos - cursor_scene_pos
        self.translate(delta.x(), delta.y())

    def highlight_marking(self, marking_str):
        # Unhighlight previous marking
        if self.current_marking is not None:
            if hasattr(self.current_marking, "setBrush"):
                self.current_marking.setBrush(QBrush(QColor("white")))

        # Update current marking
        if marking_str in self.nodes:
            self.current_marking = self.nodes[marking_str]
            if hasattr(self.current_marking, "setBrush"):
                self.current_marking.setBrush(QBrush(QColor("yellow")))
        else:
            self.current_marking = None

    def highlight_unbounded(self, m_null, m_last):
        if m_null in self.nodes:
            if hasattr(self.nodes[m_null], "setBrush"):
                self.nodes[m_null].setBrush(QBrush(QColor("red")))
        if m_last in self.nodes:
            if hasattr(self.nodes[m_last], "setBrush"):
                self.nodes[m_last].setBrush(QBrush(QColor("pink")))

    def reset_graph(self):
        self.edges.clear()
        self.nodes.clear()
        self.current_marking = None
        self.layers.clear()
        self.layer_counts.clear()
        self.parents.clear()
        self.layer_nodes.clear()
        self.scene.clear()