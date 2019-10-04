import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pyproj
import netCDF4 as nc
import cartopy.crs as ccrs
from cartopy.feature import NaturalEarthFeature, OCEAN, LAKES
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
import shapely.geometry as sgeom
from copy import copy
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from matplotlib.font_manager import FontProperties
import re  # regular expression

# /home/opti3040a/Documentos/met_em.d04.2018-03-31_12:00:00.nc
# /home/opti3040a/Documentos/met_em.d01.2018-03-27_12:00:00.nc
# /home/opti3040a/Documentos/met_em.d02.2018-03-13_12:00:00.nc
# /home/opti3040a/Documentos/met_em.d03.2018-03-30_12:00:00.nc
etopo1file = '/home/opti3040a/Documentos/WRF15-08-19/wrfout_d01_2018-03-05_00:00:00'

rootgroup = nc.Dataset(etopo1file, 'r', format =  "NETCDF3")
print(rootgroup.variables)
temp2 = rootgroup.variables['ST100200'][:]    # read temperature at 2m  ST100200
dem_lat = rootgroup.variables['CLAT'][:]      # read latitutde variable
dem_lon = rootgroup.variables['CLONG'][:]     # read longitude variable
cosalpha = rootgroup.variables['COSALPHA'][0]
sinalpha = rootgroup.variables['SINALPHA'][0]
vv = rootgroup.variables['VV'][0]
uu = rootgroup.variables['UU'][0]
ulon = rootgroup.variables['XLONG_V']
vlat = rootgroup.variables['XLAT_V']
nc_vars = [var for var in rootgroup.variables]  # list of nc variables
print(nc_vars)
print(rootgroup.variables)
print(temp2.shape)
print(dem_lat.shape)
print(dem_lon.shape)
temp2 = temp2.reshape(dem_lat.shape[1],dem_lat.shape[2])
dem_lon = dem_lon.reshape(dem_lat.shape[1],dem_lat.shape[2])
dem_lat = dem_lat.reshape(dem_lat.shape[1],dem_lat.shape[2])
print(dem_lat.shape)
rootgroup.close()




# ********************************************************
# 		main code
# 		*********

z_min, z_max = np.abs(temp2).min(), np.abs(temp2).max()
print(z_min)
print(z_max)
print(cosalpha)
wpsproj = ccrs.LambertConformal(central_longitude=-65.4, central_latitude=-17.9,
                                    standard_parallels=(-14.48, -17.42), globe=None, cutoff=10)

fig1 = plt.figure(figsize=(10,8))
ax1 = plt.axes(projection=wpsproj)
ax1.pcolormesh(dem_lon, dem_lat, temp2, cmap='viridis', vmin=z_min, vmax=z_max, alpha=1, transform=ccrs.PlateCarree())
# ax1.pcolormesh(dem_lon, dem_lat, tempac, cmap='viridis', vmin=z_min, vmax=50, alpha=1, transform=ccrs.PlateCarree())
#ax1.quiver(dem_lon, dem_lat, u10ac, v10ac, transform=ccrs.PlateCarree(), regrid_shape=10)
#ax1.streamplot(dem_lon, dem_lat, ue, ve, transform=ccrs.PlateCarree(), density=2)
#ax1.streamplot(dem_lon, dem_lat, u10ac, v10ac, transform=ccrs.PlateCarree(), density=2,color = 'red')
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

ax1.set_title('Metgrid, size=20')

cbar_ax = fig1.add_axes([0.92, 0.2, 0.02, 0.6])
cb1 = mpl.colorbar.ColorbarBase(cbar_ax, cmap='viridis', ticks=np.arange(0,1.01,0.25), orientation='vertical')
cb1.set_ticklabels([str(int(z_min)),str(int(z_max/4)),str(int(z_max/3)), str(int(z_max/2)), str(int(z_max))])
# cb1.set_ticklabels([str(int(z_min)),'','', '', '30'])
cbar_ax.tick_params(labelsize=12)
cbar_ax.text(1.1, -0.05, 'Celc', size=10)
#plt.savefig("Anidamiento Qollpana12.png")
plt.show()

print(dem_lon.max())
print(dem_lon.min())
print(dem_lat.max())
print(dem_lat.min())
