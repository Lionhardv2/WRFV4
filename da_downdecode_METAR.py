
# Python libs
from datetime import datetime, timedelta
import optparse
import os 
import fortranformat as ff

import sys
reload(sys)
sys.setdefaultencoding('utf8')

def parse_params():
    """
    """
    parser = optparse.OptionParser()
    parser.add_option('-a', '--aptos-dir', dest='aptos_file',
                      help='Ubicacion del archivo de los aeropuertos a descargar, decodificar y traducir a little_r',
                      action="store", type="string")
    parser.add_option('-M', '--Metar-dir', dest='metar_dir',
                      help='Ruta de la carpeta donde se desea que se descarguen los METARes',
                      action="store", type="string")
    parser.add_option('-O', '--Obsproc-dir', dest='obsproc_dir',
                      help='Ruta de la carpeta en donde se encuentra Obsproc.exe',
                      action="store", type="string")
    parser.add_option('-s', '--start-date', dest='start_date',
                      help='Start date for simulation',
                      action="store", type="string")
    parser.add_option('--wmin',  dest='window_min',
                      help='Window minimun for data assimilation',
                      action="store", type="string")
    parser.add_option('--wmax',  dest='window_max',
                      help='Window maximum for data assimilation',
                      action="store", type="string")
    options, args = parser.parse_args()
    if any([o is None for o in [options.aptos_file, options.metar_dir,
                                options.obsproc_dir, options.start_date,
                                options.window_min, options.window_max]]):
                                
        parser.print_help()
        parser.error('all arguments are mandatory')

    
    if not os.path.isdir(options.metar_dir):
        parser.print_help()
        parser.error('%s is not a directory. It should be' % options.scada_data_dir)

    if not os.path.isdir(options.obsproc_dir):
        parser.print_help()
        parser.error('%s is not a directory. It should be' % options.scada_data_dir)

    aptos_in=options.aptos_file
    if not os.path.isfile(aptos_in) or not os.access(aptos_in, os.R_OK):
        parser.print_help()
        parser.error('%s is not a file, or cannot be read. It should be. Fix it please' % aptos_in)

    options.start_date = datetime.strptime(options.start_date, '%Y-%m-%d_%H:%M:%S')
    options.window_min = datetime.strptime(options.window_min, '%Y-%m-%d_%H:%M:%S')
    options.window_max = datetime.strptime(options.window_max, '%Y-%m-%d_%H:%M:%S')
    return options

def aptos(listaptos):
    #Lee el archivo de aeropuertos y extrae codigo ICAO, nombre de aeropuerto, longitud, latitud y altura
        a=open(listaptos,'r')
        aptos=a.readlines()
        coos={}
        for linea in aptos:
            linea=linea.rstrip('\n')
            linea=linea.split(';')
            icao=linea[0]
            coos[icao]=[] #Codigo ICAO
            coos[icao].append(linea[2]) #Latitud
            coos[icao].append(linea[3]) #Longitud
            coos[icao].append(linea[1]) #Nombre aeropuerto
            coos[icao].append(linea[4]) #altura

        return coos

def Humrel(tc,td,ps):
    from math import exp
    eslcon2=29.65
    eslcon1=17.67
    ezero=611.2  # Pa     # =30.0 mb - 35.0 mb
    celkel=273.15
    eps=0.622
    t2=tc+celkel
    td=td+celkel
    es=611.2*exp(eslcon1*(t2-celkel)/(t2-eslcon2)) #Pa,t2(K)
    ev=611.2*exp(eslcon1*(td-celkel)/(td-eslcon2)) #Pa,t2(K)
    qv=ev/(ps-ev)
    return (ev/es)*100.,qv*1000.

def Decode_metar_3DVAR(rutafile,f_temp):
    import re
    from datetime import datetime

    Hr={}
    Qv={}
    TC={}
    ps={}
    vv={}

    tabla=open(rutafile[:-8]+'.csv','w')
    print(rutafile[:-8]+'.csv')
    a=f_temp.split('\n')
    #Decodificador
    String1="(\d{6})\d{6} METAR SL\S{2} (\d{4})00.*(\d{5}KT).*(\S{2}/\S{2}).*Q(\d{4})"
    pat=re.compile(String1)
    #pat=re.compile("(\d{6})\d{6} METAR SKSM (\d{4})00.*(\d{5}KT).*(\S{2}/\S{2}) A(\d{4})")

    for li in range(1,len(a)):
        elinea=a[li]
        c=pat.search(elinea)
        print elinea
        if c!=None:
            sfecha1=c.group(1)
            shora1=c.group(2)
            fecha1=datetime.strptime(sfecha1+shora1,"%Y%m%d%H")
#            if fecha1 != efecha: continue
            dir1=c.group(3)[:3]
            dir1=int(dir1)
            vkt1=c.group(3)[3:5]
            vkt1=int(vkt1)
            vv1=vkt1*.514444 # m/s
            vv[fecha1]=vv1
            pp1=int(c.group(5))
            pp=pp1*33.855526315789476 #/25.4*1013./760. Pa
            ps[fecha1]=pp
#Humedad relativa:
            TT=c.group(4)
            try:
                TC1=int(TT[:2])
                TD1=int(TT[3:5])
                rh,q2=Humrel(TC1,TD1,pp)
            except:
#                print c.group(4),TT[:2],TT[3:5],fecha1
                TC1=9999.
                TD1=9999.
                rh=9999.
                q2=9999.
            
	        Hr[fecha1]=rh
            Qv[fecha1]=q2
            TC[fecha1]=TC1

            tabla.writelines(datetime.strftime(fecha1,"%Y%m%d%H")+';'+str(vv1)+';'+str(pp)+';'+str(TD1)+';'+str(q2)+';'+str(TC1)+'\n')
    tabla.close()
    #return vv,ps,Hr,Qv,TC
    return None


def downmetar_3DVAR(ruta,window_min,window_max,coos):
    import os,requests
    from datetime import date,timedelta,datetime
    from time import sleep
    import io

    #crear directorio
    try:
        os.makedirs(ruta)  #crea el directorio
    except:
        pass

    #extraer informacion sobre limites temporales
    iyear=window_min.strftime("%Y") 
    imonth=window_min.strftime("%m")
    iday=window_min.strftime("%d")
    ihour=window_min.strftime("%H")
    fyear=window_max.strftime("%Y") 
    print(fyear)
    fmonth=window_max.strftime("%m")
    fday=window_max.strftime("%d")
    fhour=window_max.strftime("%H")
    minute=59

    #ciclo sobre estaciones para Ogimet
    for i in coos.keys():
        print(i)
        oaci=i
        print "http://www.ogimet.com/display_metars2.php?lang=en&lugar=%s&tipo=ALL&ord=REV&nil=SI&fmt=txt&ano=%s&mes=%s&day=%s&hora=%s&anof=%s&mesf=%s&dayf=%s&horaf=%s&minf=%s&send=send" % (oaci,iyear,imonth,iday,ihour,fyear,fmonth,fday,fhour, minute)
        #print "http://www.ogimet.com/display_metars2.php?lang=en&lugar=%s&tipo=ALL&ord=REV&nil=SI&fmt=txt&ano=2018&mes=02&day=15&hora=18&anof=2018&mesf=03&dayf=01&horaf=18&minf=00&send=send" %(oaci)
        r = requests.get("http://www.ogimet.com/display_metars2.php?lang=en&lugar=%s&tipo=ALL&ord=REV&nil=SI&fmt=txt&ano=%s&mes=%s&day=%s&hora=%s&anof=%s&mesf=%s&dayf=%s&horaf=%s&minf=%s&send=send" % (oaci,iyear,imonth,iday,ihour,fyear,fmonth,fday,fhour, minute), stream=True)
        #r = requests.get(("http://www.ogimet.com/display_metars2.php?lang=en&lugar=%s&tipo=ALL&ord=REV&nil=SI&fmt=txt&ano=2018&mes=02&day=15&hora=18&anof=2018&mesf=03&dayf=01&horaf=18&minf=00&send=send") %(oaci), stream=True)
        if r.status_code == 200:
           if '%s%s%s%s' % (fyear, fmonth, fday, fhour) in r.text:
               try:
                   rutafile=ruta+'/'+oaci+'_'+str(fyear)+'-'+str(fmonth)+'-'+str(fday)+'_raw.txt'
                   raw=io.open(rutafile,'w', encoding="utf-8")
                   raw.write(r.text.encode('utf-8'))
               except:
                   print(oaci,window_min,'raw no escrito')
               #Une metares con saltos
               a=r.text 
               f_temp=a.replace('\n  ','')              
               Decode_metar_3DVAR(rutafile,f_temp)
           else:
               print("NO hay METAR", oaci)
               print(r.text)
        else:
             print("No hay METAR en Ogimet:", r.status_code)
        #3minutos 
        sleep(185)

    return None

def metar2little_r(METARdir, Destdir, ifecha,window_min,window_max,coos):
    '''
    Input: METARdir = directorio de ubicacion de archivos METAR decodificados
           Destdir = directorio de destino para archivo little_r_obs_3dvar
           ifecha = datetime con la fecha de inicio de la corrida en UTC
           coos = diccionario con informacion de los aeropuertos que se desean asimilar
                  nota: el diccionario coos debe contener la altura entre sus datos

    Output: archivo little_r_obs_3dvar en el directorio Destdir
    '''
    
    from datetime import datetime

    print('metar2little_r',METARdir, Destdir, ifecha)

    little_r=open(Destdir+'/'+'little_r_obs_3dvar','w')
    # downmetar descraga archivos mensuales
    fecha_archivo=ifecha.strftime("%Y-%m")

    #Generar vacios
    Er=-777777
    empty=-888888

    #Ciclo sobre aeropuertos
    for apto in coos.keys():
        #Extraer variables para el Header
        Lat=float(coos[apto][0]) #Extraer latitud
        Lon=float(coos[apto][1]) #Extraer longitud
        ID='ICAO '+apto
        ID=ID.ljust(40) #justificar a izquierda 
        Name='Aeropuerto de '+coos[apto][2]
        Name=Name.ljust(40) #justificar a izquierda
	Platform=str('FM-15 METAR')
        Platform=Platform.ljust(40) #justificar a izquierda
        Source=str('proveniente de metar.py')
        Source=Source.ljust(40) #justificar a izquierda
        Elevation=float(coos[apto][3]) #Extraer altura
        ValidFields=int(11)

#   abrir archivo de METAR del aeropuerto apto 
        loc=METARdir+'/'+apto+'_'+fecha_archivo+'.csv'
	print(loc)
	try:
            a=open(loc,'r')
            data_METAR=a.readlines()

	    for x in range(0,len(data_METAR)):
             
              linea=data_METAR[x].rstrip('\n')
              linea=linea.split(';')
              sfecha=linea[0]+'0000' #Cambiar si se tiene la fecha con minutos y segundos
              fecha=datetime.strptime(sfecha,"%Y%m%d%H0000") 
              if fecha > window_min and fecha< window_max:
                 SeaLevelPressure=float(linea[2]) #Pa 
                 magnitudViento=float(linea[1]) #m/s
                 PuntoDeRocio=float(linea[3])+273.15 #K
                 Temperatura=float(linea[5])+273.15 #K             

#    Varibles en el Header
#    Latitud, Longitud, ID, Name, Platform, Source, Elevation, 
#    ValidFields, Intempty, Intempty, seq_num?, Intempty, is_sound, bogus, discard
#    #sut, #julian, date_char, SeaLevelPressure qc, #emptydata+qcflag * 12
    
                 Header = ff.FortranRecordWriter('(F20.5, F20.5, A40, A40, A40, A40, F20.5, I10, I10, I10, I10, I10, L10, L10, L10, I10, I10, A20, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7)')
                 PrintHeader = Header.write([Lat,Lon,ID,Name,Platform,Source,Elevation,ValidFields,empty,empty,int(x),empty,0,0,0,empty,empty,sfecha,SeaLevelPressure,0,empty,0,empty,0,empty,0,empty,0,empty,0,empty,0,empty,0,empty,0,empty,0,empty,0,empty,0,empty,0])
                 little_r.writelines(PrintHeader+'\n')

#   Variables en la linea de datos    
#    Presion [Pa], altura [m], temperatura [K], pto de rocio [K], magnitud Viento [m/s], direccion Viento [grados], 4*empty

                 Data = ff.FortranRecordWriter('(F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7)')
                 PrintData = Data.write([empty, 0, Elevation, 0, Temperatura, 0, PuntoDeRocio, 0, magnitudViento, 0, empty, 0, empty, 0, empty, 0, empty, 0, empty, 0])
                 little_r.writelines(PrintData+'\n')

# Imprimir final de datos
                 EndData = ff.FortranRecordWriter('(F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7, F13.5, I7)')
                 PrintEndData = EndData.write([Er, 0, Er, 0, 1.00000, 0, empty, 0, empty, 0, empty, 0, empty, 0, empty, 0, empty, 0, empty, 0])
                 little_r.writelines(PrintEndData+'\n')
             
# Imprimir final de reporte                
                 EndReport = ff.FortranRecordWriter('(I7, I7, I7)')
                 PrintEndReport = EndReport.write([ValidFields, 0, 0])
    	         little_r.writelines(PrintEndReport+'\n')
		 print 'escribio',Destdir+'/'+'little_r_obs_3dvar'
	except:
	    print "NO existe", loc 
	    continue

    little_r.close()
    return None


def main():
    p = parse_params()

    coos=aptos(p.aptos_file)

    downmetar_3DVAR(p.metar_dir,p.window_min,p.window_max,coos)
    print 'metar2little_r', p.metar_dir, p.obsproc_dir, p.start_date, coos
    metar2little_r(p.metar_dir, p.obsproc_dir, p.start_date,p.window_min,p.window_max, coos)


if __name__ == "__main__":
    main()
