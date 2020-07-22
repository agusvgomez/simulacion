import pandas as pd
import numpy as np
import random
pd.set_option("display.max_rows", None, "display.max_columns", None)
import warnings
warnings.filterwarnings('ignore')

def get_random_unif(a, b):
    if a==0 and b==1:
        a, b = 0.000001, 0.999999
    return round(random.uniform(a, b), 2)

def get_exp_neg(media, rnd):
    return round(-media*np.log(1-rnd), 2)

def get_norm(tipo_pieza):
    if tipo_pieza==1:
        media, desv = 150, 2
    elif tipo_pieza==2:
        media, desv = 80, 3
    elif tipo_pieza==3:
        media, desv = 82, 1
    return round(np.random.normal(loc=media, scale=desv))

def get_tipo(rnd):
    if rnd<=0.23:
        return 1
    if rnd<=0.6:
        return 2
    return 3

#para obtener tiempo desde el que esta libre un torno
def obtener_ult_libre(df, nro_torno):
    tiempo = 0
    if nro_torno==1:
        df = df.loc[:, :'estado_TORNO1']
    else:
        df = df.loc[:, :'estado_TORNO2']
    for idx, row in df[::-1].iterrows():
        if row[-1]=='Libre':
            return float(row['reloj']) 

#buscar de abajo hacia arriba y de der a izq
def buscar_pieza_en_estado(estado, df):
    try:
        df = df.loc[:,'estado_pieza1':]
        cant_piezas = int(df.shape[1] / 3)
        for i in reversed(range(1, cant_piezas+1)):
            ult_estado_i = list(df['estado_pieza'+str(i)])[-1]
            if ult_estado_i == estado:
                return i
        return -1
    except:
        #print(df)
        raise

#encuentra pieza con menor indice cuyo estado actual sea en cola
def buscar_pieza_menor_estado(estado, df):
    try:
        df = df.loc[:,'estado_pieza1':]
        cant_piezas = int(df.shape[1] / 3)
        piezas_enc = []
        for i in range(1, cant_piezas+1):
            ult_estado_i = list(df['estado_pieza'+str(i)])[-1]
            if ult_estado_i == estado:
                piezas_enc.append(i)
        if len(piezas_enc)>0:
            return min(piezas_enc)
        return -1
    except:
        #print(df)
        raise

def calcular_vaciado(t0, d0, tipo_pieza, nro_torno, h=1):
    #unidad de tiempo = h = 1 = 2min
    if nro_torno==1:
        dD_dt = 0.4 * tipo_pieza
    elif nro_torno==2:
        dD_dt = 5 / tipo_pieza
    
    df = pd.DataFrame([[np.nan, np.nan, np.nan, t0, d0]],columns=['t','D','dD/dt', 't(i+1)', 'D(i+1)'])
    full = False
    i=1
    
    while full!=True:
        this_t = df.iloc[i-1]['t(i+1)']
        this_d = df.iloc[i-1]['D(i+1)']
        next_t = this_t + h
        next_d = this_d + h * dD_dt
        df.loc[i] = [this_t, this_d, dD_dt, next_t, next_d]
        if this_d>=20:
            full = True
        i+=1
    return df

def generate_df(cant_iteraciones):
    #COLUMNAS
    cols = ['evento','reloj','RND_ll','tiempo_entre_llegadas', 'prox_llegada', 
            'RND_tp', 'tipo_pieza', 'COLA',  'cant_piezas_AL1', 'ult_pieza_AL1', 
            'cant_piezas_AL2', 'ult_pieza_AL2', 'RND_mz', 't_mecanizado', 'fin_mecanizado1', 
            'fin_mecanizado2', 'recipiente1', 'descarga_desperdicio1', 'recipiente2', 'descarga_desperdicio2', 
            'fin_reprogramacion1', 'fin_reprogramacion2', 'tipo_p_ant_1', 'estado_TORNO1', 'ac_t_ocioso1',
            'tipo_p_ant_2', 'estado_TORNO2', 'ac_t_ocioso2', 'max_tiempo_espera'] #'estado_PIEZA1', 't_llegada1']
    df = pd.DataFrame(columns=cols, index=list(range(cant_iteraciones+1)))

    reloj_ini = 0
    rnd_primera_llegada = get_random_unif(0,1)
    t_llegada = get_exp_neg(200, rnd_primera_llegada)
    prox_llegada = reloj_ini + t_llegada
    rnd_tipo_pieza = get_random_unif(0,1)
    tipo_pieza = get_tipo(rnd_tipo_pieza)


    df.loc[0] = ['Inicializacion', reloj_ini, rnd_primera_llegada, t_llegada, prox_llegada, 
                rnd_tipo_pieza, tipo_pieza, 0, 0, np.nan, 
                0, np.nan, np.nan, np.nan, np.nan, 
                np.nan, 0, np.nan, 0, np.nan, 
                np.nan, np.nan, np.nan, 'Libre', 0, 
                np.nan, 'Libre', 0, 0]


    eventos_posibles = ['Llegada pieza','Fin mecanizado1', 'Fin mecanizado2', 'Descarga desperdicio1', 
                    'Descarga desperdicio2', 'Fin reprogramacion1', 'Fin reprogramacion2']

    cont_piezas = 0
    for i in range(1,cant_iteraciones+1):
        #print('ITERACION ',i)
        ant_cant_pieza_alimentador1 = df.loc[i-1]['cant_piezas_AL1']
        ant_ult_pieza_alimentador1 = df.loc[i-1]['ult_pieza_AL1']
        ant_cant_pieza_alimentador2 = df.loc[i-1]['cant_piezas_AL2']
        ant_ult_pieza_alimentador2 = df.loc[i-1]['ult_pieza_AL2']
        
        ant_estado_torno1 = df.loc[i-1]['estado_TORNO1']
        ant_ult_pieza_torno1 = df.loc[i-1]['tipo_p_ant_1']
        ant_estado_torno2 = df.loc[i-1]['estado_TORNO2']
        ant_ult_pieza_torno2 = df.loc[i-1]['tipo_p_ant_2']
        
        ant_recipiente1 = df.loc[i-1]['recipiente1']
        ant_recipiente2 = df.loc[i-1]['recipiente2']
        
        ant_ac_t_ocioso1 = df.loc[i-1]['ac_t_ocioso1']
        ant_ac_t_ocioso2 = df.loc[i-1]['ac_t_ocioso2']
        ant_max_tiempo_espera = df.iloc[i-1]['max_tiempo_espera']
        
        tipo_pieza_ant = df.loc[i-1]['tipo_pieza']
        
        ant_prox_llegada = df.loc[i-1]['prox_llegada']
        e_ant_prox_llegada = ant_prox_llegada if not pd.isna(ant_prox_llegada) else 10000000000000
        ant_fin_mecanizado1 = df.loc[i-1]['fin_mecanizado1']
        e_ant_fin_mecanizado1 = ant_fin_mecanizado1 if not pd.isna(ant_fin_mecanizado1) else 10000000000000
        ant_fin_mecanizado2 = df.loc[i-1]['fin_mecanizado2']
        e_ant_fin_mecanizado2 = ant_fin_mecanizado2 if not pd.isna(ant_fin_mecanizado2) else 10000000000000
        ant_descarga_desperdicio1 = df.loc[i-1]['descarga_desperdicio1']
        e_ant_descarga_desperdicio1 = ant_descarga_desperdicio1 if not pd.isna(ant_descarga_desperdicio1) else 10000000000000
        ant_descarga_desperdicio2 = df.loc[i-1]['descarga_desperdicio2']
        e_ant_descarga_desperdicio2 = ant_descarga_desperdicio2 if not pd.isna(ant_descarga_desperdicio2) else 10000000000000
        ant_fin_reprogramacion1 = df.loc[i-1]['fin_reprogramacion1']
        e_ant_fin_reprogramacion1 = ant_fin_reprogramacion1 if not pd.isna(ant_fin_reprogramacion1) else 10000000000000
        ant_fin_reprogramacion2 = df.loc[i-1]['fin_reprogramacion2']
        e_ant_fin_reprogramacion2 = ant_fin_reprogramacion2 if not pd.isna(ant_fin_reprogramacion2) else 10000000000000
        
        eventos = [e_ant_prox_llegada, e_ant_fin_mecanizado1, e_ant_fin_mecanizado2, e_ant_descarga_desperdicio1,
                e_ant_descarga_desperdicio2, e_ant_fin_reprogramacion1, e_ant_fin_reprogramacion2]
        prox_evento = eventos_posibles[np.argmin(eventos)]
        
        
        #asignar todas las var ant a THIS
        THIS_reloj = df.loc[i-1]['reloj']
        THIS_prox_llegada = ant_prox_llegada
        THIS_cola = df.loc[i-1]['COLA']
        THIS_cant_piezas_AL1 = ant_cant_pieza_alimentador1
        THIS_ult_pieza_alimentador1 = ant_ult_pieza_alimentador1
        THIS_cant_piezas_AL2 = ant_cant_pieza_alimentador2
        THIS_ult_pieza_alimentador2 = ant_ult_pieza_alimentador2
        THIS_fin_reprogramacion1 = ant_fin_reprogramacion1
        THIS_fin_reprogramacion2 = ant_fin_reprogramacion2
        THIS_estado_torno1 = ant_estado_torno1
        THIS_estado_torno2 = ant_estado_torno2
        THIS_fin_mecanizado1 = ant_fin_mecanizado1
        THIS_ult_pieza_torno1 = ant_ult_pieza_torno1
        THIS_fin_mecanizado2 = ant_fin_mecanizado2
        THIS_ult_pieza_torno2 = ant_ult_pieza_torno2
        THIS_descarga_desperdicio1 = ant_descarga_desperdicio1
        THIS_recipiente1 = ant_recipiente1
        THIS_descarga_desperdicio2 = ant_descarga_desperdicio2
        THIS_recipiente2 = ant_recipiente2
        THIS_ac_t_ocioso1 = ant_ac_t_ocioso1
        THIS_ac_t_ocioso2 = ant_ac_t_ocioso2
        THIS_max_tiempo_espera = ant_max_tiempo_espera
        THIS_tipo_pieza = tipo_pieza_ant
        
        #caso en el que 
        if cont_piezas>0:
            for j in range(1, cont_piezas+1):   #estado_pieza1	llegada_pieza1	tipo_pieza1
                df['estado_pieza'+str(j)][i] = df['estado_pieza'+str(j)][i-1]
                df['llegada_pieza'+str(j)][i] = df['llegada_pieza'+str(j)][i-1]
                df['tipo_pieza'+str(j)][i] = df['tipo_pieza'+str(j)][i-1]
                
        df['fin_mecanizado1'][i] = ant_fin_mecanizado1
        df['fin_mecanizado2'][i] = ant_fin_mecanizado2
        
        #print('evento', prox_evento)
        if prox_evento=='Llegada pieza':
            THIS_reloj = df.loc[i-1]['prox_llegada']
            
            #genero proxima llegada
            THIS_rnd_prox_llegada = get_random_unif(0,1)
            df['RND_ll'][i] = THIS_rnd_prox_llegada
            THIS_t_llegada = get_exp_neg(200, THIS_rnd_prox_llegada)
            df['tiempo_entre_llegadas'][i] = THIS_t_llegada
            THIS_prox_llegada = THIS_reloj + THIS_t_llegada
            THIS_rnd_tipo_pieza = get_random_unif(0,1)
            df['RND_tp'][i] = THIS_rnd_tipo_pieza
            THIS_tipo_pieza = get_tipo(THIS_rnd_tipo_pieza)
            df['tipo_pieza'][i] = THIS_tipo_pieza
            
            #creo la pieza
            cont_piezas +=1
            df['estado_pieza'+str(cont_piezas)] = np.nan
            df['llegada_pieza'+str(cont_piezas)] = np.nan
            df['tipo_pieza'+str(cont_piezas)] = np.nan
            
            df['tipo_pieza'+str(cont_piezas)][i:] = tipo_pieza_ant
            df['llegada_pieza'+str(cont_piezas)][i:] = THIS_reloj
            
            if ant_cant_pieza_alimentador1<3 and (ant_ult_pieza_alimentador2!=tipo_pieza_ant or ant_cant_pieza_alimentador2>=3):
                #road to torno1
                THIS_ult_pieza_alimentador1 = tipo_pieza_ant #registro tipo pieza en el alimentdor
                if ant_estado_torno1=='Libre':
                    if ant_ult_pieza_torno1!= tipo_pieza_ant:
                        THIS_fin_reprogramacion1 = THIS_reloj + 2 #si la pieza anterior no era del mismo tipo, reprogramo
                        THIS_estado_torno1 = 'Reprogramando'
                        df['estado_pieza'+str(cont_piezas)][i] = 'En Alimentador (1)'
                        THIS_cant_piezas_AL1 +=1
                    else:                     #PASA DIRECTO
                        #cambio estados
                        THIS_estado_torno1 = 'Ocupado'
                        df['estado_pieza'+str(cont_piezas)][i] = 'Siendo Maquinada (1)'
                        
                        #calculo fin mecanizado
                        THIS_rnd_mz = get_random_unif(0,1)
                        df['RND_mz'][i] = THIS_rnd_mz
                        THIS_t_mecanizado = get_norm(tipo_pieza_ant)
                        df['t_mecanizado'][i] = THIS_t_mecanizado
                        THIS_fin_mecanizado1 = THIS_reloj + THIS_t_mecanizado
                        df['fin_mecanizado1'][i] = THIS_fin_mecanizado1

                        #registro tipo pieza en el torno y acumulo tiempo ocioso
                        THIS_ult_pieza_torno1 = tipo_pieza_ant
                        THIS_ac_t_ocioso1 = ant_ac_t_ocioso1 + (THIS_reloj - obtener_ult_libre(df.loc[:i-1], 1))

                        #calculo vaciado
                        dif_df = calcular_vaciado(THIS_reloj/120, ant_recipiente1, tipo_pieza_ant, 1)
                        #print('Fin mecanizado ',THIS_fin_mecanizado1/120)
                        #print('Simulo dif')
                        #print(dif_df)
                        t_llenado = list(dif_df['t'])[-1]*120
                        if t_llenado <= THIS_fin_mecanizado1:
                            THIS_descarga_desperdicio1 = t_llenado
                            THIS_recipiente1 = 20
                        elif t_llenado > THIS_fin_mecanizado1:
                            THIS_descarga_desperdicio1 = np.nan
                            THIS_recipiente1 = list(dif_df[dif_df.t<=(THIS_fin_mecanizado1/120)]['D'])[-1]
                else:
                    THIS_cant_piezas_AL1 +=1      
                    df['estado_pieza'+str(cont_piezas)][i] = 'En Alimentador (1)'
            
            elif ant_cant_pieza_alimentador2<3:  
                #road to torno2
                THIS_ult_pieza_alimentador2 = tipo_pieza_ant #registro tipo pieza en el alimentdor
                if ant_estado_torno2=='Libre':
                    if ant_ult_pieza_torno2!= tipo_pieza_ant:
                        THIS_fin_reprogramacion2 = THIS_reloj + 2 #si la pieza anterior no era del mismo tipo, reprogramo
                        THIS_estado_torno2 = 'Reprogramando'
                        df['estado_pieza'+str(cont_piezas)][i] = 'En Alimentador (2)'
                        THIS_cant_piezas_AL2 +=1
                    else:                     #PASA DIRECTO
                        #cambio estados
                        THIS_estado_torno2 = 'Ocupado'
                        df['estado_pieza'+str(cont_piezas)][i] = 'Siendo Maquinada (2)'
                        
                        #calculo fin mecanizado
                        THIS_rnd_mz = get_random_unif(0,1)
                        df['RND_mz'][i] = THIS_rnd_mz
                        THIS_t_mecanizado = get_norm(tipo_pieza_ant)
                        df['t_mecanizado'][i] = THIS_t_mecanizado
                        THIS_fin_mecanizado2 = THIS_reloj + THIS_t_mecanizado
                        df['fin_mecanizado2'][i] = THIS_fin_mecanizado2

                        #registro tipo pieza en el torno y acumulo tiempo ocioso
                        THIS_ult_pieza_torno2 = tipo_pieza_ant
                        THIS_ac_t_ocioso2 = ant_ac_t_ocioso2 + (THIS_reloj - obtener_ult_libre(df.loc[:i-1], 2))

                        #calculo vaciado
                        dif_df = calcular_vaciado(THIS_reloj/120, ant_recipiente2, tipo_pieza_ant, 2)
                        #print('Fin mecanizado ',THIS_fin_mecanizado2/120)
                        #print('Simulo dif')
                        #print(dif_df)
                        t_llenado = list(dif_df['t'])[-1]*120
                        if t_llenado <= THIS_fin_mecanizado2:
                            THIS_descarga_desperdicio2 = t_llenado
                            THIS_recipiente2 = 20
                        if t_llenado > THIS_fin_mecanizado2:
                            THIS_descarga_desperdicio2 = np.nan
                            THIS_recipiente2 = list(dif_df[dif_df.t<=(THIS_fin_mecanizado2/120)]['D'])[-1]
                else:
                    THIS_cant_piezas_AL2 +=1      
                    df['estado_pieza'+str(cont_piezas)][i] = 'En Alimentador (2)'
                        
            else:
                #incremento la cola
                THIS_cola +=1
                df['estado_pieza'+str(cont_piezas)][i] = 'En Cola'
                
        elif prox_evento=='Fin reprogramacion1':
            THIS_reloj = df.loc[i-1]['fin_reprogramacion1']
            THIS_fin_reprogramacion1 = np.nan
            
            #quito pieza de alimentador
            THIS_cant_piezas_AL1 -=1
            
            #cambio estados
            THIS_estado_torno1 = 'Ocupado'
            pieza_i = buscar_pieza_menor_estado('En Alimentador (1)', df[:i])
            df['estado_pieza'+str(pieza_i)][i] = 'Siendo Maquinada (1)'
            
            #busco tipo de pieza
            tipo_pieza = df.loc[i-1]['tipo_pieza'+str(pieza_i)]
            
            #registro espera de la pieza
            tiempo_espera = THIS_reloj - df.loc[i]['llegada_pieza'+str(pieza_i)]
            if tiempo_espera>df.loc[i-1]['max_tiempo_espera']:
                THIS_max_tiempo_espera = tiempo_espera
                
            #calculo fin mecanizado
            THIS_rnd_mz = get_random_unif(0,1)
            df['RND_mz'][i] = THIS_rnd_mz
            THIS_t_mecanizado = get_norm(tipo_pieza_ant)
            df['t_mecanizado'][i] = THIS_t_mecanizado
            THIS_fin_mecanizado1 = THIS_reloj + THIS_t_mecanizado
            df['fin_mecanizado1'][i] = THIS_fin_mecanizado1

            #registro tipo pieza en el torno y acumulo tiempo ocioso
            THIS_ult_pieza_torno1 = tipo_pieza
            if len(df[:i-1]['estado_TORNO1'].unique())==1:
                THIS_ac_t_ocioso1 = THIS_reloj
            else:
                THIS_ac_t_ocioso1 = ant_ac_t_ocioso1 + (THIS_reloj - obtener_ult_libre(df.loc[:i-1], 1))

            #calculo vaciado
            dif_df = calcular_vaciado(THIS_reloj/120, ant_recipiente1, tipo_pieza, 1)
            t_llenado = list(dif_df['t'])[-1]*120
            #print('Fin mecanizado ',THIS_fin_mecanizado1/120)
            #print('Simulo dif')
            #print(dif_df)
            if t_llenado <= THIS_fin_mecanizado1:
                THIS_descarga_desperdicio1 = t_llenado
                THIS_recipiente1 = 20
            if t_llenado > THIS_fin_mecanizado1:
                THIS_descarga_desperdicio1 = np.nan
                THIS_recipiente1 = list(dif_df[dif_df['t']<=(THIS_fin_mecanizado1/120)]['D'])[-1]
        
        elif prox_evento=='Fin reprogramacion2':
            THIS_reloj = df.loc[i-1]['fin_reprogramacion2']
            THIS_fin_reprogramacion2 = np.nan
            
            #quito pieza de alimentador
            THIS_cant_piezas_AL2 -=1
            
            #cambio estados
            THIS_estado_torno2 = 'Ocupado'
            pieza_i = buscar_pieza_menor_estado('En Alimentador (2)', df[:i])
            df['estado_pieza'+str(pieza_i)][i] = 'Siendo Maquinada (2)'   
            
            #busco tipo de pieza
            tipo_pieza = df.loc[i-1]['tipo_pieza'+str(pieza_i)]
            
            #registro espera de la pieza
            tiempo_espera = THIS_reloj - df.loc[i]['llegada_pieza'+str(pieza_i)]
            if tiempo_espera>df.loc[i-1]['max_tiempo_espera']:
                THIS_max_tiempo_espera = tiempo_espera

            #calculo fin mecanizado
            THIS_rnd_mz = get_random_unif(0,1)
            df['RND_mz'][i] = THIS_rnd_mz
            THIS_t_mecanizado = get_norm(tipo_pieza_ant)
            df['t_mecanizado'][i] = THIS_t_mecanizado
            THIS_fin_mecanizado2 = THIS_reloj + THIS_t_mecanizado
            df['fin_mecanizado2'][i] = THIS_fin_mecanizado2

            #registro tipo pieza en el torno y acumulo tiempo ocioso
            THIS_ult_pieza_torno2 = tipo_pieza
            if len(df[:i-1]['estado_TORNO2'].unique())==1:
                THIS_ac_t_ocioso2 = THIS_reloj
            else:
                THIS_ac_t_ocioso2 = ant_ac_t_ocioso2 + (THIS_reloj - obtener_ult_libre(df.loc[:i-1], ))

            #calculo vaciado
            dif_df = calcular_vaciado(THIS_reloj/120, ant_recipiente2, tipo_pieza, 2)
            #print('Fin mecanizado ',THIS_fin_mecanizado2/120)
            #print('Simulo dif')
            #print(dif_df)
            t_llenado = list(dif_df['t'])[-1]*120
            if t_llenado <= THIS_fin_mecanizado2:
                THIS_descarga_desperdicio2 = t_llenado
                THIS_recipiente2 = 20
            if t_llenado > THIS_fin_mecanizado2:
                THIS_descarga_desperdicio2 = np.nan
                THIS_recipiente2 = list(dif_df[dif_df.t<=(THIS_fin_mecanizado2/120)]['D'])[-1]
                
        elif prox_evento=='Descarga desperdicio1':
            THIS_reloj = df.loc[i-1]['descarga_desperdicio1']
            #seteo a cero las cols de desperdicio
            THIS_descarga_desperdicio1 = np.nan
            THIS_recipiente1 = 0
            
            #busco pieza y tipo
            if df['reloj'][i-1]==THIS_reloj and df['evento'][i-1]=='Fin mecanizado1':
                #ya se fue del sist
                #pieza_i = buscar_pieza_en_estado('Siendo Maquinada (2)', df[:i-1])
                pass
            else:
                pieza_i = buscar_pieza_en_estado('Siendo Maquinada (1)', df[:i])
                tipo_pieza = df.loc[i]['tipo_pieza'+str(pieza_i)]

                #cambio estados
                THIS_estado_torno1 = 'Descargando'
                #df['estado_pieza'+str(pieza_i)][i] = 'Esperando Maquina (1)'

                #actualizo tiempos
                THIS_fin_mecanizado1 = THIS_fin_mecanizado1+45
                df['fin_mecanizado1'][i] = THIS_fin_mecanizado1


                #calculo vaciado nuevamente
                dif_df = calcular_vaciado(THIS_reloj/120, THIS_recipiente1, tipo_pieza, 1)
                t_llenado = list(dif_df['t'])[-1]*120
                #print('Fin mecanizado ',THIS_fin_mecanizado1/120)
                #print('Simulo dif')
                #print(dif_df)
                if t_llenado <= THIS_fin_mecanizado1:
                    THIS_descarga_desperdicio1 = t_llenado
                    THIS_recipiente1 = 20
                if t_llenado > THIS_fin_mecanizado1:
                    THIS_descarga_desperdicio1 = np.nan
                    THIS_recipiente1 = list(dif_df[dif_df.t<=(THIS_fin_mecanizado1/120)]['D'])[-1]
                
        elif prox_evento=='Descarga desperdicio2':
            THIS_reloj = df.loc[i-1]['descarga_desperdicio2']
            
            #seteo a cero las cols de desperdicio
            THIS_descarga_desperdicio2 = np.nan
            THIS_recipiente2 = 0
            
            #busco pieza y tipo
            if df['reloj'][i-1]==THIS_reloj and df['evento'][i-1]=='Fin mecanizado2':
                #ya se fue del sist
                #pieza_i = buscar_pieza_en_estado('Siendo Maquinada (2)', df[:i-1])
                pass
            else:
                pieza_i = buscar_pieza_en_estado('Siendo Maquinada (2)', df[:i])
                tipo_pieza = df.loc[i]['tipo_pieza'+str(pieza_i)]
            
                #cambio estados
                THIS_estado_torno2 = 'Descargando'
                #df['estado_pieza'+str(pieza_i)][i] = 'Esperando Maquina (2)'

                #actualizo tiempos
                THIS_fin_mecanizado2 = THIS_fin_mecanizado2+45
                df['fin_mecanizado2'][i] = THIS_fin_mecanizado2
            
                #calculo vaciado nuevamente
                dif_df = calcular_vaciado(THIS_reloj/120, THIS_recipiente2, tipo_pieza, 2)
                #print('Fin mecanizado ',THIS_fin_mecanizado2/120)
                #print('Simulo dif')
                #print(dif_df)
                t_llenado = list(dif_df['t'])[-1]*120
                if t_llenado <= THIS_fin_mecanizado2:
                    THIS_descarga_desperdicio2 = t_llenado
                    THIS_recipiente2 = 20
                if t_llenado > THIS_fin_mecanizado2:
                    THIS_descarga_desperdicio2 = np.nan
                    THIS_recipiente2 = list(dif_df[dif_df.t<=(THIS_fin_mecanizado2/120)]['D'])[-1]
            
                
        elif prox_evento=='Fin mecanizado1':
            THIS_reloj = df.loc[i-1]['fin_mecanizado1']
            
            #busco pieza
            pieza_i = buscar_pieza_en_estado('Siendo Maquinada (1)', df[:i])
            df['estado_pieza'+str(pieza_i)][i] = 'Fuera de Sistema'
            df['fin_mecanizado1'][i] = np.nan
            
            #cambio estados
            if THIS_cant_piezas_AL1>0:
                #busco pieza
                pieza_i = buscar_pieza_menor_estado('En Alimentador (1)', df[:i])
                tipo_pieza = df.loc[i]['tipo_pieza'+str(pieza_i)]
                
                if ant_ult_pieza_torno1!= tipo_pieza:
                        THIS_fin_reprogramacion1 = THIS_reloj + 2 #si la pieza anterior no era del mismo tipo, reprogramo
                        THIS_estado_torno1 = 'Reprogramando'
                else:                     #PASA DIRECTO
                    #cambio estados
                    THIS_estado_torno1 = 'Ocupado'
                    df['estado_pieza'+str(pieza_i)][i] = 'Siendo Maquinada (1)'
                    THIS_tipo_p_ant_1 = tipo_pieza

                    #muevo de la cola al alimentador
                    if THIS_cola>0:
                        pieza_en_colai = buscar_pieza_menor_estado('En Cola', df[:i])
                        tipo_pieza_cola = df.loc[i]['tipo_pieza'+str(pieza_i)]
                        df['estado_pieza'+str(pieza_en_colai)][i] = 'En Alimentador (1)'
                        THIS_ult_pieza_alimentador1 = tipo_pieza_cola
                    else: #disminuyo alimentador
                        THIS_cant_piezas_AL1-=1

                    #calculo fin mecanizado
                    THIS_rnd_mz = get_random_unif(0,1)
                    df['RND_mz'][i] = THIS_rnd_mz
                    THIS_t_mecanizado = get_norm(tipo_pieza_ant)
                    df['t_mecanizado'][i] = THIS_t_mecanizado
                    THIS_fin_mecanizado1 = THIS_reloj + THIS_t_mecanizado
                    df['fin_mecanizado1'][i] = THIS_fin_mecanizado1

                    #calculo vaciado
                    dif_df = calcular_vaciado(THIS_reloj/120, ant_recipiente1, tipo_pieza, 1)
                    t_llenado = list(dif_df['t'])[-1]*120
                    #print('Fin mecanizado ',THIS_fin_mecanizado1/120)
                    #print('Simulo dif')
                    #print(dif_df)
                    if t_llenado <= THIS_fin_mecanizado1:
                        THIS_descarga_desperdicio1 = t_llenado
                        THIS_recipiente1 = 20
                    if t_llenado > THIS_fin_mecanizado1:
                        THIS_descarga_desperdicio1 = np.nan
                        THIS_recipiente1 = list(dif_df[dif_df.t<=(THIS_fin_mecanizado1/120)]['D'])[-1]
            else:
                THIS_estado_torno1 = 'Libre'
            
        elif prox_evento=='Fin mecanizado2':
            THIS_reloj = df.loc[i-1]['fin_mecanizado2']
            
            #busco pieza
            pieza_i = buscar_pieza_en_estado('Siendo Maquinada (2)', df[:i])
            df['estado_pieza'+str(pieza_i)][i] = 'Fuera de Sistema'
            df['fin_mecanizado2'][i] = np.nan
            
            #cambio estados
            if THIS_cant_piezas_AL2>0:
                #busco pieza
                pieza_i = buscar_pieza_menor_estado('En Alimentador (2)', df[:i])
                tipo_pieza = df.loc[i]['tipo_pieza'+str(pieza_i)]
                
                if ant_ult_pieza_torno2!= tipo_pieza:
                        THIS_fin_reprogramacion2 = THIS_reloj + 2 #si la pieza anterior no era del mismo tipo, reprogramo
                        THIS_estado_torno2 = 'Reprogramando'
                else:                     #PASA DIRECTO
                    #cambio estados
                    THIS_estado_torno2 = 'Ocupado'
                    df['estado_pieza'+str(pieza_i)][i] = 'Siendo Maquinada (2)'
                    THIS_tipo_p_ant_2 = tipo_pieza

                    #muevo de la cola al alimentador
                    if THIS_cola>0:
                        pieza_en_colai = buscar_pieza_menor_estado('En Cola', df[:i])
                        tipo_pieza_cola = df.loc[i]['tipo_pieza'+str(pieza_i)]
                        df['estado_pieza'+str(pieza_en_colai)][i] = 'En Alimentador (2)'
                        THIS_ult_pieza_alimentador2 = tipo_pieza_cola
                    else: #disminuyo alimentador
                        THIS_cant_piezas_AL2-=1

                    #calculo fin mecanizado
                    THIS_rnd_mz = get_random_unif(0,1)
                    df['RND_mz'][i] = THIS_rnd_mz
                    THIS_t_mecanizado = get_norm(tipo_pieza_ant)
                    df['t_mecanizado'][i] = THIS_t_mecanizado
                    THIS_fin_mecanizado2 = THIS_reloj + THIS_t_mecanizado
                    df['fin_mecanizado2']['i'] = THIS_fin_mecanizado2

                    #calculo vaciado
                    dif_df = calcular_vaciado(THIS_reloj/120, ant_recipiente2, tipo_pieza, 2)
                    t_llenado = list(dif_df['t'])[-1]*120
                    #print('Fin mecanizado ',THIS_fin_mecanizado1/120)
                    #print('Simulo dif')
                    #print(dif_df)
                    if t_llenado <= THIS_fin_mecanizado2:
                        THIS_descarga_desperdicio2 = t_llenado
                        THIS_recipiente2 = 20
                    if t_llenado > THIS_fin_mecanizado2:
                        THIS_descarga_desperdicio2 = np.nan
                        THIS_recipiente2 = list(dif_df[dif_df.t<=(THIS_fin_mecanizado2/120)]['D'])[-1]
            else:
                THIS_estado_torno2 = 'Libre'
                
        
        
        ##ASIGNACIONES
        df['evento'][i] = prox_evento
        df['reloj'][i] = THIS_reloj
        df['prox_llegada'][i] = THIS_prox_llegada
        df['tipo_pieza'][i] = THIS_tipo_pieza
        df['COLA'][i] = THIS_cola
        df['cant_piezas_AL1'][i] = THIS_cant_piezas_AL1
        df['ult_pieza_AL1'][i] = THIS_ult_pieza_alimentador1
        df['cant_piezas_AL2'][i] = THIS_cant_piezas_AL2
        df['ult_pieza_AL2'][i] = THIS_ult_pieza_alimentador2
        #df['fin_mecanizado1'][i] = THIS_fin_mecanizado1
        #df['fin_mecanizado2'][i] = THIS_fin_mecanizado2
        df['recipiente1'][i] = THIS_recipiente1
        df['descarga_desperdicio1'][i] = THIS_descarga_desperdicio1
        df['recipiente2'][i] = THIS_recipiente2
        df['descarga_desperdicio2'][i] = THIS_descarga_desperdicio2
        df['fin_reprogramacion1'][i] = THIS_fin_reprogramacion1
        df['fin_reprogramacion2'][i] = THIS_fin_reprogramacion2
        df['tipo_p_ant_1'][i] = THIS_ult_pieza_torno1
        df['estado_TORNO1'][i] = THIS_estado_torno1
        df['ac_t_ocioso1'][i] = THIS_ac_t_ocioso1
        df['tipo_p_ant_2'][i] = THIS_ult_pieza_torno2
        df['estado_TORNO2'][i] = THIS_estado_torno2
        df['ac_t_ocioso2'][i] = THIS_ac_t_ocioso2
        df['max_tiempo_espera'][i] = THIS_max_tiempo_espera
        
        #print()
        
    if len(df['estado_TORNO1'].unique())==1 and df['estado_TORNO1'].unique()[0]=='Libre':
        df['ac_t_ocioso1'][i] = list(df['reloj'])[-1]  - df.loc[0]['reloj']
    if len(df['estado_TORNO2'].unique())==1 and df['estado_TORNO2'].unique()[0]=='Libre':
        df['ac_t_ocioso2'][i] = list(df['reloj'])[-1]  - df.loc[0]['reloj']
    return df
