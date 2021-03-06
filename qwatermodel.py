# -*- coding: utf-8 -*-
'''
/***************************************************************************
QWaterModel - a QGIS plugin  
QWaterModel is a simple tool to calculate Evapotranspiration from thermal images.
                              -------------------
        begin                : 2020-01-11
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Florian Ellsäßer
        email                : el-flori@gmx.de
        
This QGis plugin is based on: 
    
Ellsäßer et al. (2020), Introducing QWaterModel, a QGIS plugin for predicting 
evapotranspiration from land surface temperatures, 
Environmental Modelling & Software, https://doi.org/10.1016/j.envsoft.2020.104739.

The DATTUTDUT energy-balance model is based on:
Timmermans, W.J., Kustas, W.P., Andreu, A., 2015. Utility of an automated 
thermal-based approach for monitoring evapotranspiration. 
Acta Geophys. 63, 1571–1608. https://doi.org/10.1515/acgeo-2015-0016.

More information: https://github.com/FloEll/QWaterModel
 ***************************************************************************/
For the generation of this plugin, I used: 
Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
'''

# Import libraries
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.core import QgsProject, Qgis, QgsRasterLayer
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .qwatermodel_dialog import QWaterModelDialog
import os.path
# Import Libraries for the EB-Model
import gdal
import numpy as np
import math
import datetime

# Define global variables
sb_const = 5.6704*10**(-8) # Stefan Bolzmann constant
sw_exo = 1361.5 # exo-atmospheric short wave radiation

# 
class QWaterModel:
    '''QGIS Plugin Implementation.'''

    def __init__(self, iface):
        '''Constructor.
        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        '''
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'QWaterModel_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&QWaterModel')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        '''Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        '''
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('QWaterModel', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        '''Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        '''

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        '''Create the menu entries and toolbar icons inside the QGIS GUI.'''

        icon_path = ':/plugins/qwatermodel/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Calculate evapotranspiration from thermal images.'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        '''Removes the plugin menu item and icon from QGIS GUI.'''
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&QWaterModel'),
                action)
            self.iface.removeToolBarIcon(action)
            
    def select_input_file(self):
        '''Opens a file browser and populates the output_name lineEdit widget
        with the file path and name the user chose'''
        file_name, _filter = QFileDialog.getOpenFileName(
                self.dlg, 'Select input raster name','','*.tif')
        base_name = file_name
        self.dlg.input_name.setText(file_name)
        in_raster = QgsRasterLayer(file_name, base_name)
        QgsProject.instance().addMapLayer(in_raster)
        
    def select_output_raster_file(self):
        '''Opens a file browser and populates the output_name lineEdit widget
        with the file path and name the user chose'''
        filename, _filter = QFileDialog.getSaveFileName(
                self.dlg, 'Select output raster name','','*.tif')
        self.dlg.output_raster_name.setText(filename)
            
    def select_output_file(self):
        '''Opens a file browser and populates the output_name lineEdit widget
        with the file path and name the user chose'''
        filename, _filter = QFileDialog.getSaveFileName(
                self.dlg, 'Select output file name','','*.csv')
        self.dlg.output_name.setText(filename)
        
    def read_lst_img(self,in_file, na_val=None):
            '''This function reads thermal image and extracts land sturface 
            temperature (lst) projection (prj) and georeference data (geo).
            :in_file : path and file name
            :na_val : float that specifies NaN values
            '''            
            new_raster = gdal.Open(in_file,gdal.GA_ReadOnly)
            self.dlg.lst = new_raster.GetRasterBand(1).ReadAsArray()
            self.dlg.prj = new_raster.GetProjection()
            self.dlg.geo = new_raster.GetGeoTransform()
            self.dlg.lon = float(self.dlg.geo[0])
            self.dlg.lat = float(self.dlg.geo[3])
            # set all zeros to NaN
            self.dlg.lst[self.dlg.lst == 0.0] = self.dlg.na_val
                    
    def get_model_parameters(self,in_file):
        '''This function reads the input of the gui and assigns it to the parameters'''
        self.dlg.na_val = None
        #input
        self.read_lst_img(in_file) # read the lst image
        self.dlg.tmin_thres = self.dlg.min_temp_threshold_input.text()
        self.dlg.tmax_thres = self.dlg.max_temp_threshold_input.text()
        self.dlg.tmin = self.dlg.min_temp_input.text()
        self.dlg.tmax = self.dlg.max_temp_input.text()
        self.dlg.utc = self.dlg.utc_input.text()
        self.dlg.albedo = None 
        self.dlg.surf_emis = self.dlg.surf_emis_input.text()
        self.dlg.atm_trans = self.dlg.atm_trans_input.text()
        self.dlg.atm_emis = self.dlg.atm_emis_input.text()
        self.dlg.air_temp = self.dlg.air_temp_input.text()
        self.dlg.time_period = self.dlg.time_period_input.text() 
        self.dlg.sw_irr = self.dlg.sw_irr_input.text()
        self.dlg.g_percentage = self.dlg.g_percentage_input.text()
        self.dlg.longitude_manual = self.dlg.longitude_manual_input.text()
        self.dlg.latitude_manual = self.dlg.latitude_manual_input.text()
        
        # results
        self.dlg.rn = self.dlg.rn_input.text()
        self.dlg.h = None # sensible heat flux
        self.dlg.le = None # latent heat flux
        self.dlg.g = None # ground heat flux
        self.dlg.ef = None # evaporative fraction
        self.dlg.water = None #amount of water
        
    def get_tmin_tmax(self):
        '''This function defines tmin and tmax (minimum and maximum temperatures) 
        from the gui input or from the image itself
        '''
        if self.dlg.tmin == '':
            self.dlg.tmin  = np.percentile(self.dlg.lst[~np.isnan(self.dlg.lst)], 
                                                        float(self.dlg.tmin_thres))
        else:
            pass
        if self.dlg.tmax == '':
            self.dlg.tmax  = np.percentile(self.dlg.lst[~np.isnan(self.dlg.lst)], 
                                                        float(self.dlg.tmax_thres))
        else:
            pass
        
    def get_air_temp(self):
        '''Determines air temperature: either air temperature is given with 
        input or the minimum temperature tmin is taken as air temperature as
        in Timmermans et al. (2015)
        '''
        if self.dlg.air_temp == '':
            self.dlg.air_temp = self.dlg.tmin
        else:
            pass
        
    def get_time_period(self):
        '''This function determines the time slot for temporal upscaling of 
        evapotranspirated water amount in seconds. 
        '''
        if self.dlg.time_period == '':
            self.dlg.time_period = 3600
        else:
            pass
        
    def get_albedo(self):
        '''This function determines surface albedo from input or from land surface 
        temperatures and minimum and maximum temperatures based on Timmermans et al.
        (2015), Brutsaert (1982) and Garrat (1992)
        '''
        if self.dlg.albedo == None:
            self.dlg.albedo = abs(0.05 + ((self.dlg.lst-float(self.dlg.tmin))/
                                 (float(self.dlg.tmax)-float(self.dlg.tmin))) * 0.2)
        else:
            pass
        if np.isnan(np.sum(self.dlg.albedo)):
            pass
        else:
            self.dlg.albedo[self.dlg.albedo > 1.0] = 0.25
            self.dlg.albedo[self.dlg.albedo < 0.0] = 0.05
        
            
    def get_atm_trans(self):
        '''This function determines atmospheric transmissivity 
        an adapted from Burridge and Gadd (1977) or on manual input from the GUI
        '''
        if self.dlg.atm_trans == '':
            self.dlg.atm_trans = 0.6 + 0.2 * np.sin(np.deg2rad(self.get_sol_elev_ang()))
        else:
            pass
            
    def get_sol_elev_ang(self):
        '''This part is based on the SunPositionCalculator by mperezcorrales
        original repository = https://github.com/mperezcorrales/SunPositionCalculator'''
        
        if self.dlg.longitude_manual == '' and self.dlg.latitude_manual == '':
            #get day of the year, hour and minute from the datetime format
            utc = datetime.datetime.strptime(str(self.dlg.utc),'%Y-%m-%dT%H:%M:%S')
            doy = float(utc.strftime('%j'))
            
            daytime = float(utc.hour + utc.minute/60)
            
            g = (360 / 365.25) * (doy + daytime/24)
            g_radians = math.radians(g)
            declination = (0.396372 - 22.91327 * math.cos(g_radians) + 4.02543 *
                           math.sin(g_radians) - 0.387205 * math.cos(2 * g_radians) 
                           + 0.051967 * math.sin(2 * g_radians) - 0.154527 * 
                           math.cos(3 * g_radians) + 0.084798 * math.sin(3 * g_radians))
    
            time_correction = (0.004297 + 0.107029 * math.cos(g_radians) - 1.837877 * 
                               math.sin(g_radians) - 0.837378 * math.cos(2 * g_radians) - 
                               2.340475 * math.sin(2 * g_radians))
    
            SHA = (daytime - 12) * 15 + self.dlg.lon + time_correction
    
            if (SHA > 180):
                SHA = SHA - 360
            elif (SHA < -180):
                SHA = SHA + 360
            else:
                SHA = SHA
            lat_radians = math.radians(self.dlg.lat)
            d_radians = math.radians(declination)
            SHA_radians = math.radians(SHA)
    
            SZA_radians = math.acos(
                    math.sin(lat_radians) * math.sin(d_radians) + math.cos(lat_radians) 
                    * math.cos(d_radians) * math.cos(SHA_radians))
    
            SZA = math.degrees(SZA_radians)
    
            SEA = 90 - SZA
            
            return SEA
            
        else:
            #get day of the year, hour and minute from the datetime format
            utc = datetime.datetime.strptime(str(self.dlg.utc),'%Y-%m-%dT%H:%M:%S')
            doy = float(utc.strftime('%j'))
                
            daytime = float(utc.hour + utc.minute/60)
                
            g = (360 / 365.25) * (doy + daytime/24)
            g_radians = math.radians(g)
            declination = (0.396372 - 22.91327 * math.cos(g_radians) + 4.02543 *
                           math.sin(g_radians) - 0.387205 * math.cos(2 * g_radians) 
                           + 0.051967 * math.sin(2 * g_radians) - 0.154527 * 
                           math.cos(3 * g_radians) + 0.084798 * math.sin(3 * g_radians))
        
            time_correction = (0.004297 + 0.107029 * math.cos(g_radians) - 1.837877 * 
                               math.sin(g_radians) - 0.837378 * math.cos(2 * g_radians) - 
                               2.340475 * math.sin(2 * g_radians))
        
            SHA = (daytime - 12) * 15 + float(self.dlg.longitude_manual) + time_correction
        
            if (SHA > 180):
                SHA = SHA - 360
            elif (SHA < -180):
                SHA = SHA + 360
            else:
                SHA = SHA
            lat_radians = math.radians(float(self.dlg.latitude_manual))
            d_radians = math.radians(declination)
            SHA_radians = math.radians(SHA)
        
            SZA_radians = math.acos(
                    math.sin(lat_radians) * math.sin(d_radians) + math.cos(lat_radians) 
                    * math.cos(d_radians) * math.cos(SHA_radians))
        
            SZA = math.degrees(SZA_radians)
        
            SEA = 90 - SZA
                
            return SEA
                    
      
    def get_sw_irr(self):
        '''This function determines short-wave irradiance, either from manual
        input, as described in Timmermans et al. (2015), or based on Burridge 
        and Gadd (1974) 
        '''
        # if a measured sw_irr value is available
        if self.dlg.sw_irr != '':
            pass
        # if both time and sw_irr are not available 
        elif self.dlg.sw_irr == '' and self.dlg.utc == '':
            self.dlg.sw_irr = float(self.dlg.atm_trans) * sw_exo
        # if utc is available but sw_irr is not
        # this multiplies the solar constant first with atmospheric transmissivity and also with 
        # the sinus of solar elevation angle to  
        elif self.dlg.utc != '' and self.dlg.sw_irr == '':
            self.dlg.sw_irr = sw_exo * float(self.dlg.atm_trans) * np.sin(np.deg2rad(self.get_sol_elev_ang()))
        else:
            pass
        
    def get_atm_emis(self):
        '''This function determines etermines atmospheric emissivity either from
        manual input based on Bastiaanssen et al. (1998)
        '''
        if self.dlg.atm_emis != '':
            pass
        else:
            self.dlg.atm_emis = 1.08 * (- math.log(float(self.dlg.atm_trans)))**0.265
            
    def get_evap_frac(self):
        '''This function determines the evaporative fraction as in Timmermans 
        et al. (2015) it further applies a maximum and a minimum value
        '''
        self.dlg.ef = (float(self.dlg.tmax)-self.dlg.lst)/(
                float(self.dlg.tmax)-float(self.dlg.tmin))
        if np.isnan(np.sum(self.dlg.ef)):
            pass
        else:
            self.dlg.ef[self.dlg.ef >= 1.0] = 1.0
            self.dlg.ef[self.dlg.ef <= 0.0] = 0.0
            
    def get_rn(self):
        '''This function calculates net radiation (rn) as in Timmermans et al. 
        (2015)
        '''
        # if no value for rn is specified
        if self.dlg.rn == '':
            self.dlg.rn = ((1-self.dlg.albedo) * float(self.dlg.sw_irr) + 
                           float(self.dlg.surf_emis) * float(self.dlg.atm_emis) * 
                           sb_const * (float(self.dlg.air_temp)**4) - 
                           float(self.dlg.surf_emis) * sb_const * 
                           (self.dlg.lst**4))
        # if rn is specified 
        else: 
            self.dlg.rn = float(self.dlg.rn)*self.dlg.lst/self.dlg.lst
            
    def get_g(self):
        '''This function determines the ground heat flux (g). g is computed as 
        a linear function of Rn similar as described in Liebethal and Foken (2007).
        Default values from the GUI are based on Ogée et al. (2001). If no value
        is given, g is computed according to Timmermans et al. (2015)
        '''
        if self.dlg.g_percentage == '':
            self.dlg.g = self.dlg.rn * (0.05 + ((self.dlg.lst-float(self.dlg.tmin))/
                                 (float(self.dlg.tmax)-float(self.dlg.tmin))) * 0.4)
            
        else:
            self.dlg.g = self.dlg.rn * (float(self.dlg.g_percentage) / 100)
                
        if np.isnan(np.sum(self.dlg.g)):
            pass
        else:
            self.dlg.g[self.dlg.g > 1.0] = 0.45
            self.dlg.g[self.dlg.g < 0.0] = 0.05
        
    def get_h_le(self):
        '''This function determines latent heat flux (le) and sensible heat 
        flux (h) according to evaporative fraction (ef) based on Timmermans et
        al. (2015)
        '''
        self.dlg.le = (self.dlg.rn - self.dlg.g) * self.dlg.ef
        self.dlg.h = (self.dlg.rn -self.dlg.g) - self.dlg.le
        
    def get_water(self):
        '''This function calculates the actual amount of water based on 
        Timmermans et al. (2015)
        '''
        if self.dlg.water == None:
            self.dlg.water = ((self.dlg.le*float(self.dlg.time_period)/1000000)/
                              (2.501-0.002361*(float(self.dlg.air_temp)-273.15)))
        else: 
            pass
        
    def write_output_images(self):
        '''This function writes the output data into a GeoTIFF'''
        
        rows,cols=np.shape(self.dlg.g)
        driver = gdal.GetDriverByName('GTiff')
        nbands=6
        out_raster = driver.Create(self.dlg.output_raster_name.text(), cols, 
                                   rows, nbands, gdal.GDT_Float32)
        out_raster.SetGeoTransform(self.dlg.geo)
        out_raster.SetProjection(self.dlg.prj)
        # Write net radiation rn to band 1
        band_1=out_raster.GetRasterBand(1)
        band_1.SetNoDataValue(0)
        band_1.WriteArray(self.dlg.rn)
        band_1.FlushCache()
        # Write latent heat flux le to band 2
        band_2=out_raster.GetRasterBand(2)
        band_2.SetNoDataValue(0)
        band_2.WriteArray(self.dlg.le)
        band_2.FlushCache()
        # Write sensible heat flux h to band 3
        band_3=out_raster.GetRasterBand(3)
        band_3.SetNoDataValue(0)
        band_3.WriteArray(self.dlg.h)
        band_3.FlushCache()
        # Write ground heat flux to band 4
        band_4=out_raster.GetRasterBand(4)
        band_4.SetNoDataValue(0)
        band_4.WriteArray(self.dlg.g)
        band_4.FlushCache()
        # Write evaporative fraction to band 5
        band_5=out_raster.GetRasterBand(5)
        band_5.SetNoDataValue(0)
        band_5.WriteArray(self.dlg.ef)
        band_5.FlushCache()
        # Write actual amount of evapotranspirated water to band 6
        band_6=out_raster.GetRasterBand(6)
        band_6.SetNoDataValue(0)
        band_6.WriteArray(self.dlg.water)
        band_6.FlushCache()
                
        # Flush Cache
        out_raster.FlushCache()
        del out_raster
        
        # load layer into qgis
        qgis_raster = QgsRasterLayer(self.dlg.output_raster_name.text(), 'QWaterModel Output')
        QgsProject.instance().addMapLayer(qgis_raster)
        
    def write_stats(self,file,flux_name,flux):
        file.write(flux_name + ' ' + str(np.mean(flux[~np.isnan(flux)])) + ' ' +
                              str(np.min(flux[~np.isnan(flux)])) + ' ' +
                              str(np.max(flux[~np.isnan(flux)])) + '\n'
                              )
        
    def write_output_stats(self):
        '''This function creates the output .csv file'''
        # write the output data in a .csv file
        with open(self.dlg.output_name.text(), 'w') as output_file:
            # write an out file with the most important stats
            # model parameters
            output_file.write('QWaterModel output stats:' + '\n')
            output_file.write('Input file name: ' + str(self.dlg.input_name.text()) + '\n')
            output_file.write('utc: ' + str(self.dlg.utc) + '\n')
            output_file.write('Temperature information:' + '\n')
            output_file.write('tmin: ' + str(self.dlg.tmin) + '\n')
            output_file.write('tmax: ' + str(self.dlg.tmax) + '\n')
            output_file.write('temp mean: ' + str(np.mean(self.dlg.lst[~np.isnan(self.dlg.lst)])) + '\n')
            output_file.write('Model parameters:' + '\n')
            output_file.write('surf_emis: ' + str(self.dlg.surf_emis) + '\n')
            output_file.write('atm_emis: ' + str(self.dlg.atm_emis) + '\n')
            output_file.write('atm_trans: ' + str(self.dlg.atm_trans) + '\n')
            output_file.write('solar_elev_ang: ' + str(self.get_sol_elev_ang()) + '\n')
            output_file.write('albedo mean: ' + str(np.mean(self.dlg.albedo[~np.isnan(self.dlg.albedo)])) + '\n')
            output_file.write('sw_irr: ' + str(self.dlg.sw_irr) + '\n')
            output_file.write('air_temp: ' + str(self.dlg.air_temp) + '\n')
            output_file.write('time_period: ' + str(self.dlg.time_period) + '\n')
            output_file.write('Output raster information:' + '\n')
            output_file.write('flux ' + 'mean ' + 'min ' + 'max ' + '\n')
            self.write_stats(output_file,'net radiation [W/m²]',self.dlg.rn)
            self.write_stats(output_file,'latent heat flux [W/m²]',self.dlg.le)
            self.write_stats(output_file,'sensible heat flux [W/m²]',self.dlg.h)
            self.write_stats(output_file,'ground heat flux [W/m²]',self.dlg.g)
            self.write_stats(output_file,'evaporative fraction [-]',self.dlg.ef)
            self.write_stats(output_file,'water amount [mm/time/m²]',self.dlg.water)
            
    def run(self):
        '''This function runs the plugin'''
               
        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = QWaterModelDialog()
            self.dlg.search_input_button.clicked.connect(self.select_input_file)
            self.dlg.search_output_raster_button.clicked.connect(self.select_output_raster_file)
            self.dlg.search_output_button.clicked.connect(self.select_output_file)
                
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # define in raster
            in_file = self.dlg.input_name.text()
            #selected_input_rastername = QgsProject.instance().mapLayersByName(input_rastername)[0]
            # get all the model parameters
            self.get_model_parameters(in_file)
            # get tmin and tmax if not already defined in settings
            self.get_tmin_tmax()
            # get air temperature
            self.get_air_temp()
            # get time
            self.get_time_period()
            # Calculate surface albedo 
            self.get_albedo()
            # Determine atmospheric transmissivity
            self.get_atm_trans()
            # Calculate short wave incoming radiation. 
            self.get_sw_irr()
            # Calculate atmospheric emissivity
            self.get_atm_emis()
            # Calculate evaporative fraction Lambda 
            self.get_evap_frac()
            # Calculate fluxes
            self.get_rn()
            self.get_g()
            self.get_h_le()
            # calculate the actual amount of evapotranspirated water
            self.get_water()
            # write results to a .tif file and load it into qgis
            self.write_output_images()
            # write output stats file 
            self.write_output_stats()
                         
            # Display a push message that QWaterModel was successful
            self.iface.messageBar().pushMessage(
                    'Success', 'QWaterModel was successfull!',
                    level=Qgis.Success, duration=3)       
