from PySide6.QtGui import QPainter, QWheelEvent
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QWidget

from graphic_items import PlaceNode, TransitionNode, Edge


class PetrinetCanvas(QGraphicsView):
    """
    A QGraphicsView for displaying and interacting with a Petri net.
    """

    def __init__(self, controller, parent: QWidget | None = None) -> None:
        """
        Initialize the Petri net canvas.

        Args:
            controller: The controller object managing the Petri net.
            parent: The parent widget.
        """
        self.scene = QGraphicsScene()
        super().__init__(self.scene, parent)
        self.controller = controller
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.nodes: dict[int, PlaceNode | TransitionNode] = {}
        self.edges: dict[int, Edge] = {}

    def add_place(self, x: float, y: float, val: int, model_id: int, name: str) -> None:
        """
        Add a place node to the canvas.

        Args:
            x: The x-coordinate of the place.
            y: The y-coordinate of the place.
            val: The number of tokens in the place.
            model_id: The ID of the place in the model.
            name: The name of the place.
        """
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

    def add_trans(self, x: float, y: float, model_id: int, name: str) -> None:
        """
        Add a transition node to the canvas.

        Args:
            x: The x-coordinate of the transition.
            y: The y-coordinate of the transition.
            model_id: The ID of the transition in the model.
            name: The name of the transition.
        """
        t = TransitionNode(x, y, model_id, name, on_click=lambda tid=model_id: self.controller.fire_trans(tid))
        self.scene.addItem(t)
        self.scene.update()
        self.viewport().update()
        self.nodes[model_id] = t

    def add_edge(self, source_id: int, target_id: int, label: str) -> None:
        """
        Add an edge between two nodes.

        Args:
            source_id: The ID of the source node.
            target_id: The ID of the target node.
            label: The label of the edge.
        """
        e = Edge(self.nodes[source_id], self.nodes[target_id], label)
        self.scene.addItem(e)
        self.scene.update()
        self.viewport().update()
        self.edges[source_id + target_id] = e

    def fit_all(self) -> None:
        """
        Fit all items in the scene within the view.
        """
        bounding_rect = self.scene.itemsBoundingRect()
        self.centerOn(bounding_rect.center())
        padding = 50
        self.scene.setSceneRect(
            bounding_rect.x() - padding,
            bounding_rect.y() - padding,
            bounding_rect.width() + 2 * padding,
            bounding_rect.height() + 2 * padding
        )

    def update_labels(self, mark: list[int]) -> None:
        """
        Update the token labels on place nodes.

        Args:
            mark: The current marking (list of token counts).
        """
        for p_id, val in enumerate(mark):
            p = self.nodes[p_id]
            if isinstance(p, PlaceNode):
                p.label.setPlainText(str(val))
                p.label.setPos(-p.label.boundingRect().width() / 2, -p.label.boundingRect().height() / 2)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Handle mouse wheel events for zooming.

        Args:
            event: The wheel event.
        """
        zoom_in_factor = 1.01
        zoom_out_factor = 0.99

        pos = event.position().toPoint()
        cursor_scene_pos = self.mapToScene(pos)
        zoom_factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor
        self.scale(zoom_factor, zoom_factor)

        new_cursor_pos = self.mapToScene(pos)
        delta = new_cursor_pos - cursor_scene_pos
        self.translate(delta.x(), delta.y())

    def reset_petrinet_graph(self) -> None:
        """
        Clear the Petri net graph.
        """
        self.scene.clear()
        self.nodes.clear()
        self.edges.clear()