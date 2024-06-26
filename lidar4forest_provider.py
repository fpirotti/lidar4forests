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

import os
import sys
import inspect
from qgis.core import QgsProcessingProvider,  QgsApplication
from qgis.PyQt.QtGui import *
from .lidar4forest_01_setup_project import LidarSetupProject
#from .lidar4forest_00_about import Lidar4ForestAbout
from .lidar4forest_01_global_setup import Lidar4ForestGlobalSetup

import subprocess

class LidarForForestProvider(QgsProcessingProvider):

    def __init__(self):
        """
        Default constructor.
        """
        QgsProcessingProvider.__init__(self)

    def unload(self):
        """
        Unloads the provider. Any tear-down steps required by the provider
        should be implemented here.
        """
        pass

    def loadAlgorithms(self):
        """
        Loads all algorithms belonging to this provider.
        """
        self.addAlgorithm(Lidar4ForestGlobalSetup())
        self.addAlgorithm(LidarSetupProject())
        #self.addAlgorithm(Lidar4ForestAbout())
        # add additional algorithms here
        # self.addAlgorithm(MyOtherAlgorithm())


    def id(self):
        """
        Returns the unique provider id, used for identifying the provider. This
        string should be a unique, short, character only string, eg "qgis" or
        "gdal". This string should not be localised.
        """
        return 'lidar4forest'

    def name(self):
        """
        Returns the provider name, which is used to describe the provider
        within the GUI.

        This string should be short (e.g. "Lastools") and localised.
        """
        return self.tr('Lidar4Forests')

    def icon(self):
        """
        Should return a QIcon which is used for your provider inside
        the Processing toolbox.
        """

        cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
        icon = QIcon(os.path.join(os.path.join(cmd_folder, 'assets/icons/logo.png')))
        return icon
        #return QgsProcessingProvider.icon(self)

    def longName(self):
        """
        Returns the a longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools
        (version 2.2.1)". This string should be localised. The default
        implementation returns the same string as name().
        """
        return "Lidar processing for forestry applications."
