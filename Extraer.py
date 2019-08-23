import netCDF4 
import numpy as np
import pandas as pd
from wrf import to_np, getvar, CoordPair, vertcross, disable_xarray, ll_to_xy,omp_get_num_procs
import wrf
import math
from glob import glob 
import xarray as xr
import time

def ls(expr = '*.*'):
    return glob(expr)


Direccion = 'D:/WRF/WRF19-08-2019/'
Dominio = '4'
Anio = '2018'
Mes = '03'
Dia = '01'
Fecha = Anio+'-'+Mes+'-'
archivos = ls(Direccion + '*wrfout_d0'+Dominio+'_'+Fecha+'*')

# Open the NetCDF file
index = archivos[0].find("wrfout_d0")
filename = Direccion+archivos[0][index:]   # el programa debe estar en la misma carpeta de las extensiones .nc

print(filename)
ncfile = netCDF4.Dataset(filename)
altura = ncfile.variables['HGT'][:]
print(altura.shape)
z = getvar(ncfile,'z',meta=False) 
wspd =  getvar(ncfile, "uvmet_wspd_wdir",meta=False)[0,:]
lats = getvar(ncfile, 'lat',meta=False)
lons = getvar(ncfile, 'lon',meta=False)
UU, VV = wrf.g_uvmet.get_uvmet(ncfile,meta= False)
coor = wrf.ll_to_xy(ncfile, -17.6290737, -65.2842807, timeidx=0, meta=False, as_int=True) # Lat Lon cerca de Qollpana
ncfile.close()

print(lons[coor[1],coor[0]])
print(lats[coor[1],coor[0]])


#   Extrayendo los datos con MFdataset
Fecha = Anio+'-'+Mes
archivos = ls(Direccion + 'wrfout_d0'+Dominio+'_'+Fecha+'*')
# print(archivos)
index = archivos[0].find("wrfout_d0")
lista = archivos[:][index:]
print(coor)
start = time.time()
# f = netCDF4.MFDataset("D:/WRF/WRF15-08-19/wrfout_d04*")
test = xr.open_mfdataset("D:/WRF/WRF19-08-2019/wrfout_d04_2018-03*")
V10 = test.V10.values
U10 = test.U10.values
Time = test.XTIME.values
T2 = test.T2.values
i = coor[0]
j = coor[1]
print(V10.shape)
print(Time.shape)

end = time.time()
print('Tiempo de ejecucion de lectura: ', end - start)
# Angulo en coordenadas matematicas
direccion = np.arctan2(V10[:,j,i], U10[:,j,i]) * 180 / np.pi
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
R = np.sqrt(U10[:,j,i]*U10[:,j,i]+V10[:,j,i]*V10[:,j,i])

# Calculando la magnitud de la temperatura
Temp = T2[:,j,i]
Temp = Temp-273.15

#********************************************************************************
#               Exporting Data to CSV format
#               ****************************

df2 = pd.DataFrame({'Time': Time,
                    'T2s_1s': Temp,
                    'W10s_1s': R,
                    'Wds_1s': direccion
                    })

df2 = df2[['Time', 'T2s_1s','W10s_1s','Wds_1s']]          # set order of columns

df2.to_csv('Marzo2018v2.csv')

