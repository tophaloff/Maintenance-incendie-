import streamlit as st
import pandas as pd
from datetime import datetime, date
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# --- CONFIGURATION ---
st.set_page_config(page_title="Gestionnaire SSI Expert", layout="wide")

# Référentiels Constructeurs & Matériels
CONSTRUCTEURS = ["DEF", "Chubb", "ESSER", "Finsecur", "Siemens", "Eaton", "Neutronic"]
TYPES_BATT = ["12V 7Ah", "12V 12Ah", "12V 18Ah", "12V 24Ah", "2V (Éléments)"]

# --- INITIALISATION DE LA MÉMOIRE ---
if 'parc' not in st.session_state:
    st.session_state.parc = {}

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🛡️ Expert SSI")
    page = st.radio("Menu", ["🌍 Parc Immobilier", "➕ Nouveau Site", "📄 Rapports & Certificats"])
    st.divider()
    st.info("Conforme NF S 61-933 & APSAD R7")

# --- FONCTION : CALCUL ALERTE BATTERIE ---
def check_batterie(date_pose):
    if not date_pose: return "Inconnu", "grey"
    ans_ecoules = (date.today() - date_pose).days / 365
    if ans_ecoules >= 4: return "🔴 À REMPLACER (4 ans+)", "red"
    if ans_ecoules >= 3.5: return "🟠 PRÉVOIR REMPLACEMENT", "orange"
    return f"🟢 OK ({ans_ecoules:.1f} ans)", "green"

# --- PAGE : NOUVEAU SITE ---
if page == "➕ Nouveau Site":
    st.header("🏗️ Création d'un nouveau dossier technique")
    with st.form("crea_site"):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nom de l'établissement")
            adresse = st.text_input("Adresse / Ville")
            marque = st.selectbox("Constructeur Centrale", CONSTRUCTEURS)
        with c2:
            model = st.text_input("Modèle ECS / CMSI")
            date_inst = st.date_input("Date mise en service SSI", date.today())
        
        st.subheader("🔋 Configuration Énergie (Batteries)")
        cb1, cb2, cb3 = st.columns(3)
        t_batt = cb1.selectbox("Type de batteries", TYPES_BATT)
        d_batt = cb2.date_input("Date de pose batteries")
        s_batt = cb3.text_input("N° de série / Lot")

        st.subheader("🗺️ Documentation")
        plan = st.file_uploader("Upload Plan de zone (PDF/JPG)", type=['pdf','png','jpg'])

        if st.form_submit_button("Enregistrer le Site"):
            st.session_state.parc[nom] = {
                "Infos": {"Adresse": adresse, "Marque": marque, "Modèle": model, "Install": date_inst},
                "Batteries": {"Type": t_batt, "Pose": d_batt, "SN": s_batt},
                "Points": [], # Pour les futurs détecteurs individuels
                "Plan": plan
            }
            st.success("Dossier créé avec succès.")

# --- PAGE : PARC IMMOBILIER ---
elif page == "🌍 Parc Immobilier":
    st.header("🌍 Supervision du Parc")
    if not st.session_state.parc:
        st.warning("Aucun site en base de données.")
    else:
        site_nom = st.selectbox("Choisir une installation", list(st.session_state.parc.keys()))
        s = st.session_state.parc[site_nom]

        # Dashboard Visuel
        col_inf, col_bat = st.columns(2)
        
        with col_inf:
            st.markdown(f"### 📋 {site_nom}")
            st.write(f"**📍 Localisation :** {s['Infos']['Adresse']}")
            st.write(f"**🔌 Système :** {s['Infos']['Marque']} {s['Infos']['Modèle']}")
            if s['Plan']: st.success("✅ Plan de dépannage disponible")
        
        with col_bat:
            st.markdown("### 🔋 État des Batteries")
            msg, color = check_batterie(s['Batteries']['Pose'])
            st.subheader(msg)
            st.write(f"Type : {s['Batteries']['Type']} | S/N : {s['Batteries']['SN']}")
            st.write(f"Dernière pose : {s['Batteries']['Pose']}")

        st.divider()
        
        # Section Inventaire Détaillé
        st.subheader("🔍 Inventaire des Points (Détecteurs/DM)")
        with st.expander("Ajouter un composant spécifique"):
            with st.form("add_point"):
                cp1, cp2, cp3 = st.columns(3)
                p_type = cp1.selectbox("Type", ["Optique", "Thermique", "DM", "Sirène"])
                p_adr = cp2.text_input("Adresse (ex: L1P42)")
                p_loc = cp3.text_input("Localisation précise")
                if st.form_submit_button("Ajouter le point"):
                    s['Points'].append({"Type": p_type, "Adresse": p_adr, "Loc": p_loc})
                    st.rerun()
        
        if s['Points']:
            st.table(pd.DataFrame(s['Points']))

# --- PAGE : RAPPORTS ---
elif page == "📄 Rapports & Certificats":
    st.header("📄 Génération de document officiel")
    # (Logique de génération PDF similaire à la précédente, avec données enrichies)
    st.info("Sélectionnez un site en supervision pour éditer son PV de visite.")
