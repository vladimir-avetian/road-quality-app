import streamlit as st
import os
import random
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# === Configuration ===
IMAGE_FOLDER = "images"
BATCH_SIZE = 10
SPREADSHEET_ID = "1bc0rkRjXVkNWGICW_JSYzPLhPvvio3k25-XbEMJqaM0"

# === Load images ===
all_images = [img for img in os.listdir(IMAGE_FOLDER) if img.lower().endswith(('.jpg', '.png', '.jpeg'))]

# === Session state ===
if "current_pair" not in st.session_state:
    st.session_state.current_pair = random.sample(all_images, 2)

if "batch" not in st.session_state:
    st.session_state.batch = []

if "phase" not in st.session_state:
    st.session_state.phase = "labeling"

if "sheet_submitted" not in st.session_state:
    st.session_state.sheet_submitted = False

# === Phase 1: Labeling ===
if st.session_state.phase == "labeling":
    st.markdown("Road Quality Comparison")

    img1, img2 = st.session_state.current_pair

    st.image(os.path.join(IMAGE_FOLDER, img1), caption="Top Image", width=600)
    st.image(os.path.join(IMAGE_FOLDER, img2), caption="Bottom Image", width=600)

    st.markdown("Choose the picture that shows better road quality:")
    choice = st.radio("Your choice:", ["Top", "Bottom", "Equal"], index=None)

    if st.button("Submit"):
        if choice:
            st.session_state.batch.append([img1, img2, choice, str(datetime.now())])

            if len(st.session_state.batch) >= BATCH_SIZE:
                st.session_state.phase = "review"
            else:
                st.session_state.current_pair = random.sample(all_images, 2)
                st.rerun()
        else:
            st.warning("Please select an option before submitting.")

    st.markdown(f"✅ Labeled: {len(st.session_state.batch)} / {BATCH_SIZE}")

# === Phase 2: Review + Auto-Send to Google Sheets ===
elif st.session_state.phase == "review":
    st.title("✅ You labeled 10 image pairs")

    # Send to Google Sheets only once
    if not st.session_state.sheet_submitted:
        try:
            if os.path.exists("credentials.json"):
                # Local mode: use the credentials file
                creds = Credentials.from_service_account_file("credentials.json").with_scopes([
                    "https://www.googleapis.com/auth/spreadsheets"
                ])
            else:
                # Deployed mode: use secrets from Streamlit Cloud
                try:
                    creds_dict = dict(st.secrets["gcp_service_account"])
                    creds = Credentials.from_service_account_info(creds_dict).with_scopes([
                        "https://www.googleapis.com/auth/spreadsheets"
                    ])
                except Exception as e:
                    st.error("❌ No credentials available. Add credentials.json locally or set your secrets on the server.")
                    st.stop()
            client = gspread.authorize(creds)
            sheet = client.open_by_key(SPREADSHEET_ID).sheet1

            for row in st.session_state.batch:
                sheet.append_row(row)

            st.success("✅ Sent to Google Sheets.")
        except Exception as e:
            st.error(f"⚠️ Failed to submit to Google Sheets: {e}")

        st.session_state.sheet_submitted = True

    st.write("Here are your choices:")

    for i, row in enumerate(st.session_state.batch, 1):
        img1, img2, choice, timestamp = row
        st.markdown(f"**{i}.** `{img1}` vs `{img2}` → **{choice}** at {timestamp}")

    if st.button("Start new batch"):
        st.session_state.batch = []
        st.session_state.sheet_submitted = False
        st.session_state.current_pair = random.sample(all_images, 2)
        st.session_state.phase = "labeling"
        st.rerun()
