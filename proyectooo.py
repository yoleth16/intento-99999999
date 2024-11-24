# -*- coding: utf-8 -*-
"""proyectooo

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1x8I5A5qEpHrWR2X3V-wZcvA3JnIOHvcP
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from Bio import SeqIO
from Bio.SeqUtils import GC
from Bio import pairwise2
from Bio.pairwise2 import format_alignment

st.set_page_config(page_title="Análisis de Secuencias con Biopython", layout="wide")
st.title("🔬 Análisis de Secuencias con Biopython")
st.markdown("""
Este dashboard permite analizar y visualizar datos relacionados con secuencias biológicas.
Carga un archivo y utiliza las herramientas disponibles para explorar tus datos.
""")

def process_fasta(file):
    try:
        sequences = list(SeqIO.parse(file, "fasta"))
        if not sequences:
            st.sidebar.error("El archivo FASTA no contiene secuencias válidas.")
            return None
        return sequences
    except Exception as e:
        st.sidebar.error(f"Error al procesar el archivo FASTA: {str(e)}")
        return None

def process_csv(file):
    try:
        data = pd.read_csv(file)
        return data
    except Exception as e:
        st.sidebar.error(f"Error al procesar el archivo CSV: {str(e)}")
        return None

def calculate_gc_content(sequences):
    return [GC(record.seq) for record in sequences]

def find_motifs(sequences, motifs):
    motif_counts = {motif: 0 for motif in motifs}
    for record in sequences:
        seq = str(record.seq).upper()
        for motif in motifs:
            motif_counts[motif] += seq.count(motif)
    return motif_counts

st.sidebar.title("📂 Carga de Datos")
uploaded_file = st.sidebar.file_uploader("Sube un archivo FASTA o CSV", type=["fasta", "csv"])

data = None
sequences = None

if uploaded_file:
    if uploaded_file.name.endswith(".fasta"):
        sequences = process_fasta(uploaded_file)
        if sequences:
            st.sidebar.success(f"Archivo FASTA cargado: {len(sequences)} secuencias.")
    elif uploaded_file.name.endswith(".csv"):
        data = process_csv(uploaded_file)
        if data is not None:
            st.sidebar.success(f"Archivo CSV cargado con {data.shape[0]} filas.")

if sequences:
    st.header("Análisis de Secuencias FASTA")
    st.write(f"### Número de secuencias cargadas: {len(sequences)}")
    st.text("Ejemplo de secuencia:")
    st.code(f"> {sequences[0].id}\n{str(sequences[0].seq)}")

    gc_contents = calculate_gc_content(sequences)
    st.subheader("Distribución del Contenido GC")
    fig_gc = px.histogram(gc_contents, nbins=20, labels={'value': "Contenido GC (%)", 'count': "Frecuencia"},
                          title="Distribución de Contenido GC", color_discrete_sequence=['blue'])
    st.plotly_chart(fig_gc)

    st.subheader("Búsqueda de Motivos")
    user_motifs = st.text_input("Introduce los motivos separados por comas (ej. ATG, TATA, CCGG):", value="ATG, TATA, CCGG")
    if user_motifs:
        motifs = [motif.strip().upper() for motif in user_motifs.split(",")]
        motif_counts = find_motifs(sequences, motifs)
        st.write("### Frecuencia de Motivos Encontrados")
        st.table(pd.DataFrame(list(motif_counts.items()), columns=["Motivo", "Frecuencia"]))

if data is not None:
    st.header("Análisis de Datos CSV")
    st.write("### Vista Previa de los Datos")
    st.dataframe(data)
    st.write("### Estadísticas Descriptivas")
    st.dataframe(data.describe())

st.header("Herramientas Interactivas")
selected_tool = st.radio("Elige una herramienta:", ["Alineación de Secuencias", "Predicción de Estructuras", "Análisis Estadístico"])


if selected_tool == "Alineación de Secuencias":
    st.subheader("Alineación de Secuencia")
    if sequences and len(sequences) >= 2:
        st.text("Ejemplo: Algoritmo de alineación (Needleman-Wunsch)")

        alignments = pairwise2.align.globalxx(sequences[0].seq, sequences[1].seq)
        alignment_text = format_alignment(*alignments[0])
        st.code(alignment_text, language="text")
    else:
        st.warning("Sube un archivo FASTA con al menos dos secuencias para realizar la alineación.")

elif selected_tool == "Predicción de Estructuras":
    st.subheader("Predicción de Estructuras")
    st.text("Visualización de estructura 3D simulada (Placeholder).")

    import numpy as np
    df_atom = pd.DataFrame({
        "x_coord": np.random.uniform(-10, 10, 100),
        "y_coord": np.random.uniform(-10, 10, 100),
        "z_coord": np.random.uniform(-10, 10, 100),
        "residue_name": np.random.choice(["ALA", "GLY", "SER", "THR"], 100)
    })

    fig = px.scatter_3d(df_atom, x="x_coord", y="y_coord", z="z_coord",
                        color="residue_name", template="plotly_white",
                        title="Estructura 3D Simulada")
    fig.update_traces(marker=dict(size=5))
    fig.update_layout(scene=dict(aspectmode="cube"))
    st.plotly_chart(fig)

elif selected_tool == "Análisis Estadístico":
    st.subheader("Análisis Estadístico")
    if sequences:
        st.text("Análisis basado en las secuencias cargadas.")

        sequence_lengths = [len(record.seq) for record in sequences]
        fig = px.histogram(sequence_lengths, nbins=10, labels={'value': "Longitud de Secuencia", 'count': "Frecuencia"},
                           title="Distribución de Longitudes de Secuencias", color_discrete_sequence=['green'])
        st.plotly_chart(fig)
    elif data is not None:
        st.text("Análisis basado en datos tabulares cargados.")

        numeric_columns = data.select_dtypes(include='number').columns
        if len(numeric_columns) >= 2:
            fig = px.scatter(data, x=numeric_columns[0], y=numeric_columns[1],
                             title=f"Gráfico de Dispersión: {numeric_columns[0]} vs {numeric_columns[1]}",
                             template="plotly_white")
            st.plotly_chart(fig)
        else:
            st.warning("El archivo CSV debe contener al menos dos columnas numéricas.")


if data is not None:
    st.sidebar.markdown("---")
    st.sidebar.write("📥 Descarga de Resultados")
    csv = data.to_csv(index=False)
    st.sidebar.download_button("Descargar resultados CSV", data=csv, file_name="resultados.csv", mime="text/csv")

st.sidebar.markdown("---")
st.sidebar.write("💻 Desarrollado por [Yoleth Barrios y Lucero Ramos]")