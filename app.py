import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# ----------------------
# Database Setup
# ----------------------
conn = sqlite3.connect("realestate.db")
c = conn.cursor()

# Create tables if not exist
c.execute('''CREATE TABLE IF NOT EXISTS Customers (
    CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT, Contact TEXT, Email TEXT,
    Requirement TEXT, PreferredType TEXT,
    Budget REAL, Status TEXT,
    FollowUpDate TEXT, Notes TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS Properties (
    PropertyID INTEGER PRIMARY KEY AUTOINCREMENT,
    OwnerName TEXT, Contact TEXT, Type TEXT,
    Location TEXT, Size TEXT,
    AskingPrice REAL, Status TEXT,
    BrokeragePercent TEXT, DateListed TEXT, Remarks TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS Deals (
    DealID INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerID INTEGER, PropertyID INTEGER,
    TransactionType TEXT, Date TEXT,
    Value REAL, BrokeragePercent TEXT,
    BrokerageAmount REAL, Status TEXT,
    PaymentSchedule TEXT,
    FOREIGN KEY(CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY(PropertyID) REFERENCES Properties(PropertyID)
)''')

conn.commit()

# ----------------------
# Streamlit UI
# ----------------------
st.title("🏠 Real Estate CRM Prototype")

menu = ["Dashboard", "Customers", "Properties", "Deals"]
choice = st.sidebar.selectbox("Menu", menu)

# ----------------------
# Dashboard
# ----------------------
if choice == "Dashboard":
    st.header("📊 Business Dashboard")

    cust_df = pd.read_sql("SELECT * FROM Customers", conn)
    prop_df = pd.read_sql("SELECT * FROM Properties", conn)
    deal_df = pd.read_sql("SELECT * FROM Deals", conn)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Customers", len(cust_df))
    col2.metric("Properties Listed", len(prop_df))
    col3.metric("Deals Closed", len(deal_df[deal_df['Status']=="Closed"]))

    if not deal_df.empty:
        st.subheader("Revenue Trend (Brokerage Amount)")
        deal_df["Date"] = pd.to_datetime(deal_df["Date"], errors='coerce')
        rev = deal_df.groupby(deal_df["Date"].dt.to_period("M"))["BrokerageAmount"].sum()
        st.line_chart(rev)

# ----------------------
# Customers
# ----------------------
elif choice == "Customers":
    st.header("👥 Customer Management")
    with st.form("add_cust"):
        name = st.text_input("Name")
        contact = st.text_input("Contact")
        email = st.text_input("Email")
        req = st.selectbox("Requirement", ["Buy", "Sell", "Rent"])
        ptype = st.text_input("Preferred Type")
        budget = st.number_input("Budget", min_value=0.0)
        status = st.selectbox("Status", ["New Lead", "In Discussion", "Closed-Won", "Closed-Lost"])
        follow = st.date_input("Next Follow-up")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add Customer")
        if submitted:
            c.execute("INSERT INTO Customers (Name, Contact, Email, Requirement, PreferredType, Budget, Status, FollowUpDate, Notes) VALUES (?,?,?,?,?,?,?,?,?)",
                      (name, contact, email, req, ptype, budget, status, str(follow), notes))
            conn.commit()
            st.success("Customer added successfully!")

    st.subheader("Customer List")
    df = pd.read_sql("SELECT * FROM Customers", conn)
    st.dataframe(df)

# ----------------------
# Properties
# ----------------------
elif choice == "Properties":
    st.header("🏢 Property Management")
    with st.form("add_prop"):
        owner = st.text_input("Owner Name")
        contact = st.text_input("Contact")
        ptype = st.selectbox("Type", ["Apartment", "Villa", "Plot", "Commercial"])
        location = st.text_input("Location")
        size = st.text_input("Size")
        price = st.number_input("Asking Price", min_value=0.0)
        status = st.selectbox("Status", ["Available", "Sold", "Rented"])
        brokerage = st.text_input("Brokerage %", value="2%")
        datelisted = st.date_input("Date Listed")
        remarks = st.text_area("Remarks")
        submitted = st.form_submit_button("Add Property")
        if submitted:
            c.execute("INSERT INTO Properties (OwnerName, Contact, Type, Location, Size, AskingPrice, Status, BrokeragePercent, DateListed, Remarks) VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (owner, contact, ptype, location, size, price, status, brokerage, str(datelisted), remarks))
            conn.commit()
            st.success("Property added successfully!")

    st.subheader("Property List")
    df = pd.read_sql("SELECT * FROM Properties", conn)
    st.dataframe(df)

# ----------------------
# Deals
# ----------------------
elif choice == "Deals":
    st.header("🤝 Deals Management")

    customers = pd.read_sql("SELECT CustomerID, Name FROM Customers", conn)
    properties = pd.read_sql("SELECT PropertyID, Location FROM Properties", conn)

    with st.form("add_deal"):
        cust_id = st.selectbox("Customer", customers.apply(lambda x: f"{x['CustomerID']} - {x['Name']}", axis=1))
        prop_id = st.selectbox("Property", properties.apply(lambda x: f"{x['PropertyID']} - {x['Location']}", axis=1))
        ttype = st.selectbox("Transaction Type", ["Sale", "Rent"])
        date = st.date_input("Date")
        value = st.number_input("Deal Value", min_value=0.0)
        brokerage = st.text_input("Brokerage %", value="2%")
        brokerage_amt = value * 0.02
        status = st.selectbox("Status", ["Ongoing", "Closed"])
        pay = st.text_area("Payment Schedule")
        submitted = st.form_submit_button("Add Deal")
        if submitted:
            cid = int(cust_id.split(" - ")[0])
            pid = int(prop_id.split(" - ")[0])
            c.execute("INSERT INTO Deals (CustomerID, PropertyID, TransactionType, Date, Value, BrokeragePercent, BrokerageAmount, Status, PaymentSchedule) VALUES (?,?,?,?,?,?,?,?,?)",
                      (cid, pid, ttype, str(date), value, brokerage, brokerage_amt, status, pay))
            conn.commit()
            st.success("Deal added successfully!")

    st.subheader("Deals List")
    df = pd.read_sql("SELECT * FROM Deals", conn)
    st.dataframe(df)
