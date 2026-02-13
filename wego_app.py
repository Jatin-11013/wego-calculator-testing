import streamlit as st
import sqlite3
import hashlib

# ===================== AUTH / DB LAYER =====================

DB_NAME = "users.db"

def get_conn():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash

def user_exists():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def create_user(username, password, role):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, hash_password(password), role)
    )
    conn.commit()
    conn.close()

def get_user(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT username, password_hash, role FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row

def get_all_users():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT username, role FROM users")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_user(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def update_role(username, role):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET role = ? WHERE username = ?", (role, username))
    conn.commit()
    conn.close()

def update_password(username, new_password):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET password_hash = ? WHERE username = ?",
        (hash_password(new_password), username)
    )
    conn.commit()
    conn.close()

init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None

def show_create_admin():
    st.title("🔐 Create First Admin")
    st.info("First time setup: Create your admin account")

    username = st.text_input("Admin Username")
    password = st.text_input("Admin Password", type="password")
    password2 = st.text_input("Confirm Password", type="password")

    if st.button("Create Admin"):
        if not username or not password:
            st.error("Username and password required")
        elif password != password2:
            st.error("Passwords do not match")
        else:
            create_user(username, password, "admin")
            st.success("Admin created! Please refresh the page.")
            st.stop()

def show_login():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = get_user(username)
        if user is None:
            st.error("Invalid username or password")
        else:
            _, password_hash, role = user
            if verify_password(password, password_hash):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = role
                st.rerun()
            else:
                st.error("Invalid username or password")

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.rerun()

def admin_panel():
    st.subheader("🛠️ Admin Panel - User Management")

    with st.expander("➕ Add New User"):
        new_user = st.text_input("New Username", key="new_user")
        new_pass = st.text_input("New Password", type="password", key="new_pass")
        new_role = st.selectbox("Role", ["admin", "user"], key="new_role")

        if st.button("Create User"):
            if not new_user or not new_pass:
                st.error("Username and password required")
            else:
                try:
                    create_user(new_user, new_pass, new_role)
                    st.success("User created successfully")
                except sqlite3.IntegrityError:
                    st.error("Username already exists")

    st.divider()
    st.subheader("👥 Existing Users")

    users = get_all_users()
    for u, r in users:
        cols = st.columns([3, 2, 2, 2])
        cols[0].write(u)
        cols[1].write(r)

        if cols[2].button("Make Admin" if r != "admin" else "Make User", key=f"role_{u}"):
            new_r = "admin" if r != "admin" else "user"
            update_role(u, new_r)
            st.rerun()

        if cols[3].button("Delete", key=f"del_{u}"):
            if u == st.session_state.username:
                st.error("You cannot delete yourself")
            else:
                delete_user(u)
                st.rerun()

    with st.expander("🔑 Reset User Password"):
        ru = st.text_input("Username to reset")
        np = st.text_input("New Password", type="password")
        if st.button("Reset Password"):
            if get_user(ru) is None:
                st.error("User not found")
            else:
                update_password(ru, np)
                st.success("Password updated")

# ===================== GATE =====================

if not user_exists():
    show_create_admin()
    st.stop()

if not st.session_state.logged_in:
    show_login()
    st.stop()

st.markdown(
    f"""
    <div style="display:flex; justify-content: space-between; align-items:center;">
        <div>👤 Logged in as: <b>{st.session_state.username}</b> ({st.session_state.role})</div>
    </div>
    """,
    unsafe_allow_html=True
)

if st.button("🚪 Logout"):
    logout()

if st.session_state.role == "admin":
    admin_panel()
    st.divider()

# ===================== YOUR CALCULATOR APP =====================

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Booking Safety Calculator",
    layout="wide"
)

# -------- REMOVE EXTRA TOP SPACE & SMALLER FONTS --------
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem;
    }
    .summary-box p {
        font-size: 12px;
        margin-bottom: 3px;
    }
    .summary-box h3 {
        font-size: 14px;
        margin-bottom: 5px;
    }
    .stSelectbox label, .stNumberInput label {
        font-size: 13px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🧮 Booking Safety Calculator")
st.caption("Operation Team – Safe vs Loss Booking Tool")

# ---------------- DI MASTER ----------------
supplier_di = {
    "TBO Flights Online - BOMA774": 0.0064,
    "FlyShop Series Online API": 0.01,
    "Flyshop online API": 0.01,
    "Cleartrip Private Limited - AB 2": 0.01,
    "Travelopedia Series": 0.01,
    "Just Click N Pay Series": 0.01,
    "Fly24hrs Holiday Pvt. Ltd": 0.01,
    "Travelopedia": 0.01,
    "Etrave Flights": 0.01,
    "ETrav Tech Limited": 0.01,
    "Etrav Series Flights": 0.01,
    "Tripjack Pvt. Ltd.": 0.005,
    "Indigo Corporate Travelport Universal Api (KTBOM278)": 0.0045,
    "Indigo Regular Fare (Corporate)(KTBOM278)": 0.0045,
    "Indigo Retail Chandni (14354255C)": 0.0,
    "Indigo Regular Corp Chandni (14354255C)": 0.0,
    "BTO Bhasin Travels HAP OP7": 0.018,
    "Bhasin Travel Online HAP 7U63": 0.018,
    "AIR IQ": 0.01,
    "Tripjack Flights": 0.005,
    "Etrav HAP 58Y8": 0.01,
    # ZERO DI suppliers
    "Consulate General of Indonesia-Mumbai": 0,
    "RIYA HAP 6A4T": 0,
    "Consulate Genenal Of Hungary - Visa": 0,
    "MUSAFIR.COM INDIA PVT LTD": 0,
    "MASTER BSP": 0,
    "Japan vfs": 0,
    "VFS Global Georgia - Visa": 0,
    "Akbar Travels HAP 3OT9": 0,
    "GRNConnect": 0,
    "CHINA VFS": 0,
    "FLYCREATIVE ONLINE PVT. LTD (LCC)": 0,
    "Bajaj Allianz General Insurance": 0,
    "South Africa VFS": 0,
    "MakeMyTrip (India) Private Limited": 0,
    "Travelport Universal Api": 0,
    "Deputy High Commission of Bangladesh, Mumbai": 0,
    "Bajaj Allianz General Insurance - Aertrip A/C": 0,
    "Germany Visa": 0,
    "Cleartrip Private Limited - AB 1": 0,
    "CDV HOLIDAYS PRIVATE LIMITED": 0,
    "Rudraa Tours And Travels Jayashree Patil": 0,
    "France Vfs": 0,
    "Vietnam Embassy New Delhi": 0,
    "Srilanka E Visa": 0,
    "Morocco Embassy New Delhi": 0,
    "Regional Passport Office-Mumbai": 0,
    "Klook Travel Tech Ltd Hong Kong HK": 0,
    "VANDANA VISA SERVICES": 0,
    "Consulate General of the Republic of Poland": 0,
    "Akbar Travel online AG43570": 0,
    "Just Click N Pay": 0,
    "IRCTC": 0,
    "Akbar Travels of India Pvt Ltd - (AG004261)": 0,
    "Embassy of Gabon": 0,
    "Go Airlines (India) Limited ( Offline )": 0,
    "UK VFS": 0,
    "GO KITE TRAVELS AND TOURS LLP": 0,
    "Travel super Mall (IXBAIU9800)": 0,
    "AirIQ Flights series Supplier": 0
}

supplier_list = sorted(supplier_di.keys())
supplier_list.insert(0, "Other")

# ---------------- INPUT ROW 1 ----------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    meta_partner = st.selectbox("Meta Partner", ["None", "Wego", "Wego Ads"])
with c2:
    flight_type = st.selectbox("Flight Type", ["Domestic", "International"])
with c3:
    supplier_name = st.selectbox("Supplier Name", supplier_list)
with c4:
    pax_count = st.number_input("Pax Count", min_value=1, step=1)

# ---------------- INPUT ROW 2 ----------------
c5, c6, c7, c8, c9 = st.columns(5)
with c5:
    base_fare = st.number_input("Base Fare (₹)", min_value=0.0, step=100.0)
with c6:
    purchase_amount = st.number_input("Purchase Amount (₹)", min_value=0.0, step=100.0)
with c7:
    booking_amount = st.number_input("Booking Amount (₹)", min_value=0.0, step=100.0)
with c8:
    handling_fees = st.number_input("Handling Fees (₹)", min_value=0.0, step=10.0)
with c9:
    pg_fees_input = st.number_input("PG Fees (₹)", min_value=0.0, step=10.0)

# ---------------- PG SELECTION ----------------
c10, c11 = st.columns(2)
with c10:
    payment_category = st.selectbox("Payment Method", [
        "None","Net Banking(AXIS)", "Net Banking(ICICI)", "Net Banking(HDFC)", "Net Banking(KOTAK)","Net Banking(YES)","Net Banking(OTHER)","Net Banking(SBI)",
        "Credit Cards(Visa)", "Credit Cards(Master)", "Credit Cards(Rupay)","Credit Cards(Diners)","Credit Cards(Amex)","Credit Cards(Corporate)","Credit Cards(International)",
        "Debit Cards(Visa)", "Debit Cards(Master)", "Debit Cards(Rupay)","Debit Cards(International)","Debit Cards(Corporate)","Debit Cards(Prepaid)",
        "UPI","EMI", "Cardless EMI","Wallet(PhonePe)","Wallet(Amazon Pay)","Wallet(Ola)","Wallet(Jio)","Wallet(Mobikwik)","Wallet(Freecharge)","Wallet(Airtel)","Wallet(Payzapp)","Wallet(Bajaj)","Wallet(Yes Pay)"
    ])
with c11:
    pg_name = st.selectbox("Payment Gateway", [
        "PhonePe(Aertrip)", "PhonePe", "RazorPay(Aertrip)", "PayU", "Easebuzz"
    ])

# ---------------- PG FEES MASTER ----------------
# (UNCHANGED — same as your code; kept for correctness)
pg_rates = {
    "Net Banking(HDFC)": {
        "PhonePe(Aertrip)": ("percent", 1.50),
        "PhonePe": ("percent", 1.50),
        "RazorPay(Aertrip)": ("percent", 1.55),
        "PayU": ("percent", 0.0),
        "Easebuzz": ("percent", 1.65)
    },
    "Net Banking(ICICI)": {
        "PhonePe(Aertrip)": ("percent", 1.50),
        "PhonePe": ("flat", 22.0),
        "RazorPay(Aertrip)": ("percent", 1.55),
        "PayU": ("flat", 30.29),
        "Easebuzz": ("flat", 12.50)
    },
    "Net Banking(KOTAK)": {
        "PhonePe(Aertrip)": ("percent", 1.50),
        "PhonePe": ("flat", 33.0),
        "RazorPay(Aertrip)": ("percent", 1.55),
        "PayU": ("flat", 23.29),
        "Easebuzz": ("flat", 12.50)
    },
    "Net Banking(SBI)": {
        "PhonePe(Aertrip)": ("percent", 1.50),
        "PhonePe": ("flat", 22.0),
        "RazorPay(Aertrip)": ("percent", 1.55),
        "PayU": ("flat", 30.29),
        "Easebuzz": ("flat", 12.50)
    },
    "Net Banking(AXIS)": {
        "PhonePe(Aertrip)": ("percent", 1.50),
        "PhonePe": ("flat", 22.0),
        "RazorPay(Aertrip)": ("percent", 1.55),
        "PayU": ("flat", 25.29),
        "Easebuzz": ("flat", 12.50)
    },
    "Net Banking(YES)": {
        "PhonePe(Aertrip)": ("percent", 1.00),
        "PhonePe": ("flat", 18.0),
        "RazorPay(Aertrip)": ("percent", 1.55),
        "PayU": ("flat", 23.29),
        "Easebuzz": ("flat", 12.50)
    },
    "Net Banking(OTHER)": {
        "PhonePe(Aertrip)": ("percent", 1.00),
        "PhonePe": ("flat", 18.0),
        "RazorPay(Aertrip)": ("percent", 1.50),
        "PayU": ("flat", 23.29),
        "Easebuzz": ("flat", 12.50)
    },
    "Credit Cards(Master)": {
        "PhonePe(Aertrip)": ("percent", 1.50),
        "PhonePe": ("percent", 1.50),
        "RazorPay(Aertrip)": ("percent", 1.86),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 1.60)
    },
    "Credit Cards(Visa)": {
        "PhonePe(Aertrip)": ("percent", 1.50),
        "PhonePe": ("percent", 1.50),
        "RazorPay(Aertrip)": ("percent", 1.86),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 1.60)
    },
    "Credit Cards(Rupay)": {
        "PhonePe(Aertrip)": ("percent", 1.50),
        "PhonePe": ("percent", 1.50),
        "RazorPay(Aertrip)": ("percent", 1.86),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 1.60)
    },
    "Credit Cards(Diners)": {
        "PhonePe(Aertrip)": ("percent", 1.80),
        "PhonePe": ("percent", 1.80),
        "RazorPay(Aertrip)": ("percent", 2.70),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 2.75)
    },
    "Credit Cards(Amex)": {
        "PhonePe(Aertrip)": ("percent", 2.55),
        "PhonePe": ("percent", 2.55),
        "RazorPay(Aertrip)": ("percent", 2.70),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 2.75)
    },
    "Credit Cards(Corporate)": {
        "PhonePe(Aertrip)": ("percent", 2.25),
        "PhonePe": ("percent", 2.25),
        "RazorPay(Aertrip)": ("percent", 2.55),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 2.50)
    },
    "Credit Cards(International)": {
        "PhonePe(Aertrip)": ("flat", 0.0),
        "PhonePe": ("flat", 0.0),
        "RazorPay(Aertrip)": ("percent", 2.60),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 4.00)
    },
    "UPI": {
        "PhonePe(Aertrip)": ("percent", 0.0),
        "PhonePe": ("percent", 0.0),
        "RazorPay(Aertrip)": ("percent", 0.50),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 0.0)
    }
}

# ---------------- FUNCTIONS ----------------
def calculate_meta_fee(meta, flight, amount, pax):
    if meta == "None":
        return 0, 0, 0
    if flight == "Domestic":
        base_fee = 200 if pax <= 2 else 300
    else:
        base_fee = 400 if amount <= 30000 else 600
    ads_fee = 123 if meta == "Wego Ads" else 0
    return base_fee + ads_fee, base_fee, ads_fee

# ---------------- CALCULATE ----------------
if st.button("🧮 Calculate"):
    meta_fee, base_fee_calc, ads_fee = calculate_meta_fee(
        meta_partner, flight_type, purchase_amount, pax_count
    )

    handling_fees_net = round(handling_fees / 1.18, 2)

    total_for_pg = booking_amount + handling_fees
    pg_fees = pg_fees_input
    rate_type = "N/A"
    value = 0

    if pg_fees_input in [0, None]:
        if payment_category != "None":
            key = payment_category
            if key in pg_rates and pg_name in pg_rates[key]:
                rate_type, value = pg_rates[key][pg_name]
                if rate_type == "percent":
                    pg_fees = round(total_for_pg * value / 100, 2)
                else:
                    pg_fees = value
        else:
            pg_fees = 0
            rate_type = "None"

    di_rate = 0 if supplier_name == "Other" else supplier_di.get(supplier_name, 0)
    di_amount = round(purchase_amount * di_rate, 2)

    plb_amount = 0
    if supplier_name in ["Indigo Corporate Travelport Universal Api (KTBOM278)", "Indigo Regular Fare (Corporate)(KTBOM278)"]:
        plb_amount = base_fare * (0.0075 if flight_type=="Domestic" else 0.015)
    elif supplier_name in ["Indigo Regular Corp Chandni (14354255C)", "Indigo Retail Chandni (14354255C)"]:
        plb_amount = base_fare * (0.0125 if flight_type=="Domestic" else 0.0185)
    plb_amount = round(plb_amount, 2)

    purchase_side = purchase_amount + meta_fee + pg_fees
    sale_side = booking_amount + di_amount + handling_fees_net + plb_amount
    difference = round(sale_side - purchase_side, 2)

    st.divider()
    st.subheader("📊 Calculation Summary")
    st.markdown('<div class="summary-box">', unsafe_allow_html=True)
    o1, o2, o3, o4, o5 = st.columns(5)

    with o5:
        st.markdown("### 💰 Purchase vs Sale")
        st.write(f"**Purchase Side:** ₹ {purchase_side}")
        st.write(f"**Sale Side:** ₹ {sale_side}")
        st.markdown(f"### 💹 Difference: ₹ {difference}")
        if difference < 0:
            st.error("❌ Loss Booking")
        else:
            st.success("✅ Safe Booking")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 10px;
        bottom: 10px;
        color: #6c757d;
        font-size: 12px;
    }
    </style>
    <div class="footer">
        Auto-updated via GitHub | Last updated on 08 Feb 2026
    </div>
    """,
    unsafe_allow_html=True
)
