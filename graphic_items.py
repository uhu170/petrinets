from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsItem, QGraphicsTextItem, QGraphicsLineItem, QStyleOptionGraphicsItem, QWidget
from PySide6.QtGui import QPen, QPolygonF, QColor, QBrush, QPainter
from PySide6.QtCore import QPointF
import math
from typing import Callable

class PlaceNode(QGraphicsEllipseItem):
    """
    A graphical item representing a place in a Petri net.
    """
    def __init__(self, x: float, y: float, model_id: int, name: str, on_click: Callable[[int], None] | None = None) -> None:
        """
        Initialize the PlaceNode.

        Args:
            x: The x-coordinate of the place.
            y: The y-coordinate of the place.
            model_id: The ID of the place in the model.
            name: The name of the place.
            on_click: A callback function to execute when the place is clicked.
        """
        self.radius = 20
        super().__init__(-self.radius, -self.radius, 2*self.radius, 2*self.radius)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("white")))
        self.setPen(QColor("black"))
        self.selected = False
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.edges: list['Edge'] = []
        self.name = name
        self.model_id = model_id
        self.on_click = on_click

        # Token count label inside the circle
        self.token_label = QGraphicsTextItem(str(0), self)
        self.token_label.setDefaultTextColor(QColor("black"))
        self.token_label.setPos(-self.token_label.boundingRect().width() / 2,
                                -self.token_label.boundingRect().height() / 2)
        self.label = self.token_label

        # Name label below the circle
        self.name_label = QGraphicsTextItem(name, self)
        self.name_label.setDefaultTextColor(QColor("black"))
        name_rect = self.name_label.boundingRect()
        self.name_label.setPos(-name_rect.width() / 2, self.radius + 2)

    def mousePressEvent(self, event) -> None:
        """
        Handle mouse press events.
        """
        if self.on_click:
            self.on_click(self.model_id)
        super().mousePressEvent(event)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value) -> object:
        """
        Handle item changes, such as position changes.
        """
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edges:
                edge.update_position()
        return super().itemChange(change, value)

    def set_selected(self, value: bool) -> None:
        """
        Set the selection state of the place.

        Args:
            value: True if selected, False otherwise.
        """
        self.selected = value
        self.setBrush(QBrush(QColor("yellow") if value else QColor("white")))
        self.update()


class MarkingNode(QGraphicsRectItem):
    """
    A graphical item representing a marking in the reachability graph.
    """
    def __init__(self, x: float, y: float, marking_str: str, on_click: Callable[[str], None] | None = None) -> None:
        """
        Initialize the MarkingNode.

        Args:
            x: The x-coordinate of the marking node.
            y: The y-coordinate of the marking node.
            marking_str: The string representation of the marking.
            on_click: A callback function to execute when the marking node is clicked.
        """
        super().__init__()

        text_item = QGraphicsTextItem(marking_str)
        text_rect = text_item.boundingRect()
        rect_width = max(60, int(text_rect.width()) + 10)
        rect_height = 30

        self.setRect(-rect_width/2, -rect_height/2, rect_width, rect_height)

        self.setPos(x, y)
        self.setBrush(QBrush(QColor("white")))
        self.setPen(QColor("black"))

        self.selected = False
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        self.edges: list['Edge'] = []
        self.model_id = marking_str
        self.on_click = on_click

        self.label = QGraphicsTextItem(marking_str, self)
        self.label.setDefaultTextColor(QColor("black"))
        label_rect = self.label.boundingRect()
        self.label.setPos(-label_rect.width()/2, -label_rect.height()/2)

    def mousePressEvent(self, event) -> None:
        """
        Handle mouse press events.
        """
        if self.on_click:
            self.on_click(self.model_id)
        super().mousePressEvent(event)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value) -> object:
        """
        Handle item changes, such as position changes.
        """
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edges:
                edge.update_position()
        return super().itemChange(change, value)

class TransitionNode(QGraphicsRectItem):
    """
    A graphical item representing a transition in a Petri net.
    """
    def __init__(self, x: float, y: float, model_id: int, name: str, on_click: Callable[[int], None] | None = None, width: float = 20, height: float = 40) -> None:
        """
        Initialize the TransitionNode.

        Args:
            x: The x-coordinate of the transition.
            y: The y-coordinate of the transition.
            model_id: The ID of the transition in the model.
            name: The name of the transition.
            on_click: A callback function to execute when the transition is clicked.
            width: The width of the transition rectangle.
            height: The height of the transition rectangle.
        """
        super().__init__(-width/2, -height/2, width, height)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("white")))
        self.setPen(QColor("black"))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.edges: list['Edge'] = []
        self.model_id = model_id
        self.on_click = on_click

        self.label = QGraphicsTextItem(name, self)
        self.label.setDefaultTextColor(QColor("black"))
        label_rect = self.label.boundingRect()
        # Position label below the rectangle
        self.label.setPos(-label_rect.width()/2, self.rect().height()/2 + 2)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value) -> object:
        """
        Handle item changes, such as position changes.
        """
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edges:
                edge.update_position()
        return super().itemChange(change, value)

    def mousePressEvent(self, event) -> None:
        """
        Handle mouse press events.
        """
        if self.on_click:
            self.on_click(self.model_id)
        super().mousePressEvent(event)

class Edge(QGraphicsLineItem):
    """
    A graphical item representing an edge (arc) in a Petri net or reachability graph.
    """
    def __init__(self, source: PlaceNode | TransitionNode | MarkingNode, target: PlaceNode | TransitionNode | MarkingNode, label: str) -> None:
        """
        Initialize the Edge.

        Args:
            source: The source node.
            target: The target node.
            label: The label of the edge.
        """
        super().__init__()
        self.source = source
        self.target = target
        self.label = label
        self.setPen(QPen(QColor("black"), 2))
        self.arrow_size = 10

        self.source.edges.append(self)
        self.target.edges.append(self)
        self.arrow_head = QPolygonF()

        self.update_position()

    def update_position(self) -> None:
        """
        Update the position of the edge based on the source and target positions.
        """
        start = self.source.scenePos()
        end = self.target.scenePos()

        dx = end.x() - start.x()
        dy = end.y() - start.y()
        length = math.hypot(dx, dy)
        if length == 0:
            return

        if hasattr(self.source, "radius"):  # Kreis
            start_offset = self.source.radius
        else:
            start_offset = max(self.source.rect().width(), self.source.rect().height()) / 2

        if hasattr(self.target, "radius"):
            end_offset = self.target.radius
        else:
            end_offset = max(self.target.rect().width(), self.target.rect().height()) / 2

        start_x = start.x() + dx / length * start_offset
        start_y = start.y() + dy / length * start_offset
        end_x = end.x() - dx / length * end_offset
        end_y = end.y() - dy / length * end_offset

        self.setLine(start_x, start_y, end_x, end_y)
        self.update_arrow()

    def update_arrow(self) -> None:
        """
        Update the arrow head of the edge.
        """
        line = self.line()
        dx = line.x2() - line.x1()
        dy = line.y2() - line.y1()
        angle = math.atan2(dy, dx)

        p1 = QPointF(
            line.x2() - self.arrow_size * math.cos(angle - math.pi / 6),
            line.y2() - self.arrow_size * math.sin(angle - math.pi / 6)
        )
        p2 = QPointF(
            line.x2() - self.arrow_size * math.cos(angle + math.pi / 6),
            line.y2() - self.arrow_size * math.sin(angle + math.pi / 6)
        )

        self.arrow_head = QPolygonF([QPointF(line.x2(), line.y2()), p1, p2])
        self.update()

    def boundingRect(self):
        """
        Get the bounding rectangle of the edge.
        """
        extra = self.arrow_size + 2
        rect = super().boundingRect()
        return rect.adjusted(-extra, -extra, extra, extra)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None) -> None:
        """
        Paint the edge and its arrow head.
        """
        super().paint(painter, option, widget)
        if self.arrow_head:
            painter.setBrush(QColor("black"))
            painter.setPen(QPen(QColor("black"), 2))
            painter.drawPolygon(self.arrow_head)