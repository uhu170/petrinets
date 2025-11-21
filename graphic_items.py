from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsItem, QGraphicsTextItem, QGraphicsLineItem
from PySide6.QtGui import QPen, QPolygonF, QColor, QBrush
from PySide6.QtCore import QPointF
import math

class PlaceNode(QGraphicsEllipseItem):
    def __init__(self, x, y, model_id, name, on_click = None):
        radius = 20
        super().__init__(-radius, -radius, 2*radius, 2*radius)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("white")))
        self.setPen(QColor("black"))
        self.selected = False
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.edges = []
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
        self.name_label.setPos(-name_rect.width() / 2, radius + 2)

    def mousePressEvent(self, event):
        if self.on_click:
            self.on_click(self.model_id)
        super().mousePressEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edges:
                edge.update_position()
        return super().itemChange(change, value)

    def set_selected(self, value: bool):
        self.selected = value
        self.setBrush(QBrush(QColor("yellow") if value else QColor("white")))
        self.update()


class MarkingNode(QGraphicsRectItem):
    def __init__(self, x, y, marking_str, on_click=None):
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

        self.edges = []
        self.model_id = marking_str
        self.on_click = on_click

        self.label = QGraphicsTextItem(marking_str, self)
        self.label.setDefaultTextColor(QColor("black"))
        label_rect = self.label.boundingRect()
        self.label.setPos(-label_rect.width()/2, -label_rect.height()/2)

    def mousePressEvent(self, event):
        if self.on_click:
            self.on_click(self.model_id)
        super().mousePressEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edges:
                edge.update_position()
        return super().itemChange(change, value)

class TransitionNode(QGraphicsRectItem):
    def __init__(self, x, y, model_id, name, on_click = None, width=20, height=40):
        super().__init__(-width/2, -height/2, width, height)
        self.setPos(x, y)
        self.setBrush(QBrush(QColor("white")))
        self.setPen(QColor("black"))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.edges = []
        self.model_id = model_id
        self.on_click = on_click

        self.label = QGraphicsTextItem(name, self)
        self.label.setDefaultTextColor(QColor("black"))
        label_rect = self.label.boundingRect()
        # Position label below the rectangle
        self.label.setPos(-label_rect.width()/2, self.rect().height()/2 + 2)

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in self.edges:
                edge.update_position()
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        if self.on_click:
            self.on_click(self.model_id)
        super().mousePressEvent(event)

class Edge(QGraphicsLineItem):
    def __init__(self, source, target, label):
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

    def update_position(self):
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

    def update_arrow(self):
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
        extra = self.arrow_size + 2
        rect = super().boundingRect()
        return rect.adjusted(-extra, -extra, extra, extra)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        if self.arrow_head:
            painter.setBrush(QColor("black"))
            painter.setPen(QPen(QColor("black"), 2))
            painter.drawPolygon(self.arrow_head)