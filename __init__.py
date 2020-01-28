# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QWaterModel
                                 A QGIS plugin
 QWatermodel is a simple tool to calculate Evapotranspiration from thermal images.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-01-11
        copyright            : (C) 2020 by Florian Ellsäßer
        email                : el-flori@gmx.de
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load QWaterModel class from file QWaterModel.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .qwatermodel import QWaterModel
    return QWaterModel(iface)
