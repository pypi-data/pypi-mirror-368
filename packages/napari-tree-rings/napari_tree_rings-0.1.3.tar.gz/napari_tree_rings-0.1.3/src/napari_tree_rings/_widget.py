"""
Widgets of the napari-tree-ring plugin.
"""

import os
import napari
from napari.qt.threading import create_worker
from typing import TYPE_CHECKING
from pathlib import Path
from qtpy.QtGui import QIcon
from qtpy.QtCore import Qt
from qtpy.QtCore import Slot
from qtpy.QtWidgets import QGroupBox, QFileDialog
from qtpy.QtWidgets import QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QWidget
from qtpy.QtWidgets import QApplication
from scyjava import jimport
from napari.layers import Image
from napari_tree_rings.progress import IndeterminedProgressThread
from napari_tree_rings.image.measure import TableTool
from napari_tree_rings.qtutil import WidgetTool, TableView
from napari_tree_rings.image.process import TrunkSegmenter
from napari_tree_rings.image.process import RingsSegmenter
from napari_tree_rings.image.process import BatchSegmentTrunk
from napari_tree_rings.image.fiji import FIJI
from napari_tree_rings.image.segmentation import SegmentTrunk


if TYPE_CHECKING:
    import napari


# noinspection PyTypeChecker
class SegmentTrunkWidget(QWidget):



    def __init__(self, viewer: "napari.viewer.Viewer"):
        super().__init__()
        self.viewer = viewer
        self.fieldWidth = 300
        self.runButton = None
        self.runBatchButton = None
        self.segmenter = None
        self.batchSegmenter = None
        self.ringsSegmenter = None
        self.measurements = {}
        self.table = TableView(self.measurements)
        self.segmentTrunkOptionsButton = None
        self.segmentRingsOptionsButton = None
        self.runSegmentRingsButton = None
        self.sourceFolderInput = None
        self.outputFolderInput = None
        self.sourceFolder = str(Path.home())
        self.outputFolder = str(Path.home())
        self.createLayout()
        self.tableDockWidget = self.viewer.window.add_dock_widget(self.table,
                                                                  area='right', name='measurements', tabify=False)
        self.onStartUpFinished()


    def createLayout(self):
        segmentLayout = self.createSegmentTrunkLayout()
        segmentRingsLayout = self.createSegmentRingsLayout()
        batchLayout = self.createBatchProcessingLayout()
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(segmentLayout)
        mainLayout.addLayout(segmentRingsLayout)
        mainLayout.addLayout(batchLayout)
        self.setLayout(mainLayout)


    def createSegmentTrunkLayout(self):
        segmentVLayout = QVBoxLayout()
        segmentLayout = QHBoxLayout()
        self.runButton = QPushButton("Run")
        self.runButton.clicked.connect(self.onRunButtonPressed)
        self.runButton.setEnabled(False)
        self.segmentTrunkOptionsButton = self.getOptionsButton(self.onOptionsButtonPressed)
        segmentLayout.addWidget(self.runButton)
        segmentLayout.addWidget(self.segmentTrunkOptionsButton)
        segmentTrunkGroupBox = QGroupBox("Segment Trunk")
        segmentTrunkGroupBox.setLayout(segmentLayout)
        segmentLayout.setContentsMargins(*self.getGroupBoxMargins())
        segmentVLayout.addWidget(segmentTrunkGroupBox)
        return segmentVLayout


    def createSegmentRingsLayout(self):
        segmentVLayout = QVBoxLayout()
        segmentLayout = QHBoxLayout()
        self.runSegmentRingsButton = QPushButton("Run")
        self.runSegmentRingsButton.clicked.connect(self.onRunSegmentRingsButtonPressed)
        self.runSegmentRingsButton.setEnabled(False)
        self.segmentRingsOptionsButton = self.getOptionsButton(self.onSegmentRingsOptionsButtonPressed)
        segmentLayout.addWidget(self.runSegmentRingsButton)
        segmentLayout.addWidget(self.segmentRingsOptionsButton)
        segmentRingsGroupBox = QGroupBox("Segment Rings")
        segmentRingsGroupBox.setLayout(segmentLayout)
        segmentLayout.setContentsMargins(*self.getGroupBoxMargins())
        segmentVLayout.addWidget(segmentRingsGroupBox)
        return segmentVLayout


    def createBatchProcessingLayout(self):
        sourceFileLayout = self.createSourceFileLayout()
        outputFileLayout = self.createOutputFileLayout()
        runBatchLayout = QHBoxLayout()
        self.runBatchButton = QPushButton("Run &Batch")
        self.runBatchButton.clicked.connect(self.runBatchButtonClicked)
        self.runBatchButton.setEnabled(False)
        runBatchLayout.addWidget(self.runBatchButton)
        batchLayout = QVBoxLayout()
        batchGroupBox = QGroupBox("Batch Segment Trunk")
        groupBoxLayout = QVBoxLayout()
        groupBoxLayout.setContentsMargins(*self.getGroupBoxMargins())
        batchGroupBox.setLayout(groupBoxLayout)
        groupBoxLayout.addLayout(sourceFileLayout)
        groupBoxLayout.addLayout(outputFileLayout)
        groupBoxLayout.addLayout(runBatchLayout)
        batchLayout.addWidget(batchGroupBox)
        return batchLayout


    @classmethod
    def getOptionsButton(cls, callback):
        resourcesPATH = os.path.join(Path(__file__).parent.resolve(), "resources", "gear.png")
        gearIcon = QIcon(resourcesPATH)
        optionsButton = QPushButton()
        optionsButton.setIcon(gearIcon)
        optionsButton.clicked.connect(callback)
        return optionsButton


    @classmethod
    def getGroupBoxMargins(cls):
        return 10, 20, 10, 20


    def createOutputFileLayout(self):
        outputFileLayout = QHBoxLayout()
        outputFolderLabel, self.outputFolderInput = WidgetTool.getLineInput(self, "Output: ",
                                                                            self.outputFolder,
                                                                            self.fieldWidth,
                                                                            self.outputFolderChanged)
        outputFolderBrowseButton = QPushButton("Browse")
        outputFolderBrowseButton.clicked.connect(self.browseOutputFolderClicked)
        outputFileLayout.addWidget(outputFolderLabel)
        outputFileLayout.addWidget(self.outputFolderInput)
        outputFileLayout.addWidget(outputFolderBrowseButton)
        return outputFileLayout


    def createSourceFileLayout(self):
        sourceFileLayout = QHBoxLayout()
        sourceFolderLabel, self.sourceFolderInput = WidgetTool.getLineInput(self, "Source: ",
                                                                            self.sourceFolder,
                                                                            self.fieldWidth,
                                                                            self.sourceFolderChanged)
        sourceFolderBrowseButton = QPushButton("Browse")
        sourceFolderBrowseButton.clicked.connect(self.browseSourceFolderClicked)
        sourceFileLayout.addWidget(sourceFolderLabel)
        sourceFileLayout.addWidget(self.sourceFolderInput)
        sourceFileLayout.addWidget(sourceFolderBrowseButton)
        return sourceFileLayout


    def getActiveLayer(self):
        if len(self.viewer.layers) == 0:
            return None
        if len(self.viewer.layers) == 1:
            layer = self.viewer.layers[0]
        else:
            layer = self.viewer.layers.selection.active
        return layer


    def onStartUpFinished(self):
        self.runButton.setEnabled(True)
        self.runSegmentRingsButton.setEnabled(True)
        self.runBatchButton.setEnabled(True)


    def onRunButtonPressed(self):
        layer = self.getActiveLayer()
        if not layer or not type(layer) is Image:
            return
        layer.metadata['path'] = layer.source.path
        self.segmenter = TrunkSegmenter(layer)
        self.segmenter.measurements = self.measurements
        worker = create_worker(self.segmenter.run,
                               _progress={'total': 4, 'desc': 'Segment Trunk'})
        worker.finished.connect(self.onSegmentationFinished)
        self.deactivateButtons()
        worker.start()


    def onRunSegmentRingsButtonPressed(self):
        print("Starting ring segmentation....")
        layer = self.getActiveLayer()
        if not layer or not type(layer) is Image:
            return
        layer.metadata['path'] = layer.source.path
        self.ringsSegmenter = RingsSegmenter(layer)
        self.ringsSegmenter.measurements = self.measurements
        worker = create_worker(self.ringsSegmenter.run,
                               _progress={'total': 4, 'desc': 'Segment Rings & Pith'})
        worker.finished.connect(self.onRingsSegmentationFinished)
        self.deactivateButtons()
        worker.start()


    def runBatchButtonClicked(self):
        if not self.sourceFolder or not (os.path.exists(self.sourceFolder) and os.path.isdir(self.sourceFolder)):
            return
        if not self.outputFolder or not (os.path.exists(self.outputFolder) and os.path.isdir(self.outputFolder)):
            return
        # imagePaths = os.listdir(self.sourceFolder)
        self.batchSegmenter = BatchSegmentTrunk(self.sourceFolder, self.outputFolder)
        worker = create_worker(self.batchSegmenter.run,
                               _progress={'desc': 'Batch Segment Trunk'})
        # worker.yielded.connect(self.onTableChanged)
        worker.finished.connect(self.activateButtons)
        self.deactivateButtons()
        worker.start()


    @Slot()
    def onSegmentationFinished(self):
        self.viewer.scale_bar.unit = self.segmenter.tiffFileTags.unit
        self.addTrunkSegmentationToViewer(self.segmenter.shapeLayer)
        self.tableDockWidget.close()
        self.measurements = self.segmenter.measurements
        self.table = TableView(self.measurements)
        self.table.saveData()
        self.tableDockWidget = self.viewer.window.add_dock_widget(self.table, area='right', name='measurements',
                                                                  tabify=False)
        self.activateButtons()


    @Slot()
    def onRingsSegmentationFinished(self):
        self.viewer.scale_bar.unit = self.ringsSegmenter.tiffFileTags.unit
        self.viewer.add_layer(self.ringsSegmenter.resultsLayer)
        self.tableDockWidget.close()
        self.measurements = self.ringsSegmenter.measurements
        self.table = TableView(self.measurements)
        self.table.saveData()
        self.tableDockWidget = self.viewer.window.add_dock_widget(self.table, area='right', name='measurements',
                                                                  tabify=False)
        self.activateButtons()


    def activateButtons(self):
        self.runButton.setEnabled(True)
        self.runSegmentRingsButton.setEnabled(True)
        self.runBatchButton.setEnabled(True)
        self.segmentTrunkOptionsButton.setEnabled(True)


    def deactivateButtons(self):
        self.runButton.setEnabled(False)
        self.runSegmentRingsButton.setEnabled(False)
        self.runBatchButton.setEnabled(False)
        self.segmentTrunkOptionsButton.setEnabled(False)


    def onOptionsButtonPressed(self):
        optionsWidget = SegmentTrunkOptionsWidget(self.viewer)
        self.viewer.window.add_dock_widget(optionsWidget, area='right', name='Options of Segment Trunk ')


    def onSegmentRingsOptionsButtonPressed(self):
        optionsWidget = SegmentRingsOptionsWidget(self.viewer)
        self.viewer.window.add_dock_widget(optionsWidget, area='right', name='Options of Segment Rings ')


    def addTrunkSegmentationToViewer(self, v):
        self.viewer.add_layer(v)
        v.edge_color = "Red"
        v.edge_width = 40
        v.blending = 'minimum'
        v.refresh()


    def sourceFolderChanged(self):
        pass


    def outputFolderChanged(self):
        pass


    def browseSourceFolderClicked(self):
        sourceFolderFromUser = QFileDialog.getExistingDirectory(self, "Source Folder", self.sourceFolder,
                                                                QFileDialog.ShowDirsOnly)
        if sourceFolderFromUser:
            self.sourceFolder = sourceFolderFromUser
            self.sourceFolderInput.setText(self.sourceFolder)


    def browseOutputFolderClicked(self):
        outputFolderFromUser = QFileDialog.getExistingDirectory(self, "Output Folder", self.outputFolder,
                                                                QFileDialog.ShowDirsOnly)
        if outputFolderFromUser:
            self.outputFolder = outputFolderFromUser
            self.outputFolderInput.setText(self.outputFolder)


    @Slot(object)
    def onTableChanged(self, measurements):
        self.measurements = measurements
        self.table = TableView(self.measurements)
        self.viewer.window.remove_dock_widget(self.tableDockWidget)
        self.tableDockWidget.close()
        self.tableDockWidget = self.viewer.window.add_dock_widget(self.table, area='right', name='measurements',
                                                                  tabify=False)



class SegmentTrunkOptionsWidget(QWidget):


    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer
        self.segmentTrunk = SegmentTrunk(None)
        self.options = self.segmentTrunk.options
        self.scaleFactorInput = None
        self.openingInput = None
        self.strokeWidthInput = None
        self.fieldWidth = 200
        self.createLayout()


    def createLayout(self):
        scaleFactorLabel, self.scaleFactorInput = WidgetTool.getLineInput(self, "Scale Factor: ",
                                                                          self.options['scale'],
                                                                          self.fieldWidth,
                                                                          self.scaleFactorChanged)
        openingRadiusLabel, self.openingInput = WidgetTool.getLineInput(self, "Opening radius: ",
                                                              self.options['opening'],
                                                              self.fieldWidth,
                                                              self.openingChanged)
        strokeWidthLabel, self.strokeWidthInput = WidgetTool.getLineInput(self, "Stroke width: ",
                                                                          self.options['stroke'],
                                                                          self.fieldWidth,
                                                                          self.strokeWidthChanged)
        saveButton = QPushButton("&Save")
        saveButton.clicked.connect(self.saveOptionsButtonPressed)
        saveAndCloseButton = QPushButton("Save && Close")
        saveAndCloseButton.clicked.connect(self.saveAndCloseButtonPressed)
        cancelAndCloseButton = QPushButton("&Cancel && Close")
        cancelAndCloseButton.clicked.connect(self.cancelAndCloseButtonPressed)
        buttonsLayout = QHBoxLayout()
        buttonsLayout.addWidget(saveButton)
        buttonsLayout.addWidget(saveAndCloseButton)
        buttonsLayout.addWidget(cancelAndCloseButton)
        mainLayout = QVBoxLayout()
        formLayout = QFormLayout()
        formLayout.setLabelAlignment(Qt.AlignRight)
        formLayout.addRow(scaleFactorLabel, self.scaleFactorInput)
        formLayout.addRow(openingRadiusLabel, self.openingInput)
        formLayout.addRow(strokeWidthLabel, self.strokeWidthInput)
        mainLayout.addLayout(formLayout)
        mainLayout.addLayout(buttonsLayout)
        self.setLayout(mainLayout)


    def scaleFactorChanged(self):
        pass


    def sigmaChanged(self):
        pass


    def openingChanged(self):
        pass


    def closingChanged(self):
        pass


    def strokeWidthChanged(self):
        pass


    def interpolationIntervalChanged(self):
        pass


    def vectorsChanged(self):
        pass


    def barkChanged(self):
        pass


    def setOptionsFromDialog(self):
        self.segmentTrunk.options['scale'] = int(self.scaleFactorInput.text().strip())
        self.segmentTrunk.options['opening'] = int(self.openingInput.text().strip())
        self.segmentTrunk.options['stroke'] = int(self.strokeWidthInput.text().strip())


    def saveOptionsButtonPressed(self):
        self.setOptionsFromDialog()
        self.segmentTrunk.saveOptions()


    def saveAndCloseButtonPressed(self):
        self.setOptionsFromDialog()
        self.segmentTrunk.saveOptions()
        self.viewer.window.remove_dock_widget(self)
        self.close()


    def cancelAndCloseButtonPressed(self):
        self.viewer.window.remove_dock_widget(self)
        self.close()



class SegmentRingsOptionsWidget(QWidget):


    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer
        self.segmentRings = RingsSegmenter(None)
        self.options = self.segmentRings.options
        self.ringsModelCombo = None
        self.pithModelCombo = None
        self.patchSizeInput = None
        self.overlapInput = None
        self.batchSizeInput = None
        self.thicknessInput = None
        self.fieldWidth = 200
        self.createLayout()


    def createLayout(self):
        ringsModelLabel, self.ringsModelCombo = WidgetTool.getComboInput(self,
                                                                        "Ring model: ",
                                                                        self.segmentRings.ringsModels)
        pithModelLabel, self.pithModelCombo = WidgetTool.getComboInput(self,
                                                                         "Pith model: ",
                                                                         self.segmentRings.pithModels)
        self.ringsModelCombo.setCurrentText(self.segmentRings.options['ringsModel'])
        patchSizeLabel, self.patchSizeInput = WidgetTool.getLineInput(self, "Patch size: ",
                                                              self.options['patchSize'],
                                                              self.fieldWidth,
                                                              self.patchSizeChanged)
        overlapLabel, self.overlapInput = WidgetTool.getLineInput(self, "Overlap: ",
                                                                      self.options['overlap'],
                                                                      self.fieldWidth,
                                                                      self.overlapChanged)
        batchSizeLabel, self.batchSizeInput = WidgetTool.getLineInput(self, "Batch size: ",
                                                                      self.options['batchSize'],
                                                                      self.fieldWidth,
                                                                      self.batchSizeChanged)
        thicknessLabel, self.thicknessInput = WidgetTool.getLineInput(self, "Thickness ",
                                                                      self.options['thickness'],
                                                                      self.fieldWidth,
                                                                      self.thicknessChanged)
        saveButton = QPushButton("&Save")
        saveButton.clicked.connect(self.saveOptionsButtonPressed)
        saveAndCloseButton = QPushButton("Save && Close")
        saveAndCloseButton.clicked.connect(self.saveAndCloseButtonPressed)
        cancelAndCloseButton = QPushButton("&Cancel && Close")
        cancelAndCloseButton.clicked.connect(self.cancelAndCloseButtonPressed)
        buttonsLayout = QHBoxLayout()
        buttonsLayout.addWidget(saveButton)
        buttonsLayout.addWidget(saveAndCloseButton)
        buttonsLayout.addWidget(cancelAndCloseButton)
        mainLayout = QVBoxLayout()
        formLayout = QFormLayout()
        formLayout.setLabelAlignment(Qt.AlignRight)
        formLayout.addRow(ringsModelLabel, self.ringsModelCombo)
        formLayout.addRow(pithModelLabel, self.pithModelCombo)
        formLayout.addRow(patchSizeLabel, self.patchSizeInput)
        formLayout.addRow(overlapLabel, self.overlapInput)
        formLayout.addRow(batchSizeLabel, self.batchSizeInput)
        formLayout.addRow(thicknessLabel, self.thicknessInput)
        mainLayout.addLayout(formLayout)
        mainLayout.addLayout(buttonsLayout)
        self.setLayout(mainLayout)



    def patchSizeChanged(self):
        pass


    def overlapChanged(self):
        pass


    def batchSizeChanged(self):
        pass


    def thicknessChanged(self):
        pass


    def saveOptionsButtonPressed(self):
        print("Saving options...")
        self.setOptionsFromDialog()
        self.segmentRings.saveOptions()


    def saveAndCloseButtonPressed(self):
        print("Saving options...")
        self.setOptionsFromDialog()
        self.segmentRings.saveOptions()
        self.viewer.window.remove_dock_widget(self)
        self.close()


    def cancelAndCloseButtonPressed(self):
        self.segmentRings.loadOptions()
        self.viewer.window.remove_dock_widget(self)
        self.close()



    def setOptionsFromDialog(self):
        self.segmentRings.options["patchSize"] = int(self.patchSizeInput.text().strip())
        self.segmentRings.options["overlap"] = int(self.overlapInput.text().strip())
        self.segmentRings.options["batchSize"] = int(self.batchSizeInput.text().strip())
        self.segmentRings.options["thickness"] = int(self.thicknessInput.text().strip())