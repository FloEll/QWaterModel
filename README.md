# QWaterModel
QWaterModel is a simple QGis plugin tool to calculate Evapotranspiration from thermal images.

It was designed to be very simple to use and provides only basic functionalities. 

# What does it do? 
QWaterModel is a tool to run a simple energy-balance model (DATTUTDUT) to calculate evapotranspiration and fluxes from land surface temperatures. 

Thermal images from various sources can be used: 

![Functionality explained](https://github.com/FloEll/QWaterModel/blob/master/images/imageToOutput_Graph.png)

The resulting rasters contain six bands:
1. Rn net radiation [W/m²]
2. LE latent heat flux (from which evapotranspiration in band 6 is derived) [W/m²]
3. H sensible heat flux [W/m²]
4. G ground heat flux [W/m²]
5. EF evaporative fraction [-]
6. ET evapotranspiration [mm/m²/time period]

# Installation
For installation please also install the astropy package: 
https://docs.astropy.org/en/stable/install.html

# How to use it? 
When QWaterModel is installed, please follow these instructions to fill the GUI:

![GUI explained](https://github.com/FloEll/QWaterModel/blob/master/images/HowToUseTheGUI.png)

# Background information
I used several energy-balance models and tried to create a simple to use tool that can be used without any programming skills using a simple GUI in QGis3. 

QWaterModel is based on the DATTUTDUT energy balance model from Timmermans et al. (2015). It further uses methods from Brutsaert (1982), Brenner et al. (2018), Burridge and Gadd (1975), Ellsäßer et al. (2020), Garrat (1992), Liebethal and Foken (2007), Ogée et al. (2001). See references below:

Brenner, C., Zeeman, M., Bernhardt, M., Schulz, K., 2018. Estimation of evapotranspiration of temperate grassland based on high-resolution thermal and visible range imagery from unmanned aerial systems. Int. J. Remote Sens. 39, 5141–5174. https://doi.org/10.1080/01431161.2018.1471550

Brutsaert, W., 1982. Evaporation into the Atmosphere. Theory, history, and applications. Springer, Dordrecht, 299. http://dx.doi.org/10.1007/978-94-017-1497-6

Burridge, D.M., Gadd, A.J., 1977. The Meteorological Office operational 10-level numerical weather prediction model (December 1975), Scientific paper - Meteorological Office. British Meteorological Office, Bracknell, England.

Florian Ellsäßer, Christian Stiegler, Alexander Röll, Tania June, Hendrayanto, Alexander Knohl, Dirk Hölscher 'Predicting evapotranspiration from drone-based thermography – a method comparison in a tropical oil palm plantation' submitted to Agriculture and Forest Meteorology in January 2020

Garratt, J.R., 1992. The Atmospheric Boundary Layer. Cambridge University Press, Cambridge.

Liebethal, C., Foken, T., 2007. Evaluation of six parameterization approaches for the ground heat flux. Theor. Appl. Climatol. 88, 43–56. https://doi.org/10.1007/s00704-005-0234-0

Ogée, J., Lamaud, E., Brunet, Y., Berbigier, P., Bonnefond, J.., 2001. A long-term study of soil heat flux under a forest canopy. Agric. For. Meteorol. 106, 173–186. https://doi.org/10.1016/S0168-1923(00)00214-8

Timmermans, W.J., Kustas, W.P., Andreu, A., 2015. Utility of an automated thermal-based approach for monitoring evapotranspiration. Acta Geophys. 63, 1571–1608. https://doi.org/10.1515/acgeo-2015-0016



