import streamlit as st
import pandas as pd
from datetime import datetime

DATA_PATH = "data/applications.csv"

def load_data():
    if st.session_state.get("data_loaded", False):
        return st.session_state["df"]
    try:
        df = pd.read_csv(DATA_PATH)
        df["Applied Date"] = pd.to_datetime(df["Applied Date"], format="mixed", errors="coerce")
        df["Follow Up Date"] = pd.to_datetime(df["Follow Up Date"], format="mixed", errors="coerce")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Company", "Position", "Status", "Applied Date", "Follow Up Date", "Notes"])
    st.session_state["df"] = df
    st.session_state["data_loaded"] = True
    return df

def save_data(df):
    df.to_csv(DATA_PATH, index=False)
    st.session_state["df"] = df  # Keep session state updated

st.set_page_config("Job Application Tracker", layout="wide")
st.title("📌 Job Application Tracker")

df = load_data()

with st.expander("➕ Add New Application"):
    company = st.text_input("Company")
    position = st.text_input("Position")
    status = st.selectbox("Status", ["Applied", "Interview", "Offer", "Rejected"])
    applied_date = st.date_input("Applied Date", value=datetime.today())
    follow_up_date = st.date_input("Follow-Up Date")
    notes = st.text_area("Notes")

    if st.button("Add Application"):
        new_row = pd.DataFrame([{
            "Company": company,
            "Position": position,
            "Status": status,
            "Applied Date": pd.to_datetime(applied_date),
            "Follow Up Date": pd.to_datetime(follow_up_date),
            "Notes": notes
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        
        df["Applied Date"] = pd.to_datetime(df["Applied Date"], format="mixed", errors="coerce")
        df["Follow Up Date"] = pd.to_datetime(df["Follow Up Date"], format="mixed", errors="coerce")
        
        save_data(df)
        st.success("Application added successfully!")
        st.rerun()

st.subheader("📋 Your Applications")
filter_status = st.multiselect("Filter by Status", df["Status"].unique(), default=df["Status"].unique())
filtered_df = df[df["Status"].isin(filter_status)]
st.dataframe(filtered_df.sort_values(by="Applied Date", ascending=False), use_container_width=True)

st.subheader("⏰ Follow-Up Reminders")
today = pd.Timestamp(datetime.today().date())
df["Follow Up Date"] = pd.to_datetime(df["Follow Up Date"], format="mixed", errors="coerce").dt.normalize()
reminders = df[df["Follow Up Date"] == today]

if not reminders.empty:
    st.warning("You have follow-ups today!")
    st.dataframe(reminders)
else:
    st.info("No follow-ups for today.")
