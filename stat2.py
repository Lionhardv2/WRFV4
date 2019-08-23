from pylab import *
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
import pandas as pd
from scipy import stats
from sklearn.metrics import mean_squared_error
import seaborn as sns
from windrose import WindroseAxes
register_matplotlib_converters()
#******************************************************************
#					Datos Observados
#******************************************************************
Archivo = '2017_2018Q_UTC.csv'
df = pd.read_csv(Archivo, index_col= False)
df["DT"] = pd.to_datetime(df["DT"])
mask = df.DT.dt.year == 2018
dfvar = df.loc[mask]
mask = dfvar.DT.dt.month == 3
dfaux = dfvar.loc[mask]
mask = dfaux.DT.dt.day < 9
dfaux = dfaux.loc[mask].reset_index()
print(dfaux)

# Cambiando los nombres de las columnas
dfaux.columns = ["index","Time","W10o","Wdo","T2o"]
print(dfaux.tail())
#******************************************************************
#					Datos Simulados Cada hora Marzo
#******************************************************************
Archivo = 'Marzo2018v2.csv'
dfs = pd.read_csv(Archivo, index_col= False)
dfauxs = dfs.drop(['Unnamed: 0'], axis=1)
dfauxs["Time"] = pd.to_datetime(dfauxs["Time"])
mask = dfauxs.Time.dt.day < 9
dfauxs = dfauxs.loc[mask].reset_index()

print(dfauxs.tail())
#******************************************************************
#					Datos Simulados Cada hora Marzo
#******************************************************************
Archivo = 'Marzo2018.csv'
dfs2 = pd.read_csv(Archivo, index_col= False)
dfauxs2 = dfs2.drop(['Unnamed: 0'], axis=1)
dfauxs2["Time"] = pd.to_datetime(dfauxs2["Time"])
mask = dfauxs2.Time.dt.day < 9
dfauxs2 = dfauxs2.loc[mask].reset_index()
print(dfauxs2.tail())
dfauxs2.columns = ["index","Time","T2s_1s2","W10s_1s2","Wds_1s2"]


#******************************************************************
#		Comparativa dfauxs(simulado) vs dfaux(Observado)
#******************************************************************
# Generando solo un Dataframe para datos simulados y observados
df_Total = dfaux.merge(dfauxs,on=["Time"])
df_Total = df_Total.merge(dfauxs2, on=["Time"] )
print(df_Total.head())
print(df_Total.shape)
# Calculando coeficiente de correlacion
pearson_coef, p_value = stats.pearsonr(df_Total['W10o'], df_Total['W10s_1s'])
print("coeficiente de correlacion Pearson es:",pearson_coef)
# Comparando V10o vs V10WRF
plt.subplots_adjust(hspace=0.8)
plt.subplot(2,1,1)
W10o = df_Total['W10o'].tolist()
W10wrf = df_Total['W10s_1s'].tolist()
W10wrf2 = df_Total['W10s_1s2'].tolist()
Fecha = df_Total['Time'].tolist()
plt.plot_date(Fecha,W10o,'-r', label='obse')
plt.plot_date(Fecha,W10wrf,'--b', label= 'WRF 1 km')
plt.plot_date(Fecha,W10wrf2,'--y',label= 'WRF 1.2 km')
plt.title("Comparativa Marzo 2018")
plt.ylabel('Velocidad de Viento m/s')
plt.xticks(rotation=45)
plt.legend()
# Graficando la Correlacion
plt.subplot(2,1,2)
sns.regplot(x="W10o", y="W10s_1s",data=df_Total)
plt.title("Correlacion Viento Observado vs Simulado 1Km")
plt.text(min(W10o)*0.2,max(W10wrf)*0.8,r"$r^2 =$"+"{0:.4f}".format(pearson_coef),fontsize = 10, color = 'blue')

plt.savefig('EstadisticosMarzoCorv3.png',dpi=300)

plt.show()
plt.close()
# Rosa de Vietos Simulado
ax = WindroseAxes.from_ax()
ax.box(df_Total['Wdo'],df_Total["W10o"],normed = True, bins=np.arange(0, 23, 1) , nsector=12)
ax.set_legend()
plt.title('Rosa de Vientos Observado ')
plt.savefig("WRQollpana.png",dpi =300)
plt.show()