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
Archivo = 'Marzo2018.csv'
dfs = pd.read_csv(Archivo, index_col= False)
dfauxs = dfs.drop(['Unnamed: 0'], axis=1)
dfauxs["Time"] = pd.to_datetime(dfauxs["Time"])
mask = dfauxs.Time.dt.day < 9
dfauxs = dfauxs.loc[mask].reset_index()

print(dfauxs.tail())
#******************************************************************
#		Comparativa dfauxs(simulado) vs dfaux(Observado)
#******************************************************************
# Generando solo un Dataframe para datos simulados y observados
df_Total = dfaux.merge(dfauxs,on=["Time"])
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
Fecha = df_Total['Time'].tolist()
plt.plot_date(Fecha,W10o,'-r')
plt.plot_date(Fecha,W10wrf,'--b')
plt.title("Comparativa Marzo 2018")
plt.ylabel('Velocidad de Viento m/s')
plt.xticks(rotation=45)
# Graficando la Correlacion
plt.subplot(2,1,2)
sns.regplot(x="W10o", y="W10s_1s",data=df_Total)
plt.title("Correlacion Viento Observado vs Simulado")
plt.text(min(W10o)*0.2,max(W10wrf)*0.8,r"$r^2 =$"+"{0:.4f}".format(pearson_coef),fontsize = 10, color = 'blue')
# plt.savefig('EstadisticosMarzoCorv2.png',dpi=300)
plt.show()
plt.close()
# Rosa de Vietos Simulado
ax = WindroseAxes.from_ax()
ax.box(dfauxs['Wds_1s'],dfauxs["W10s_1s"],normed = True, bins=np.arange(0, 23, 1) , nsector=12)
ax.set_legend()
# plt.savefig("WRQollpanaWRF.png",dpi =300)
plt.show()