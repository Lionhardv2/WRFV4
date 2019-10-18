import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from osgeo import gdal
import pandas as pd

import image

gdal.UseExceptions()
Archivo = '/home/opti3040a/Documentos/MapasES/Mapa Solar/GIZ_Bolivia_DIF/Bolivia_DIF_kwhm2yr_01.tif'
DEM = gdal.Open(Archivo)

DEM_Array = DEM.ReadAsArray()

DEM_ArrayM = np.ma.masked_equal(DEM_Array,DEM_Array==0)

cols = DEM.RasterXSize
rows = DEM.RasterYSize
print(cols,"\n",rows,"\n")
print(DEM_ArrayM)
i, j = np.where(DEM_ArrayM>0)
topo = DEM_ArrayM[0:max(i)+1, 0:max(j)+1]
fig = plt.figure(frameon=True)
print(type(topo))
print("array")
print(DEM_ArrayM)
print(DEM_ArrayM.shape)
print(DEM_ArrayM[2000][3000])
print("end array")
# filtrando los datos no requieridos
mask = topo >0
print(topo)
print(topo*mask)
Datos = topo*mask
#
print(topo.shape)
plt.imshow(Datos, cmap=cm.terrain)

plt.axis('off')

cbar = plt.colorbar(shrink=0.9)

cbar.set_label('m/s')
#******************************************************************
#   	Generando lista de vectores cada 0.0018 grados
#******************************************************************
latitud = -9.6257792399
longitud = -69.6851485163
escala = 0.0018
indice = 0
VectorLon = np.zeros(6822)
VectorLat = np.zeros(7398)
for indice in range(0,6822):
    VectorLon[indice] = longitud+indice*escala
for indice in range(0,2000):
    VectorLat[indice] = latitud-indice*escala
print(VectorLon)
print(VectorLat)
print(VectorLat.shape)
# print(DEM_ArrayM[latitud][longitud])
#******************************************************************
#			Construyendo el vector latitud
#******************************************************************
# NumeroTotal = 7398*6822
# indicex = 0
# Enero = []
# # array1 = [0,1,2,3]
# # array2 = [4,5,6,7]
# # array1.extend(array2)
# # print(array1)

# for i in range(0,2000):
#     Enero.extend(Datos[i][:6822])
# print(len(Enero))


