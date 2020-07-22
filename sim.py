import streamlit as st
from sim2 import generate_df
import pandas as pd
import numpy as np
import random
pd.set_option("display.max_rows", None, "display.max_columns", None)
import warnings
warnings.filterwarnings('ignore')

@st.cache
def gen_df(cant_iteraciones):
    return generate_df(cant_iteraciones)

st.header('Examen SIMULACION')

cant_it = st.text_input("Cantidad iteraciones", 10)
df = gen_df(int(cant_it))


mostrar_desde = int(st.text_input("Mostrar desde", 0))
mostrar_hasta = int(st.text_input("Mostrar hasta", 10))

if mostrar_desde>df.shape[0] or mostrar_hasta>df.shape[0]:
    mostrar_desde, mostrar_hasta = 0, df.shape[0]
st.write(df.loc[mostrar_desde:mostrar_hasta])

ac_t1 = list(df['ac_t_ocioso1'])[-1]
ac_t2 = list(df['ac_t_ocioso2'])[-1]
t_max_e = list(df['max_tiempo_espera'])[-1]

st.write('Acumulador tiempo ocioso 1 ', ac_t1)
st.write('Acumulador tiempo ocioso 2 ',ac_t2)
st.write('Tiempo maximo de espera ', t_max_e)

