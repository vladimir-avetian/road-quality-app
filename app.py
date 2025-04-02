import streamlit as st
import os
import random
from datetime import datetime

# Configuration
IMAGE_FOLDER = "images"  # This assumes your images are in ./images/
OUTPUT_FILE = "human_labels.csv"

# Load all images
all_images = [img for img in os.listdir(IMAGE_FOLDER) if img.lower().endswith(('.jpg', '.png', '.jpeg'))]

# Session state for current image pair
if "current_pair" not in st.session_state:
    st.session_state.current_pair = random.sample(all_images, 2)

# UI
st.title("Road Quality Comparison")

img1, img2 = st.session_state.current_pair

st.image(os.path.join(IMAGE_FOLDER, img1), caption="Top Image", width=600)
st.image(os.path.join(IMAGE_FOLDER, img2), caption="Bottom Image", width=600)

st.markdown("### Choose the picture that shows better road quality:")
choice = st.radio("Your choice:", ["Top", "Bottom", "Equal"], index=None)

if st.button("Submit"):
    if choice:
        with open(OUTPUT_FILE, "a") as f:
            f.write(f"{img1},{img2},{choice},{datetime.now()}\n")
        st.session_state.current_pair = random.sample(all_images, 2)
        st.rerun()
    else:
        st.warning("Please select an option before submitting.")
