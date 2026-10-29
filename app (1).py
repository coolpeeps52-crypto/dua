
import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

st.set_page_config(page_title="City Care Hospital", page_icon="🏥", layout="wide")

DATA_DIR = "data"
PATIENTS_FILE = os.path.join(DATA_DIR, "patients.csv")
DOCTORS_FILE = os.path.join(DATA_DIR, "doctors.csv")
APPOINTMENTS_FILE = os.path.join(DATA_DIR, "appointments.csv")

os.makedirs(DATA_DIR, exist_ok=True)

def load_csv(path, columns):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(columns=columns)

def save_csv(df, path):
    df.to_csv(path, index=False)

patients = load_csv(PATIENTS_FILE, ["patient_id", "name", "age", "gender", "phone", "address", "registered_on"])
doctors = load_csv(DOCTORS_FILE, ["doctor_id", "name", "specialization", "phone", "availability"])
appointments = load_csv(APPOINTMENTS_FILE, ["appointment_id", "patient_id", "doctor_id", "date", "time", "reason", "status"])

menu = st.sidebar.radio("Navigation", ["Dashboard", "Patients", "Doctors", "Appointments"])
st.sidebar.success("City Care Hospital Management System")

if menu == "Dashboard":
    st.title("🏥 City Care Hospital Dashboard")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Patients", len(patients))
    c2.metric("Total Doctors", len(doctors))
    c3.metric("Total Appointments", len(appointments))

    st.subheader("Appointments by Status")
    if not appointments.empty:
        status_counts = appointments["status"].value_counts()
        st.bar_chart(status_counts)
    else:
        st.info("No appointments yet.")

    st.subheader("Recent Patients")
    if not patients.empty:
        st.dataframe(patients.tail(10), use_container_width=True)
    else:
        st.info("No patients registered yet.")

elif menu == "Patients":
    st.title("🧑‍⚕️ Patient Management")

    with st.form("add_patient"):
        st.subheader("Register New Patient")
        name = st.text_input("Full Name")
        age = st.number_input("Age", min_value=0, max_value=120, value=30)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        phone = st.text_input("Phone Number")
        address = st.text_area("Address")
        submitted = st.form_submit_button("Register Patient")

        if submitted:
            if name and phone:
                patient_id = f"P{len(patients) + 1001}"
                new_patient = pd.DataFrame([{
                    "patient_id": patient_id,
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "phone": phone,
                    "address": address,
                    "registered_on": datetime.now().strftime("%Y-%m-%d")
                }])
                patients = pd.concat([patients, new_patient], ignore_index=True)
                save_csv(patients, PATIENTS_FILE)
                st.success(f"Patient registered successfully. ID: {patient_id}")
            else:
                st.error("Please enter the patient name and phone number.")

    st.subheader("Patient Records")
    search = st.text_input("Search by name or patient ID")
    if not patients.empty:
        filtered = patients[
            patients["name"].str.contains(search, case=False, na=False) |
            patients["patient_id"].str.contains(search, case=False, na=False)
        ]
        st.dataframe(filtered, use_container_width=True)
    else:
        st.info("No patient records available.")

elif menu == "Doctors":
    st.title("👨‍⚕️ Doctor Management")

    with st.form("add_doctor"):
        st.subheader("Add New Doctor")
        doctor_name = st.text_input("Doctor Name")
        specialization = st.text_input("Specialization")
        doctor_phone = st.text_input("Phone Number")
        availability = st.text_input("Availability", value="Mon-Fri, 9 AM - 5 PM")
        doctor_submitted = st.form_submit_button("Add Doctor")

        if doctor_submitted:
            if doctor_name and specialization:
                doctor_id = f"D{len(doctors) + 101}"
                new_doctor = pd.DataFrame([{
                    "doctor_id": doctor_id,
                    "name": doctor_name,
                    "specialization": specialization,
                    "phone": doctor_phone,
                    "availability": availability
                }])
                doctors = pd.concat([doctors, new_doctor], ignore_index=True)
                save_csv(doctors, DOCTORS_FILE)
                st.success(f"Doctor added successfully. ID: {doctor_id}")
            else:
                st.error("Please enter doctor name and specialization.")

    st.subheader("Doctor Directory")
    if not doctors.empty:
        st.dataframe(doctors, use_container_width=True)
    else:
        st.info("No doctors added yet.")

elif menu == "Appointments":
    st.title("📅 Appointment Management")

    if patients.empty or doctors.empty:
        st.warning("Register at least one patient and one doctor before booking appointments.")
    else:
        with st.form("book_appointment"):
            st.subheader("Book Appointment")
            patient_option = st.selectbox(
                "Select Patient",
                patients.apply(lambda r: f"{r['patient_id']} - {r['name']}", axis=1)
            )
            doctor_option = st.selectbox(
                "Select Doctor",
                doctors.apply(lambda r: f"{r['doctor_id']} - {r['name']} ({r['specialization']})", axis=1)
            )
            appointment_date = st.date_input("Appointment Date", value=date.today())
            appointment_time = st.time_input("Appointment Time")
            reason = st.text_area("Reason for Visit")
            booked = st.form_submit_button("Book Appointment")

            if booked:
                appointment_id = f"A{len(appointments) + 2001}"
                new_appointment = pd.DataFrame([{
                    "appointment_id": appointment_id,
                    "patient_id": patient_option.split(" - ")[0],
                    "doctor_id": doctor_option.split(" - ")[0],
                    "date": appointment_date.strftime("%Y-%m-%d"),
                    "time": appointment_time.strftime("%H:%M"),
                    "reason": reason,
                    "status": "Scheduled"
                }])
                appointments = pd.concat([appointments, new_appointment], ignore_index=True)
                save_csv(appointments, APPOINTMENTS_FILE)
                st.success(f"Appointment booked successfully. ID: {appointment_id}")

    st.subheader("Appointment Records")
    if not appointments.empty:
        st.dataframe(appointments, use_container_width=True)

        appointment_to_update = st.selectbox(
            "Select appointment to update",
            appointments["appointment_id"]
        )
        new_status = st.selectbox("New Status", ["Scheduled", "Completed", "Cancelled"])
        if st.button("Update Status"):
            appointments.loc[appointments["appointment_id"] == appointment_to_update, "status"] = new_status
            save_csv(appointments, APPOINTMENTS_FILE)
            st.success("Appointment status updated.")
    else:
        st.info("No appointments booked yet.")
