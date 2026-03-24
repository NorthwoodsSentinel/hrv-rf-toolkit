
from PySide6.QtCore import Qt, QMargins, QSize, QPointF
from PySide6.QtWidgets import QSizePolicy, QWidget
from PySide6.QtCharts import QChart, QChartView, QValueAxis, QSplineSeries, QAreaSeries
from PySide6.QtGui import QPen, QFont, QColor

class CirclesWidget(QChartView):
    def __init__(self, x_values=None, y_values=None, pacer_color=None, breathing_color=None, hr_color=None):
        super().__init__()

        self.setSizePolicy(
            QSizePolicy(
                QSizePolicy.Fixed,  # enforce self.sizeHint by fixing horizontal (width) policy
                QSizePolicy.Preferred,
            )
        )
        
        self.scene().setBackgroundBrush(Qt.white)
        self.setAlignment(Qt.AlignCenter)

        self.plot = QChart()
        self.plot.legend().setVisible(False)
        self.plot.setBackgroundRoundness(0)
        self.plot.setMargins(QMargins(0, 0, 0, 0))

        # Pacer disc
        self.pacer_circumference_coord = QSplineSeries()
        self.disk = QAreaSeries(self.pacer_circumference_coord)
        self.disk.setColor(pacer_color)
        self.plot.addSeries(self.disk)

        # Breathing disc
        self.breath_circumference_coord = QSplineSeries()
        pen = QPen(breathing_color)
        pen.setWidth(2)
        self.breath_circumference_coord.setPen(pen)
        self.plot.addSeries(self.breath_circumference_coord)   

        if x_values is not None and y_values is not None:
            self._instantiate_series(x_values, y_values)

        # Axes
        self.x_axis = QValueAxis()
        self.x_axis.setRange(-1, 1)
        self.x_axis.setVisible(False)
        self.plot.addAxis(self.x_axis, Qt.AlignBottom)
        self.disk.attachAxis(self.x_axis)
        self.breath_circumference_coord.attachAxis(self.x_axis)

        self.y_axis = QValueAxis()
        self.y_axis.setRange(-1, 1)
        self.y_axis.setVisible(False)
        self.plot.addAxis(self.y_axis, Qt.AlignLeft)
        self.disk.attachAxis(self.y_axis)
        self.breath_circumference_coord.attachAxis(self.y_axis)
        
        self.setChart(self.plot)

        # Phase label (Inhale/Exhale) centered on the chart
        self.phase_label = self.scene().addText("", QFont("Arial", 14))
        self.phase_label.setDefaultTextColor(QColor(0, 0, 0))
        self.phase_label.setZValue(10)  # Draw on top of the disc

    def _instantiate_series(self, x_values, y_values):
        for x, y in zip(x_values, y_values):
            self.pacer_circumference_coord.append(x, y)
            self.breath_circumference_coord.append(0, 0)

    def update_pacer_series(self, x_values, y_values):
        for i, (x, y) in enumerate(zip(x_values, y_values)):
            self.pacer_circumference_coord.replace(i, x, y)

    def update_breath_series(self, x_values, y_values):
        for i, (x, y) in enumerate(zip(x_values, y_values)):
            self.breath_circumference_coord.replace(i, x, y)

    def update_phase_label(self, text):
        """Update the Inhale/Exhale label centered on the pacer disc"""
        self.phase_label.setPlainText(text)
        # Map chart coordinate (0, 0) to scene position for centering
        center = self.chart().mapToPosition(QPointF(0, 0))
        rect = self.phase_label.boundingRect()
        self.phase_label.setPos(center.x() - rect.width() / 2,
                                center.y() - rect.height() / 2)

    def sizeHint(self):
        height = self.size().height()
        return QSize(height, height)  # force square aspect ratio

    def resizeEvent(self, event):
        if self.size().width() != self.size().height():
            self.updateGeometry()  # adjusts geometry based on sizeHint
        return super().resizeEvent(event)

class SquareWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
    def sizeHint(self):
        return QSize(100, 100)

    def resizeEvent(self, event):
        side = min(self.width(), self.height())
        if self.width() > self.height():
            self.setMaximumHeight(side)
            self.setMaximumWidth(side)
        else:
            self.setMaximumWidth(side)
            self.setMaximumHeight(side)
