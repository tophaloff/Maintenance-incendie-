import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Configuration de l'interface
st.set_page_config(page_title="Supervision Multi-Sites SSI", layout="wide")

# --- STYLE ---
st.markdown("""
    <style>
    .site-card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALISATION ---
if 'sites' not in st.session_state:
    st.session_state.sites = ["Usine Nord", "Entrepôt Logistique", "Siège Social"]

if 'maintenances' not in st.session_state:
    # On ajoute une colonne 'Site' et une 'Gamme'
    st.session_state.maintenances = pd.DataFrame([
        {"Site": "Usine Nord", "Élément": "Centrale ECS", "Dernière VGP": "2024-01-10", "Fréquence": 90, "Gamme": "Essai batteries + report défauts"},
        {"Site": "Entrepôt Logistique", "Élément": "Rideau RF", "Dernière VGP": "2023-11-05", "Fréquence": 180, "Gamme": "Test de descente + graissage"},
    ])

# --- BARRE LATÉRALE : SÉLECTION DU SITE ---
st.sidebar.title("🌍 Supervision")
site_filtre = st.sidebar.selectbox("Filtrer par site", ["Tous les sites"] + st.session_state.sites)

# --- VUE GLOBALE (MULTI-SITES) ---
st.title("🛡️ Supervision Multi-Sites & Gammes")

# Filtrage des données
df = st.session_state.maintenances
if site_filtre != "Tous les sites":
    df = df[df['Site'] == site_filtre]

# Affichage des KPIs
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Installations", len(df))
with col2:
    # Calcul des retards
    df['Prochaine'] = df.apply(lambda r: (datetime.strptime(str(r['Dernière VGP']), '%Y-%m-%d') + timedelta(days=r['Fréquence'])).date(), axis=1)
    retards = len(df[df['Prochaine'] < datetime.now().date()])
    st.metric("Actions en retard", retards, delta=-retards, delta_color="inverse")

st.divider()

# --- AFFICHAGE DES GAMMES DE MAINTENANCE ---
st.subheader("📋 Détail des installations et Gammes Opératoires")

for index, row in df.iterrows():
    statut_color = "🔴" if row['Prochaine'] < datetime.now().date() else "🟢"
    
    with st.expander(f"{statut_color} {row['Site']} - {row['Élément']} (Échéance : {row['Prochaine']})"):
        st.write(f"**Dernière visite :** {row['Dernière VGP']}")
        st.info(f"**Gamme de maintenance à appliquer :** \n\n {row['Gamme']}")
        
        # Simulation d'une check-list interactive
        st.write("---")
        st.markdown("**Check-list de l'intervenant :**")
        c1, c2, c3 = st.columns(3)
        c1.checkbox("Contrôle visuel", key=f"v_{index}")
        c2.checkbox("Test fonctionnel", key=f"f_{index}")
        c3.checkbox("Nettoyage/Graissage", key=f"n_{index}")
        
        if st.button("Valider la maintenance", key=f"btn_{index}"):
            st.success(f"Maintenance enregistrée pour {row['Élément']} !")

# --- FORMULAIRE D'AJOUT ---
st.sidebar.divider()
with st.sidebar.expander("➕ Nouveau Site / Matériel"):
    nouveau_site = st.text_input("Nom du nouveau site")
    if st.button("Ajouter Site"):
        st.session_state.sites.append(nouveau_site)
        st.rerun()
