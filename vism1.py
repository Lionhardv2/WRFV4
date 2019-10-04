import xarray as xr
import numpy as np
import salem
import matplotlib.pyplot as plt
from salem.utils import get_demo_file
from salem import open_wrf_dataset, get_demo_file
from salem import geogrid_simulator
import cartopy
from salem import mercator_grid, Map, open_xr_dataset

# fpath = get_demo_file('namelist_mercator.wps')
fpath = 'namelist2.wps'
with open(fpath, 'r') as f:  # this is just to show the file
    print(f.read())

g, maps = geogrid_simulator(fpath)
print(g)
print('ss')
print(maps[0])
maps[0].set_rgb(natural_earth='lr')
maps[0].visualize(title='Anidamiento Qollpana Marzo 2018',addcbar=False)
plt.savefig('QollpanaMarzo2018.png', dpi=300)

plt.show()
plt.close()
#ALBBCK
ds = open_xr_dataset("/home/opti3040a/Documentos/WRF15-08-19/wrfout_d01_2018-03-05_00:00:00")
grid = mercator_grid(center_ll=( -60.0,-17.9), extent=(75e5, 75e5))
smap = Map(grid, nx=500)
# VAR_SSO
smap.set_data(ds.LANDMASK) 
smap.visualize()
plt.show()


# # get the data at the latest time step
# ds = salem.open_wrf_dataset("/home/opti3040a/Documentos/WRF_1s/WRF_OUT/wrfout_d03_2018-06-01_09:00:00").isel(time=-1)
# print(ds.WS)
# # get the wind data at 10000 m a.s.l.
# u = ds.salem.wrf_zlevel('U', 2800.)
# v = ds.salem.wrf_zlevel('V', 2800.)
# ws = ds.salem.wrf_zlevel('WS', 2800.)

# # get the axes ready
# f, ax = plt.subplots()

# # plot the salem map background, make countries in grey
# smap = ds.salem.get_map(countries=False)
# smap.set_shapefile(countries=True, color='grey')
# smap.plot(ax=ax)

# # transform the coordinates to the map reference system and contour the data
# xx, yy = smap.grid.transform(ws.west_east.values, ws.south_north.values,
#                              crs=ws.salem.grid.proj)
# cs = ax.contour(xx, yy, ws, cmap='viridis', levels=np.arange(0, 81, 10),
#                 linewidths=2)

# # Quiver only every 7th grid point
# u = u[4::7, 4::7]
# v = v[4::7, 4::7]
# print('u')
# print(u)
# print('v')
# print(v)
# # transform their coordinates to the map reference system and plot the arrows
# xx, yy = smap.grid.transform(u.west_east.values, u.south_north.values,
#                              crs=u.salem.grid.proj)
# xx, yy = np.meshgrid(xx, yy)
# qu = ax.quiver(xx, yy, u.values, v.values)
# qk = plt.quiverkey(qu, 0.7, 0.95, 50, '50 m s$^{-1}$',
#                    labelpos='E', coordinates='figure')

# # done!
# plt.show()