import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pyproj
import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature, OCEAN, LAKES
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import shapely.geometry as sgeom
from copy import copy
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from matplotlib.font_manager import FontProperties
import netCDF4 as nc
import re  # regular expression
from netCDF4 import MFDataset
etopo1file = '/home/opti3040a/Documentos/wrfout_d04_2018-03-26_14:00:00'

rootgroup = nc.Dataset(etopo1file, 'r', format =  "NETCDF3")
temp2 = rootgroup.variables['T2'][:]    # read temperature at 2m
dem_lat = rootgroup.variables['XLAT'][:]      # read latitutde variable
dem_lon = rootgroup.variables['XLONG'][:]     # read longitude variable
cosalpha = rootgroup.variables['COSALPHA'][0]
sinalpha = rootgroup.variables['SINALPHA'][0]
# print(rootgroup.variables)
print(temp2.shape)
print(dem_lat.shape)
print(dem_lon.shape)
temp2 = temp2.reshape(300,291)
dem_lon = dem_lon.reshape(300,291)
dem_lat = dem_lat.reshape(300,291)
print(dem_lat.shape)
rootgroup.close()

mask = temp2 > 0

temp2 = temp2*mask

temp2 = temp2 -273.15 


#******************************************************************
#           Capturando todas las variables con MFDATATEST
#******************************************************************
#wrfout_d01_2018-03-11_12:00:00 
#/home/opti3040a/Documentos/WRF_2019/run/wrfout_d01_2018-03*
f = MFDataset("/home/opti3040a/Documentos/wrfout_d04_2018-03-26_14:00:00")
time1 = f.variables["Times"][:]             # read time in format byte
temp2m = f.variables['T2'][:]        # read temperature at 2m
v10 = f.variables["V10"][:]                 # read wind velocity component at 10m
u10 = f.variables["U10"][:] # read wind velocity component at 10m
tempZ = f.variables["TMN"][:]
print(temp2m.shape)
print(v10.shape)
print(time1.shape)
print(v10.shape[0])


#******************************************************************
#					Calculando el promedio de la temp
#******************************************************************
tempac = np.zeros((300, 291))
for i in range(0,v10.shape[0]):
    tempac= temp2m[i,:,:]+tempac
print(tempac/v10.shape[0])
tempac = tempac/v10.shape[0]
tempac = tempac -273.15
print(tempac)

v10ac = np.zeros((300, 291))
for i in range(0,v10.shape[0]):
    v10ac= v10[i,:,:]+v10ac
v10ac = v10ac/v10.shape[0]
vr = v10ac
v10ac = v10ac*v10ac

u10ac = np.zeros((300, 291))
for i in range(0,v10.shape[0]):
    u10ac= u10[i,:,:]+u10ac
u10ac = u10ac/v10.shape[0]
ur = u10ac
u10ac = u10ac*u10ac

ue = ur * cosalpha - vr * sinalpha
ve = vr * cosalpha + ur * sinalpha
WindEart = np.sqrt(ue * ue +  ve * ve)


Wind = np.sqrt(v10ac+u10ac)
print(Wind)
print(v10.max())
#********************************************************
#		main code
#		*********

z_min, z_max = np.abs(WindEart).min(), np.abs(WindEart).max()
print(z_min)
print(z_max)
print(cosalpha)
wpsproj = ccrs.LambertConformal(central_longitude=-60.0, central_latitude=-17.9,
                                    standard_parallels=(-14.48, -17.42), globe=None, cutoff=10)

fig1 = plt.figure(figsize=(10,8))
ax1 = plt.axes(projection=wpsproj)
ax1.pcolormesh(dem_lon, dem_lat, WindEart, cmap='viridis', vmin=z_min, vmax=z_max, alpha=1, transform=ccrs.PlateCarree())
# ax1.pcolormesh(dem_lon, dem_lat, tempac, cmap='viridis', vmin=z_min, vmax=50, alpha=1, transform=ccrs.PlateCarree())
ax1.quiver(dem_lon, dem_lat, ue, ve, transform=ccrs.PlateCarree(), regrid_shape=50, color = 'orange')
ax1.quiver(dem_lon, dem_lat, u10ac, v10ac, transform=ccrs.PlateCarree(), regrid_shape=50)
# ax1.streamplot(dem_lon, dem_lat, ue, ve, transform=ccrs.PlateCarree(), density=3, color = 'orange')
# ax1.streamplot(dem_lon, dem_lat, u10ac, v10ac, transform=ccrs.PlateCarree(), density=5,color = 'red')
ax1.coastlines('50m', linewidth=0.8)
ax1.add_feature(OCEAN, edgecolor='k')#, facecolor='deepskyblue')
ax1.add_feature(LAKES, edgecolor='k')#, facecolor='deepskyblue')

states = NaturalEarthFeature(category='cultural', scale='10m', facecolor='none',
                             name='admin_1_states_provinces_shp')
ax1.add_feature(states, linewidth=0.5)
ax1.add_feature(cfeature.BORDERS)


fig1.canvas.draw()


xticks = [-150, -140, -130, -120, -110, -100, -90, -80, -70, -60, -50, -40,-30,-20]
yticks = [20,10,0,-10, -20,-30,-40,-50, -60, -70]
ax1.gridlines(xlocs=xticks, ylocs=yticks)
ax1.xaxis.set_major_formatter(LONGITUDE_FORMATTER) 
ax1.yaxis.set_major_formatter(LATITUDE_FORMATTER)

ax1.set_title('Anidamiento025, size=20')

cbar_ax = fig1.add_axes([0.92, 0.2, 0.02, 0.6])
cb1 = mpl.colorbar.ColorbarBase(cbar_ax, cmap='viridis', ticks=np.arange(0,1.01,0.25), orientation='vertical')
cb1.set_ticklabels([str(int(z_min)),str(int(z_max/4)),str(int(z_max/3)), str(int(z_max/2)), str(int(z_max))])
# cb1.set_ticklabels([str(int(z_min)),'','', '', '30'])
cbar_ax.tick_params(labelsize=12)
cbar_ax.text(1.1, -0.05, 'Celc', size=10)
#plt.savefig("Anidamiento Qollpana12.png")
plt.show()



