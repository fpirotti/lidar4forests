# -*- coding: utf-8 -*-

"""
/***************************************************************************
 LidarForForest
                                 A QGIS plugin
 This plugin links lidar processes via the LidR R package to QGIS
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-03-21
        copyright            : (C) 2024 by Francesco Pirotti, Larissa Falcao Granja
        email                : francesco.pirotti@unipd.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Francesco Pirotti, Larissa Falcao Granja'
__date__ = '2024-03-21'
__copyright__ = '(C) 2024 by Francesco Pirotti, Larissa Falcao Granja'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'
from qgis.gui import (QgsMessageBar)
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.uic import *
from qgis.PyQt.QtCore import (QCoreApplication)
from qgis.core import (Qgis, QgsProcessing,
                      QgsSettings,
                        QgsMessageLog,
                        QgsProject,
                        QgsProcessingParameterBoolean,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFeatureSink)

import os

from .Rsession import *
from qgis.utils import iface
import inspect
import pathlib

class LidarSetupProject(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
    INPUT = 'INPUT'
    VERBOSE = 'VERBOSE'
    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # self.bar = QgsMessageBar()
        # self.bar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed )
        #
        # self.parent.layout().addWidget(self.bar, 0, 0, 1, 1)

        s = QgsSettings()
        projectFolder1 = s.value("lidar4forests/projectFolder", "")

        # We add the input vector features source. It can have any kind of
        # geometry.
        proj = QgsProject.instance()
        projectFolder2, type_conversion_ok = proj.readEntry("lidar4forests",
                                                    "projectFolder",
                                                    "")

        # priority to project's info on where the project folder is
        if projectFolder2 == "":
            projectFolder = projectFolder1
        else:
            projectFolder = projectFolder2

        if projectFolder != "" and not os.path.exists(projectFolder):
            iface.messageBar().pushMessage("Warning", "Path of point clouds files not available", level=Qgis.Critical)

        #QgsMessageLog.logMessage("Your plugin code might have some problems", level=Qgis.Warning)

        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                self.tr('Choose project folder containing point cloud files (only LAS/LAZ supported)'),
                QgsProcessingParameterFile.Folder,
                defaultValue=projectFolder
            )
        )

        rst = RsessionStart()
        print(RsessionProcess)
        print(R_HOME)

        self.verbose = True
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.VERBOSE,
                self.tr('Output verboso'),
                defaultValue=True
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        #self.addParameter(
        #    QgsProcessingParameterFeatureSink(
        #        self.OUTPUT,
        #        self.tr('Output layer')
        #    )
        #)

    def setProgressText(self, feedback, stringin, messageType= Qgis.Info, force=False):
        if self.verbose is True or force:
            print(stringin)
            if messageType == Qgis.Warning:
                feedback.pushWarning(stringin)
            elif messageType == Qgis.Error:
                feedback.pushWarning(stringin)
            elif messageType == Qgis.Info:
                feedback.setProgressText(stringin)
            else:
                feedback.setProgressText(stringin)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.

        source = self.parameterAsFile(parameters, self.INPUT, context)

        s = QgsSettings()
        s.setValue("lidar4forests/projectFolder", source)
        proj = QgsProject.instance()
        proj.writeEntry("lidar4forests", "projectFolder", source)

        self.setProgressText(feedback, self.cmd_folder)

        files = [f for f in pathlib.Path(source).glob("*.laz")]
        for file in files:
            self.setProgressText(feedback, "File... " + str(file.name))

        return {self.OUTPUT: files}


    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Setup project'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ''


    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return LidarSetupProject()