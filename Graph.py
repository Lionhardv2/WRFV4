from __future__ import print_function, division
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
import netCDF4
import numpy as np
from netCDF4 import Dataset
from wrf import getvar, ALL_TIMES
import wrf
from glob import glob 
import time
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter

def ls(expr = '*.*'):
    return glob(expr)
#***********************************************************************************
#                   Encontrar el indice mas cercano a  QollpanaI
#                   ********************************************
Direccion = 'D:/WRF/WRF15-08-19/'
Dominio = '4'
Anio = '2018'
Mes = '03'
Dia = '01'
Fecha = Anio+'-'+Mes+'-'
archivos = ls(Direccion + '*wrfout_d0'+Dominio+'_'+Fecha+'*')
# Open the NetCDF file
index = archivos[0].find("wrfout_d0")
filename = Direccion+archivos[0][index:]   # el programa debe estar en la misma carpeta de las extensiones .nc
ncfile = netCDF4.Dataset(filename)
lats = getvar(ncfile, 'lat',meta=False)
lons = getvar(ncfile, 'lon',meta=False)
ncfile.close()

start = time.time()
filename_list = ls('D:/WRF/WRF15-08-19/wrfout_d04_2018-03*')
# print(filename_list)
# Result shape (hard coded for this example)
result_shape = (211, 32, 85, 80)
WindSpeed_shape = (211,1,85,80)

# Only need 4-byte floats
z_final = np.empty(result_shape, np.float32)
U10 = np.empty(WindSpeed_shape,np.float32)
V10 = np.empty(WindSpeed_shape,np.float32)
T2 = np.empty(WindSpeed_shape,np.float32)
TER = np.empty(WindSpeed_shape,np.float32)
Tiempo = ["" for x in range(0,211)]
# Modify this number if using more than 1 time per file
times_per_file = 1

for timeidx in range(result_shape[0]):
    # Compute the file index and the time index inside the file
    fileidx = timeidx // times_per_file
    file_timeidx = timeidx % times_per_file

    f = Dataset(filename_list[fileidx])
    z = getvar(f, "z", file_timeidx)
    heigh = getvar(f, 'ter', file_timeidx, meta=False)
    WS1 = getvar(f, 'U10', file_timeidx)
    WS2 = getvar(f, 'V10', file_timeidx)
    Temp = getvar(f, 'T2', file_timeidx)
    Tp = getvar(f,'times',file_timeidx, meta=False )
    U10[timeidx,:] = WS1[:]
    V10[timeidx,:] = WS2[:]
    T2[timeidx,:] = Temp[:]
    z_final[timeidx,:] = z[:]
    Tiempo[timeidx] = Tp
    TER = heigh[:]
    f.close()
end = time.time()
print(TER.shape)
# Calculando la magnitud del vector Velocidad a 10 m
R = np.sqrt(U10[:]*U10[:]+V10[:]*V10[:])
print('max R: ', R.max())
print('min  R :', R.min())
# Graficando el mapa de elevacion
fig = plt.figure()
ax = fig.gca(projection='3d')

surf = ax.plot_surface(lons, lats, TER, cmap=cm.terrain,
                       linewidth=0, antialiased=False)

# Customize the z axis.
ax.zaxis.set_major_locator(LinearLocator(10))
ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

# Add a color bar which maps values to colors.
fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()

plt.close()

plt.pcolormesh(lons, lats, R[200,0,:,:].reshape(85,80))
cbar = plt.colorbar(shrink = 0.5, aspect = 5)
cbar.set_label('m')
plt.show()