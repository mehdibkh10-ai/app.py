import streamlit as st
import sqlite3
import hashlib

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Event SaaS PRO", layout="wide")

# ======================
# STYLE (BLANC / NOIR CLEAN)
# ======================
st.markdown("""
<style>
.stApp {
    background-color: white;
    color: black;
}

h1,h2,h3,label,p {
    color: black !important;
}

div[data-testid="metric-container"] {
    background-color: #f5f5f5;
    padding: 15px;
    border-radius: 10px;
}

.stButton>button {
    background-color: black;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ======================
# DB
# ======================
conn = sqlite3.connect("gestion.db", check_same_thread=False)
c = conn.cursor()

# USERS
c.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)""")

# CLIENTS
c.execute("""CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    telephone TEXT,
    email TEXT,
    adresse TEXT,
    note TEXT
)""")

# EVENTS
c.execute("""CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    type_event TEXT,
    nom_event TEXT,
    nom_mari TEXT,
    nom_mariee TEXT,
    date_debut TEXT,
    date_fin TEXT,
    budget REAL,
    cout REAL,
    acompte REAL
)""")

# STOCK
c.execute("""CREATE TABLE IF NOT EXISTS stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    prix_achat REAL,
    quantite INTEGER
)""")

conn.commit()

# ======================
# PASSWORD SECURITY
# ======================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ======================
# LOGIN SYSTEM
# ======================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()

        if user and user[2] == hash_password(password):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Login incorrect ❌")

    # CREATE ACCOUNT
    st.subheader("Créer compte")
    new_user = st.text_input("New username")
    new_pass = st.text_input("New password", type="password")

    if st.button("Register"):
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (new_user, hash_password(new_pass)))
        conn.commit()
        st.success("Compte créé ✔")

if not st.session_state.logged_in:
    login()
    st.stop()

# ======================
# MENU
# ======================
menu = st.sidebar.radio("Menu", ["📊 Dashboard", "👤 Clients", "📅 Events", "📦 Stock"])

st.title("🎉 Event SaaS PRO")

# ======================
# 👤 CLIENTS
# ======================
if menu == "👤 Clients":
    st.header("Clients")

    nom = st.text_input("Nom")
    tel = st.text_input("Téléphone")
    email = st.text_input("Email")
    adresse = st.text_input("Adresse")
    note = st.text_area("Note")

    if st.button("Ajouter client"):
        c.execute("""INSERT INTO clients VALUES (NULL, ?, ?, ?, ?, ?)""",
                  (nom, tel, email, adresse, note))
        conn.commit()
        st.success("Client ajouté")

    st.subheader("Liste clients")

    for cl in c.execute("SELECT * FROM clients"):
        st.write(f"👤 {cl[1]} | 📞 {cl[2]} | ✉ {cl[3]} | 📍 {cl[4]}")

# ======================
# 📅 EVENTS
# ======================
elif menu == "📅 Events":
    st.header("Events")

    clients = c.execute("SELECT * FROM clients").fetchall()
    client_dict = {c[1]: c[0] for c in clients}

    client = st.selectbox("Client", list(client_dict.keys()))

    type_event = st.selectbox("Type", ["Mariage", "Anniversaire", "Conférence", "Autre"])
    nom_event = st.text_input("Nom event")

    nom_mari = ""
    nom_mariee = ""

    if type_event == "Mariage":
        st.subheader("💍 Mariage")
        nom_mari = st.text_input("Nom mari")
        nom_mariee = st.text_input("Nom mariée")

    date1 = st.date_input("Date début")
    date2 = st.date_input("Date fin")

    budget = st.number_input("Budget")
    cout = st.number_input("Coût")
    acompte = st.number_input("Acompte")

    if st.button("Créer event"):
        c.execute("""INSERT INTO events VALUES (
        NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (client_dict[client], type_event, nom_event,
         nom_mari, nom_mariee,
         str(date1), str(date2),
         budget, cout, acompte))

        conn.commit()
        st.success("Event ajouté")

    st.subheader("Liste events")

    events = c.execute("SELECT type_event, nom_event, budget, cout FROM events").fetchall()

    for e in events:
        gain = e[2] - e[3]
        st.write(f"📅 {e[0]} | {e[1]} | 💰 Gain: {gain} DA")

# ======================
# 📦 STOCK
# ======================
elif menu == "📦 Stock":
    st.header("Stock")

    nom = st.text_input("Produit")
    prix_achat = st.number_input("Prix achat")
    quantite = st.number_input("Quantité", min_value=0)

    prix_location = prix_achat / 4 if prix_achat > 0 else 0

    st.info(f"💡 Prix location = {prix_location} DA")

    if st.button("Ajouter produit"):
        c.execute("INSERT INTO stock VALUES (NULL, ?, ?, ?)",
                  (nom, prix_achat, quantite))
        conn.commit()
        st.success("Produit ajouté")

    st.subheader("Inventaire")

    for s in c.execute("SELECT nom, prix_achat, quantite FROM stock"):
        location = s[1] / 4
        valeur = s[1] * s[2]

        st.write(f"📦 {s[0]} | Achat: {s[1]} | Location: {location} | Stock: {s[2]} | Valeur: {valeur}")

# ======================
# 📊 DASHBOARD
# ======================
elif menu == "📊 Dashboard":
    st.header("Dashboard")

    events = c.execute("SELECT budget, cout FROM events").fetchall()
    profit = sum([e[0] - e[1] for e in events])

    stock = c.execute("SELECT prix_achat, quantite FROM stock").fetchall()
    stock_value = sum([s[0] * s[1] for s in stock])

    st.metric("💰 Profit", f"{profit} DA")
    st.metric("📦 Stock value", f"{stock_value} DA")

    st.subheader("📈 Graph")
    st.bar_chart([e[0] - e[1] for e in events])
