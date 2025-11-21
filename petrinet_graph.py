from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene

from graphic_items import PlaceNode, TransitionNode, Edge


class PetrinetCanvas(QGraphicsView):
    def __init__(self, controller, parent=None):
        self.scene = QGraphicsScene()
        super().__init__(self.scene, parent)
        self.controller = controller
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.nodes = {}
        self.edges = {}

    def add_place(self, x, y, val, model_id, name):
        p = PlaceNode(
            x, y,
            model_id=model_id,
            name=name
        )
        p.on_click = lambda mid=model_id, node_ref=p: self.controller.place_clicked(mid, node_ref)
        self.scene.addItem(p)
        p.label.setPlainText(str(val))
        p.label.setPos(-p.label.boundingRect().width() / 2,
                       -p.label.boundingRect().height() / 2)
        self.scene.update()
        self.viewport().update()
        self.nodes[model_id] = p

    def add_trans(self, x, y, model_id, name):
        t = TransitionNode(x, y, model_id, name, on_click=lambda tid=model_id: self.controller.fire_trans(tid))
        self.scene.addItem(t)
        self.scene.update()
        self.viewport().update()
        self.nodes[model_id] = t

    def add_edge(self, source_id, target_id, label):
        e = Edge(self.nodes[source_id], self.nodes[target_id], label)
        self.scene.addItem(e)
        self.scene.update()
        self.viewport().update()
        self.edges[source_id + target_id] = e

    def fit_all(self):
        bounding_rect = self.scene.itemsBoundingRect()
        self.centerOn(bounding_rect.center())
        padding = 50
        self.scene.setSceneRect(
            bounding_rect.x() - padding,
            bounding_rect.y() - padding,
            bounding_rect.width() + 2 * padding,
            bounding_rect.height() + 2 * padding
        )

    def update_labels(self, mark):
        for p_id, val in enumerate(mark):
            p = self.nodes[p_id]
            p.label.setPlainText(str(val))
            p.label.setPos(-p.label.boundingRect().width() / 2, -p.label.boundingRect().height() / 2)

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

    def reset_petrinet_graph(self):
        self.scene.clear()
        self.nodes.clear()
        self.edges.clear()