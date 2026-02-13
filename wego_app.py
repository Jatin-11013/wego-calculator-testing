import streamlit as st

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

    "Debit Cards(Master)(<=2000)": {
        "PhonePe(Aertrip)": ("percent", 0.35),
        "PhonePe": ("percent", 0.35),
        "RazorPay(Aertrip)": ("percent", 0.40),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 0.50)
    },
    "Debit Cards(Visa)(<=2000)": {
        "PhonePe(Aertrip)": ("percent", 0.35),
        "PhonePe": ("percent", 0.35),
        "RazorPay(Aertrip)": ("percent", 0.40),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 0.50)
    },
    "Debit Cards(Master)(>2000)": {
        "PhonePe(Aertrip)": ("percent", 0.78),
        "PhonePe": ("percent", 0.78),
        "RazorPay(Aertrip)": ("percent", 0.80),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 0.60)
    },
    "Debit Cards(Visa)(>2000)": {
        "PhonePe(Aertrip)": ("percent", 0.78),
        "PhonePe": ("percent", 0.78),
        "RazorPay(Aertrip)": ("percent", 0.80),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 0.60)
    },
    "Debit Cards(Corporate)": {
        "PhonePe(Aertrip)": ("percent", 2.25),
        "PhonePe": ("percent", 2.25),
        "RazorPay(Aertrip)": ("percent", 2.55),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 2.20)
    },
    "Debit Cards(Rupay)": {
        "PhonePe(Aertrip)": ("percent", 0.0),
        "PhonePe": ("percent", 0.0),
        "RazorPay(Aertrip)": ("percent", 0.10),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 0.0)
    },
    "Debit Cards(Prepaid)": {
        "PhonePe(Aertrip)": ("percent", 1.50),
        "PhonePe": ("percent", 1.50),
        "RazorPay(Aertrip)": ("percent", 2.00),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 2.50)
    },
    "Debit Cards(International)": {
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
    },

    "EMI": {
        "PhonePe(Aertrip)": ("flat", 0.0),
        "PhonePe": ("flat", 0.0),
        "RazorPay(Aertrip)": ("percent", 2.50),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("flat", 0.0)
    },
    "Cardless EMI": {
        "PhonePe(Aertrip)": ("flat", 0.0),
        "PhonePe": ("flat", 0.0),
        "RazorPay(Aertrip)": ("percent", 2.50),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("flat", 0.0)
    },

    "Wallet(PhonePe)": {
        "PhonePe(Aertrip)": ("percent", 1.50),
        "PhonePe": ("percent", 1.50),
        "RazorPay(Aertrip)": ("percent", 1.70),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 1.50)
    },
    "Wallet(Amazon Pay)": {
        "PhonePe(Aertrip)": ("flat", 0.0),
        "PhonePe": ("flat", 0.0),
        "RazorPay(Aertrip)": ("percent", 1.70),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 1.50)
    },
    "Wallet(Ola)": {
        "PhonePe(Aertrip)": ("flat", 0.0),
        "PhonePe": ("flat", 0.0),
        "RazorPay(Aertrip)": ("percent", 1.70),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 1.50)
    },
    "Wallet(Jio)": {
        "PhonePe(Aertrip)": ("flat", 0.0),
        "PhonePe": ("flat", 0.0),
        "RazorPay(Aertrip)": ("percent", 1.70),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 1.50)
    },
    "Wallet(Mobikwik)": {
        "PhonePe(Aertrip)": ("flat", 0.0),
        "PhonePe": ("flat", 0.0),
        "RazorPay(Aertrip)": ("percent", 1.70),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 1.50)
    },
    "Wallet(Freecharge)": {
        "PhonePe(Aertrip)": ("flat", 0.0),
        "PhonePe": ("flat", 0.0),
        "RazorPay(Aertrip)": ("percent", 1.70),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("flat", 0.0)
    },
    "Wallet(Airtel)": {
        "PhonePe(Aertrip)": ("flat", 0.0),
        "PhonePe": ("flat", 0.0),
        "RazorPay(Aertrip)": ("percent", 1.70),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 1.50)
    },
    "Wallet(Payzapp)": {
        "PhonePe(Aertrip)": ("flat", 0.0),
        "PhonePe": ("flat", 0.0),
        "RazorPay(Aertrip)": ("percent", 1.70),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 1.50)
    },
    "Wallet(Bajaj)": {
        "PhonePe(Aertrip)": ("flat", 0.0),
        "PhonePe": ("flat", 0.0),
        "RazorPay(Aertrip)": ("percent", 1.70),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 1.50)
    },
    "Wallet(Yes Pay)": {
        "PhonePe(Aertrip)": ("flat", 0.0),
        "PhonePe": ("flat", 0.0),
        "RazorPay(Aertrip)": ("percent", 1.70),
        "PayU": ("flat", 0.0),
        "Easebuzz": ("percent", 1.50)
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
    # ----- META FEES -----
    meta_fee, base_fee_calc, ads_fee = calculate_meta_fee(
        meta_partner, flight_type, purchase_amount, pax_count
    )

    # ----- HANDLING FEES GST CUT -----
    handling_fees_net = round(handling_fees / 1.18, 2)

    # ----- PG FEES -----
    total_for_pg = booking_amount + handling_fees
    pg_fees = pg_fees_input  # start with manual input
    rate_type = "N/A"
    value = 0

    if pg_fees_input in [0, None]:
        if payment_category != "None":
            key = payment_category
            # Debit card ranges adjustment
            if "Debit Cards" in payment_category:
                if payment_category in ["Debit Cards(Visa)", "Debit Cards(Master)"]:
                    key += "(<=2000)" if booking_amount <= 2000 else "(>2000)"
            if key in pg_rates and pg_name in pg_rates[key]:
                rate_type, value = pg_rates[key][pg_name]
                if rate_type == "percent":
                    pg_fees = round(total_for_pg * value / 100, 2)
                else:
                    pg_fees = value
        else:
            pg_fees = 0
            rate_type = "None"

    # ----- DI & PLB -----
    di_rate = 0 if supplier_name == "Other" else supplier_di.get(supplier_name, 0)
    di_amount = round(purchase_amount * di_rate, 2)

    plb_amount = 0
    if supplier_name in ["Indigo Corporate Travelport Universal Api (KTBOM278)", "Indigo Regular Fare (Corporate)(KTBOM278)"]:
        plb_amount = base_fare * (0.0075 if flight_type=="Domestic" else 0.015)
    elif supplier_name in ["Indigo Regular Corp Chandni (14354255C)", "Indigo Retail Chandni (14354255C)"]:
        plb_amount = base_fare * (0.0125 if flight_type=="Domestic" else 0.0185)
    plb_amount = round(plb_amount, 2)

    # ----- PURCHASE VS SALE -----
    purchase_side = purchase_amount + meta_fee + pg_fees
    sale_side = booking_amount + di_amount + handling_fees_net + plb_amount
    difference = round(sale_side - purchase_side, 2)

    # ----- DISPLAY -----
    st.divider()
    st.subheader("📊 Calculation Summary")
    st.markdown('<div class="summary-box">', unsafe_allow_html=True)
    o1, o2, o3, o4, o5 = st.columns(5)

    with o1:
        st.markdown("### 🏷 Supplier & DI")
        st.write(f"**Supplier:** {supplier_name}")
        st.write(f"**DI %:** {di_rate*100:.2f}%")
        st.write(f"**DI Amount:** ₹ {di_amount}")

    with o2:
        st.markdown("### 📢 Meta Fees")
        st.write(f"**Meta Partner:** {meta_partner}")
        st.write(f"**Base Fee:** ₹ {base_fee_calc}")
        if meta_partner == "Wego Ads":
            st.write(f"**Ads Fee:** ₹ {ads_fee}")
        st.write(f"**Total Meta Fees:** ₹ {meta_fee}")

    with o3:
        st.markdown("### 💳 PG Fees")
        st.write(f"**Payment Method:** {payment_category}")
        st.write(f"**Payment Gateway:** {pg_name}")
        st.write(f"**PG Fee Type:** {rate_type}")
        pg_percent_text = f"{value}%" if rate_type=="percent" else "Flat"
        st.write(f"**PG Fee % / Flat:** {pg_percent_text}")
        st.write(f"**PG Fees Amount:** ₹ {pg_fees}")

    with o4:
        st.markdown("### 🎯 PLB")
        plb_percent_text = "0%"
        if supplier_name in ["Indigo Corporate Travelport Universal Api (KTBOM278)", "Indigo Regular Fare (Corporate)(KTBOM278)"]:
            plb_percent_text = "0.75%" if flight_type=="Domestic" else "1.50%"
        elif supplier_name in ["Indigo Regular Corp Chandni (14354255C)", "Indigo Retail Chandni (14354255C)"]:
            plb_percent_text = "1.25%" if flight_type=="Domestic" else "1.85%"
        st.write(f"**Base Fare:** ₹ {base_fare}")
        st.write(f"**PLB % Applied:** {plb_percent_text}")
        st.write(f"**PLB Amount:** ₹ {plb_amount}")

    with o5:
        st.markdown("### 💰 Purchase vs Sale")
        st.write(f"**Purchase Side (Purchase + Meta + PG):** ₹ {purchase_side}")
        st.write(f"**Sale Side (Booking + DI + Handling + PLB):** ₹ {sale_side}")
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



