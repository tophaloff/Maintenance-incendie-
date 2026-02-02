import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuration de la page pour un look moderne
st.set_page_config(page_title="SSI - Registre de Sécurité", layout="wide", initial_sidebar_state="expanded")

# --- STYLE CSS POUR L'INTERFACE ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if 'registre' not in st.session_state:
    st.session_state.registre = pd.DataFrame([
        {"ID": "ECS-01", "Élément": "Centrale Principale", "Type": "ECS", "Zone": "Accueil", "Dernière VGP": "2024-01-15", "Période": "Trimestriel"}
    ])

if 'anomalies' not in st.session_state:
    st.session_state.anomalies = pd.DataFrame(columns=["Date", "Équipement", "Description", "Gravité", "Statut"])

PERIODES = {"Mensuel": 30, "Trimestriel": 90, "Semestriel": 180, "Annuel": 365}

# --- BARRE LATÉRALE (NAVIGATION) ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/fire-alarm.png", width=80)
    st.title("Menu Maintenance")
    page = st.radio("Aller vers :", ["📊 Tableau de Bord", "🔍 Signaler une Anomalie", "➕ Ajouter un Organe"])

# --- PAGE 1 : TABLEAU DE BORD ---
if page == "📊 Tableau de Bord":
    st.header("Tableau de Bord de Conformité SSI")
    
    # Indicateurs rapides (KPIs)
    col1, col2, col3 = st.columns(3)
    total_organes = len(st.session_state.registre)
    anomalies_ouvertes = len(st.session_state.anomalies[st.session_state.anomalies["Statut"] == "Ouvert"])
    
    col1.metric("Organes au Registre", total_organes)
    col2.metric("Anomalies en cours", anomalies_ouvertes, delta_color="inverse")
    col3.metric("Prochaine Commission", "12/2026", "230 jours")

    st.divider()

    # Tableau Principal avec Couleurs
    st.subheader("État des Vérifications Périodiques")
    
    def calculer_statut(row):
        derniere = datetime.strptime(str(row['Dernière VGP']), '%Y-%m-%d')
        echeance = derniere + timedelta(days=PERIODES[row['Période']])
        jours_restants = (echeance.date() - datetime.now().date()).days
        
        if jours_restants < 0: return "🔴 RETARD", "error"
        elif jours_restants < 15: return "🟠 À PRÉVOIR", "warning"
        else: return "🟢 CONFORME", "success"

    df_display = st.session_state.registre.copy()
    df_display[['État', 'Niveau']] = df_display.apply(lambda r: pd.Series(calculer_statut(r)), axis=1)
    
    st.table(df_display[["ID", "Élément", "Zone", "Période", "Dernière VGP", "État"]])

    # Affichage des anomalies en cours
    if not st.session_state.anomalies.empty:
        st.subheader("⚠️ Anomalies actives")
        st.warning("Des défauts ont été signalés et nécessitent une intervention.")
        st.dataframe(st.session_state.anomalies[st.session_state.anomalies["Statut"] == "Ouvert"], use_container_width=True)

# --- PAGE 2 : SIGNALER UNE ANOMALIE ---
elif page == "🔍 Signaler une Anomalie":
    st.header("Rapport d'Anomalie / Essais Mensuels")
    with st.form("form_anomalie"):
        equip = st.selectbox("Équipement concerné", st.session_state.registre["Élément"])
        desc = st.text_area("Description du défaut (ex: Voyant dérangement batterie)")
        gravite = st.select_slider("Gravité", options=["Mineure", "Moyenne", "Critique"])
        submit = st.form_submit_button("Enregistrer l'anomalie")
        
        if submit:
            nouvelle_a = {"Date": datetime.now().strftime("%d/%m/%Y"), "Équipement": equip, 
                          "Description": desc, "Gravité": gravite, "Statut": "Ouvert"}
            st.session_state.anomalies = pd.concat([st.session_state.anomalies, pd.DataFrame([nouvelle_a])], ignore_index=True)
            st.success("Anomalie enregistrée dans le registre de sécurité.")

# --- PAGE 3 : AJOUTER UN ORGANE ---
elif page == "➕ Ajouter un Organe":
    st.header("Configuration du Système")
    # Formulaire simplifié ici...
    st.info("Utilisez ce formulaire pour enregistrer un nouveau détecteur, déclencheur manuel ou clapet coupe-feu.")
