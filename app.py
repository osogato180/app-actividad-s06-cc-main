import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import certifi

# -------------------------
# CONFIGURACIÓN
# -------------------------
st.set_page_config(page_title="Banco Regional Andino", layout="wide")

# -------------------------
# CONEXIÓN MONGODB ATLAS
# -------------------------
uri = "mongodb+srv://josebaldeon365_db_user:im3v8WmvvbmghmkV@cluster0.dslhgkt.mongodb.net/"

client = MongoClient(uri, tlsCAFile=certifi.where())

db = client["banco_bra"]
coleccion = db["creditos"]

# -------------------------
# TÍTULO
# -------------------------
st.title("Portal Digital de Créditos - Banco Regional Andino")

# -------------------------
# TABS
# -------------------------
tab1, tab2 = st.tabs(["Cliente Digital", "Panel Bancario"])

# ======================================================
# CLIENTE DIGITAL
# ======================================================
with tab1:

    st.subheader("Solicita tu crédito en línea")

    col1, col2 = st.columns(2)

    with col1:
        nombre = st.text_input("Nombre completo")
        dni = st.text_input("DNI")
        ingreso = st.number_input("Ingreso mensual (S/)", min_value=0)

    with col2:
        antiguedad = st.number_input("Antigüedad laboral (meses)", min_value=0)
        deuda = st.number_input("Deuda actual (S/)", min_value=0)
        monto = st.number_input("Monto solicitado (S/)", min_value=0)

    if st.button("Evaluar solicitud"):

        if nombre and dni and ingreso > 0:

            score = 0
            sugerencias = []

            ratio_deuda = deuda / ingreso
            ratio_monto = monto / ingreso

            # -------------------------
            # INGRESOS
            # -------------------------
            if ingreso >= 3000:
                score += 30
            elif ingreso >= 2000:
                score += 20
            else:
                sugerencias.append("Incrementar ingresos demostrables mejora tu perfil financiero.")

            # -------------------------
            # ANTIGÜEDAD
            # -------------------------
            if antiguedad >= 12:
                score += 25
            elif antiguedad >= 6:
                score += 15
            else:
                sugerencias.append("Mayor estabilidad laboral mejora la evaluación.")

            # -------------------------
            # DEUDA
            # -------------------------
            if ratio_deuda < 0.3:
                score += 25
            elif ratio_deuda < 0.4:
                score += 15
            else:
                sugerencias.append("Reducir tu nivel de deuda actual puede mejorar tu aprobación.")

            # -------------------------
            # MONTO SOLICITADO
            # -------------------------
            if ratio_monto <= 5:
                score += 20
            elif ratio_monto <= 8:
                score += 10
            else:
                sugerencias.append("Solicitar un monto menor mejora la probabilidad de aprobación.")

            # -------------------------
            # DECISIÓN
            # -------------------------
            monto_recomendado = ingreso * 5

            if score >= 80:
                resultado = "Preaprobado"
                mensaje = "Tu crédito fue preaprobado digitalmente."
            elif score >= 50:
                resultado = "En evaluación"
                mensaje = "Tu solicitud requiere validación adicional."
            else:
                resultado = "No aprobado"
                mensaje = "Actualmente no cumples con las condiciones mínimas."

            # -------------------------
            # GUARDAR EN MONGO
            # -------------------------
            datos = {
                "nombre": nombre,
                "dni": dni,
                "ingreso": ingreso,
                "antiguedad": antiguedad,
                "deuda": deuda,
                "monto": monto,
                "score": score,
                "resultado": resultado,
                "fecha": datetime.now()
            }

            coleccion.insert_one(datos)

            # -------------------------
            # RESULTADO CLIENTE
            # -------------------------
            st.success(mensaje)
            st.info(f"Score crediticio: {score}/100")
            st.info(f"Monto sugerido por el sistema: S/ {monto_recomendado}")
            st.metric("Tiempo estimado de respuesta", "2 segundos")

            if sugerencias:
                st.warning("Recomendaciones para mejorar tu perfil:")
                for s in sugerencias:
                    st.write(f"- {s}")

# ======================================================
# PANEL BANCARIO
# ======================================================
with tab2:

    st.subheader("Panel de monitoreo bancario")

    datos_db = list(coleccion.find({}, {"_id": 0}))
    df = pd.DataFrame(datos_db)

    if not df.empty:

        c1, c2, c3 = st.columns(3)

        c1.metric("Solicitudes Totales", len(df))
        c2.metric("Preaprobados", len(df[df["resultado"] == "Preaprobado"]))
        c3.metric("En evaluación", len(df[df["resultado"] == "En evaluación"]))

        st.subheader("Buscar por DNI")

        dni_buscar = st.text_input("Ingrese DNI")

        if dni_buscar:
            filtro = df[df["dni"] == dni_buscar]

            if not filtro.empty:
                st.dataframe(filtro, use_container_width=True)
            else:
                st.write("Cliente no encontrado")

        st.subheader("Historial General")
        st.dataframe(df, use_container_width=True)

        st.subheader("Distribución de solicitudes")
        conteo = df["resultado"].value_counts()
        st.bar_chart(conteo)

    else:
        st.write("No hay solicitudes registradas")