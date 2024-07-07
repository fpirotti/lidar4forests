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
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFile
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsProcessingParameterVectorDestination
from qgis.core import QgsProcessingParameterString
from qgis.core import  *

from qgis.utils import *
from qgis.core import (Qgis, QgsProcessing,
                      QgsSettings,
                        QgsMessageLog,
                        QgsProject,
                        QgsProcessingParameterBoolean,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                        QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFeatureSink)

import os

from .Rsession import *
from qgis.utils import iface
import inspect
import pathlib
dirname, filename = os.path.split(os.path.abspath(__file__))
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

    INPUT = 'INPUT'
    PARCELS = 'PARCELS'
    TARIF = 'TARIF'

    TREEPOSITION = 'TREEPOSITION'
    CHM = 'CHM'
    OUTPUT = 'OUTPUT'
    VERBOSE = 'VERBOSE'

    def __init__(self):
        super().__init__()
        self.rst = None

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """


        s = QgsSettings()
        projectFolder1 = s.value("lidar4forests/projectFolder", "")

        #
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
                'folder_with_las_files',
                self.tr('Choose project folder containing point cloud files (only LAS/LAZ supported)'),
                QgsProcessingParameterFile.Folder,
                defaultValue=projectFolder
            )
        )

        self.addParameter(QgsProcessingParameterNumber('output_chm_resolution', 'Output CHM resolution', type=QgsProcessingParameterNumber.Double, minValue=0.1, maxValue=10, defaultValue=1))
        self.addParameter(QgsProcessingParameterVectorLayer('parcels_optionally_with_tarifs', 'Parcels optionally with tarifs', optional=True, types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('Chm', 'CHM', createByDefault=True, defaultValue=None))

        self.addParameter(QgsProcessingParameterVectorDestination('ParcelsWithEstimatedTotalVolume', 'Parcels with Estimated total Volume', type=QgsProcessing.TypeVectorPoint, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterString('allometry_tarif_reference__function__see_examples', 'Allometry (tarif reference | function) ... see examples)', multiLine=True, defaultValue='v=0.0026*h^2+0.0299*h-0.478'))


        print("check Rsession1")
        self.rst = Rsession()
        print("check Rsession2")

        self.verbose = True
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.VERBOSE,
                self.tr('Output verboso'),
                defaultValue=True
            )
        )

        self.addParameter(QgsProcessingParameterVectorDestination(
                          'LasTiles',
                          'LAS Tiles',
                          type=QgsProcessing.TypeVectorPolygon,
                          createByDefault=True,
                          optional=False,
                          defaultValue=None))

    def setProgressText(self, feedback, stringin, messageType= Qgis.Info, force=False):
        if self.verbose is True or force:

            if messageType == Qgis.Warning:
                feedback.pushWarning(stringin)
            elif messageType == Qgis.Info:
                feedback.setProgressText(stringin)
            else:
                feedback.setProgressText("("+messageType+"): "+stringin)

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        source = self.parameterAsFile(parameters, 'folder_with_las_files', context)

        s = QgsSettings()
        s.setValue("lidar4forests/projectFolder", source)
        proj = QgsProject.instance()
        proj.writeEntry("lidar4forests", "projectFolder", source)
        mypath = str(pathlib.Path(source)).replace(os.sep, '/')

        geopackage = os.path.join(mypath, "ctgIndex.gpkg" )
        if not os.path.exists(geopackage):
        ##VERY VERY IMPORTANT TO ADD TWO CARRIAGE RETURNS TO READ AND BREAK IN RSESSION!
            self.rst.giveCommand("ctg <- lidR::readLAScatalog(\""+mypath+"\")\r\nsf::st_write(sf::st_as_sf(ctg), sprintf(\"%s/%s\", \""+mypath+"\", \"ctgIndex.gpkg\"))\r\n\r\n")

        self.setProgressText(feedback, mypath )

        out_vlayer = QgsVectorLayer(geopackage, "LAS Tiles")
        mess, success = out_vlayer.loadNamedStyle(dirname + "/extra/styleLAStiles.qml")
        QgsProject.instance().addMapLayer(out_vlayer)

        #files = [f for f in pathlib.Path(source).glob("*.laz")]
        #for file in files:
        #    self.setProgressText(feedback, "File... " + str(file.name))

        return {self.OUTPUT: geopackage}


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
