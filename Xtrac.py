from __future__ import print_function, division
import netCDF4
import numpy as np
from netCDF4 import Dataset
from wrf import getvar, ALL_TIMES
import wrf
from glob import glob 
import time
import pandas as pd
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
coor = wrf.ll_to_xy(ncfile, -17.6290737, -65.2842807, timeidx=0, meta=False, as_int=True) # Lat Lon cerca de Qollpana
ncfile.close()

start = time.time()
filename_list = ls('D:/WRF/WRF15-08-19/wrfout_d04_2018-03*')
print(filename_list)
# Result shape (hard coded for this example)
result_shape = (211, 32, 85, 80)
WindSpeed_shape = (211,1,85,80)

# Only need 4-byte floats
z_final = np.empty(result_shape, np.float32)
U10 = np.empty(WindSpeed_shape,np.float32)
V10 = np.empty(WindSpeed_shape,np.float32)
T2 = np.empty(WindSpeed_shape,np.float32)
Tiempo = ["" for x in range(0,211)]
TER = np.empty(WindSpeed_shape,np.float32)
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
    TER = heigh[:]
    z_final[timeidx,:] = z[:]
    Tiempo[timeidx] = Tp

    f.close()
end = time.time()


i = coor[0]
j = coor[1]
print(z_final.shape)
print(U10.shape)
print(V10.shape)
print(T2.shape)
print(TER[j,i])
print('tiempo total : ', end-start)
#**********************************************************
# Angulo en coordenadas matematicas
direccion = np.arctan2(V10[:,0,j,i], U10[:,0,j,i]) * 180 / np.pi
# print(direccion.shape)
for ii,tetha_i in enumerate(direccion):
    if tetha_i<0.0:
        direccion[ii] = direccion[ii] + 360                 # Positive degrees
# Conviertiendo a coordenadas terrestres donde N = 0 o 360
# E = 90, S = 180, W = 270
direccion = 270 - direccion
for ii,tetha_i in enumerate(direccion):
    if tetha_i<0.0:
        direccion[ii] = direccion[ii] + 360                 # Positive degrees
np.set_printoptions(suppress=True)
print(type(direccion))

# Calculando la magnitud del vector Velocidad a 10 m
R = np.sqrt(U10[:,0,j,i]*U10[:,0,j,i]+V10[:,0,j,i]*V10[:,0,j,i])

# Calculando la magnitud de la temperatura
Temp = T2[:,0,j,i]
Temp = Temp-273.15

#********************************************************************************
#               Exporting Data to CSV format
#               ****************************

df2 = pd.DataFrame({'Time': Tiempo,
                    'T2s_1s': Temp,
                    'W10s_1s': R,
                    'Wds_1s': direccion
                    })

df2 = df2[['Time', 'T2s_1s','W10s_1s','Wds_1s']]          # set order of columns

# df2.to_csv('Marzo2018v4.csv')
