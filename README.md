# ![Logo image](https://github.com/FloEll/QWaterModel/blob/master/icon.png) QWaterModel 
QWaterModel is a simple QGis plugin tool to calculate evapotranspiration from thermal images.

It was designed to be very simple to use and provides only basic functionalities. 

# What does it do? 
QWaterModel is a tool to run a simple energy-balance model (DATTUTDUT) to calculate evapotranspiration and fluxes from land surface temperatures. 

Thermal images from various sources can be used: 

![Functionality explained image](https://github.com/FloEll/QWaterModel/blob/master/images/imageToOutput_Graph.png)

The resulting rasters contain six bands:
1. Rn net radiation [W/m²]
2. LE latent heat flux (from which evapotranspiration in band 6 is derived) [W/m²]
3. H sensible heat flux [W/m²]
4. G ground heat flux [W/m²]
5. EF evaporative fraction [-]
6. ET evapotranspiration [kg/m²/time period]

# Install QWaterModel
1. Open QGis3 
2. click on Plugins>Manage and Install Plugins
3. click on 'All' then search for 'QWaterModel' and click the 'Install Plugin' Button
4. QWaterModel should then install
5. Enable QWaterModel by ticking the field left to the QWaterModel Icon in the Plugins list. 

You should be ready to use QWaterModel now. 

# How to use it? 
When QWaterModel is installed, please follow these instructions to fill the GUI:

![GUI explained image](https://github.com/FloEll/QWaterModel/blob/master/images/HowToUseTheGUI.png)

# How to cite QWaterModel
Ellsäßer et al. (2020), Introducing QWaterModel, a QGIS plugin for predicting evapotranspiration from land surface temperatures,
Environmental Modelling & Software, https://doi.org/10.1016/j.envsoft.2020.104739.

Please also cite the DATTUTDUT energy-balance model on which this plugin is based: 

Timmermans, W.J., Kustas, W.P., Andreu, A., 2015. Utility of an automated thermal-based approach for monitoring evapotranspiration. 
Acta Geophys. 63, 1571–1608. https://doi.org/10.1515/acgeo-2015-0016. 

# More Information
QWaterModel is the result of some rainy evenings during my PhD studies in 2019 and 2020. I realized that there was no simple tool for evapotranspiration estimation and modelling out there that was simple to use, easy to access and open source. I don’t claim that it is perfect yet and due to its simplicity I cannot guarantee that it will work under all conditions. 
If you have any suggestions, ideas for improvement or further development, did you find a bug or do you want to contribute to the QWaterModel project, please feel free to contact me via github.com: https://github.com/FloEll

QGIS3 Python Plugins repository: https://plugins.qgis.org/plugins/qwatermodel/

# References
Ellsäßer et al. (2020), Introducing QWaterModel, a QGIS plugin for predicting evapotranspiration from land surface temperatures,
Environmental Modelling & Software, https://doi.org/10.1016/j.envsoft.2020.104739.

Timmermans, W.J., Kustas, W.P., Andreu, A., 2015. Utility of an automated thermal-based approach for monitoring evapotranspiration. Acta Geophys. 63, 1571–1608. https://doi.org/10.1515/acgeo-2015-0016
