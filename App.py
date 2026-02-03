import streamlit as st
import pandas as pd
from datetime import datetime, date
import io

# --- CONFIGURATION DEI ---
st.set_page_config(page_title="DEI - Supervision SSI", layout="wide")

# Référentiels Matériels (Modifiables)
TYPES_CAPTEURS = ["Optique de fumée", "Thermostatique", "Multi-capteur", "Flamme", "DM", "Sirène"]

# --- INITIALISATION ---
if 'parc' not in st.session_state:
    st.session_state.parc = {}

# --- TITRE PRINCIPAL ---
st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>DEI : Gestion & Reconditionnement</h1>", unsafe_allow_html=True)

# --- MENU LATÉRAL ---
with st.sidebar:
    st.title("🛡️ Système DEI")
    page = st.radio("Navigation", ["📊 Vision Globale Stocks", "🏢 Gestion des Sites", "⚙️ Paramètres"])
    st.divider()
    st.write("Expertise Maintenance & Reconditionnement")

# --- PAGE : GESTION DES SITES ---
if page == "🏢 Gestion des Sites":
    st.header("🏢 Configuration Technique du Site")
    with st.form("site_form"):
        col1, col2 = st.columns(2)
        with col1:
            nom_site = st.text_input("Nom de l'installation")
            constructeur = st.selectbox("Constructeur", ["DEF", "Chubb", "ESSER", "Finsecur", "Siemens"])
        with col2:
            date_vgp = st.date_input("Dernière VGP")
            central_model = st.text_input("Modèle ECS")
        
        st.subheader("📦 Inventaire des Lots (pour Reconditionnement)")
        c1, c2, c3 = st.columns(3)
        ref = c1.text_input("Référence Détecteur (ex: OA05)")
        type_c = c2.selectbox("Type", TYPES_CAPTEURS)
        quantite = c3.number_input("Quantité installée", min_value=1)
        
        date_pose_det = st.date_input("Date de pose/reconditionnement du lot")
        
        if st.form_submit_button("🔨 Enregistrer / Mettre à jour le Site"):
            if nom_site:
                st.session_state.parc[nom_site] = {
                    "Infos": {"Marque": constructeur, "Model": central_model, "VGP": date_vgp},
                    "Stock": {"Ref": ref, "Type": type_c, "Qté": quantite, "Pose": date_pose_det}
                }
                st.success(f"Site {nom_site} enregistré.")

# --- PAGE : VISION GLOBALE STOCKS ---
elif page == "📊 Vision Globale Stocks":
    st.header("📊 État du Parc pour Reconditionnement")
    
    if not st.session_state.parc:
        st.info("Aucune donnée disponible. Créez un site pour voir l'analyse.")
    else:
        # Transformation en DataFrame pour visuel global
        data_list = []
        for nom, d in st.session_state.parc.items():
            age = (date.today() - d['Stock']['Pose']).days / 365
            # Alerte reconditionnement (standard 10 ans)
            statut = "🟢 OK"
            if age >= 9: statut = "🟠 PRÉVOIR RECOND."
            if age >= 10: statut = "🔴 ÉCHÉANCE DÉPASSÉE"
            
            data_list.append({
                "Site": nom,
                "Référence": d['Stock']['Ref'],
                "Type": d['Stock']['Type'],
                "Quantité": d['Stock']['Qté'],
                "Âge (Ans)": round(age, 1),
                "État Recond.": statut
            })
        
        df = pd.DataFrame(data_list)
        
        # Filtre par référence pour le reconditionneur
        ref_filter = st.multiselect("Filtrer par Référence Matériel", df['Référence'].unique())
        if ref_filter:
            df = df[df['Référence'].isin(ref_filter)]
            
        st.dataframe(df, use_container_width=True)
        
        # Résumé pour la commande
        st.subheader("🛒 Total matériel par référence")
        summary = df.groupby('Référence')['Quantité'].sum()
        st.table(summary)

# --- SAUVEGARDE (EXPLICATION) ---
st.sidebar.divider()
st.sidebar.warning("Note : Les données sont temporaires. Pour une sauvegarde à vie, connectons une base de données.")
