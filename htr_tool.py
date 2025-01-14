import os
import json
import streamlit as st
import pandas as pd
from PIL import Image
import pyperclip

st.set_page_config(page_title="HTR Annotation Tool", layout='wide')

# session state to track document list and selected document
DATASET_DIR = st.session_state.get("dataset_dir", None)
PDF_LIST = st.session_state.get("pdf_list", None)
SELECTED_PDF = st.session_state.get("selected_pdf", None)
# SELECTED_PAGE = st.session_state.get("selected_page", 0)


DATASET_DIR = "path/to/data_folder"

specialCharacterArray = [
    "श", "ष", "स", "व",
    "त", "ट", "ठ", "द",
    "ड", "ध", "ढ", "छ",
    "न", "ण", "ङ", "त्र",
    "द्य", "ञ", "ज", "ज्ञ",
    "ि", "ी", "ु", "ू",
    "े", "ै", "ो", "ौ",
    "्", "ृ", "ं ", "ँ",
    "ा", "ः",
    "ळ", "ॐ", "ङ्ग", "ऋ", "ॠ",
]

def change_selected(pdf_idx):
    '''
    Function to navigate PDF list to display them
    Args:
        pdf_idx: Index of pdf file from PDF_LIST
    '''

    if pdf_idx >= len(PDF_LIST):
        st.success('This was the last document')
    elif pdf_idx < 0:
        st.warning('This is the first document')
    else:
        SELECTED_PDF = pdf_idx
        st.session_state.selected_pdf = SELECTED_PDF

def update_dataframe(df, csv_path, image_path, value, field):
    df.loc[df['image'] == image_path, field] = value
    df.to_csv(csv_path, index=False)
    print("Updated t0 ", value)
# sidebar to choose dataset dir and list files
with st.sidebar:
    st.header('HTR Annotation Tool')

    if DATASET_DIR:
        st.write("Dataset Directory: ", DATASET_DIR)

        PDF_LIST = [pdf for pdf in os.listdir(
            DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, pdf))]
        st.session_state.pdf_list = PDF_LIST

        if PDF_LIST:
            st.info('PDF FILES')
            for i, pdf in enumerate(PDF_LIST):
                bt_label = ('👉 ' if SELECTED_PDF == i else '') + pdf
                st.button(label=bt_label,
                          key=pdf,
                          on_click=change_selected,
                          args=[i],
                          use_container_width=True)

col1, col2 = st.columns(spec=[0.9, 0.1], gap='small')
if SELECTED_PDF is not None:
    with col1.container(height=750):
        st.write('Selected Document')
        selected_pdf = PDF_LIST[st.session_state.selected_pdf]
        st.write(selected_pdf)
        try:
            image_files = os.listdir(os.path.join(DATASET_DIR, PDF_LIST[SELECTED_PDF]))
            csv_path = os.path.join(DATASET_DIR, selected_pdf, selected_pdf+".csv")
            data = pd.read_csv(csv_path)
            for index, row in data.iterrows():
                img_file = os.path.join(DATASET_DIR, selected_pdf, row["image"])
                img = Image.open(img_file)
                st.write(row['image'])
                st.image(img, width=400)
                isInvalid = st.checkbox(
                    'isInvalid',
                    row["isInvalid"],
                    key=f"check_{index}")
                st.write(f"Target: {row['text']}")
                updated_target = st.text_input(
                    'Updated Target:',
                    value=row["text"],
                    key=index)
                if updated_target != row["text"]:
                    update_dataframe(
                        data,
                        csv_path,
                        row["image"],
                        updated_target,
                        "text")
                if isInvalid != row["isInvalid"]:
                    update_dataframe(
                        data,
                        csv_path,
                        row["image"],
                        isInvalid,
                        "isInvalid")
        except FileNotFoundError:
            st.error('Failed to locate document')

    with col2:
        st.button(
            label='Prev', use_container_width=True,
            type="primary",
            on_click=change_selected, args=[SELECTED_PDF-1])

        st.button(
            label='Next', use_container_width=True,
            type="primary",
            on_click=change_selected, args=[SELECTED_PDF+1])

        # Display special chars as buttons in a grid
        cols = st.columns(5)  # Adjust the number of columns in the grid

        for i, char in enumerate(specialCharacterArray):
            col = cols[i % 5]  # 5 chars per row
            with col:
                st.code(char)

# remove extra space at top of the page
st.markdown("""
        <style>
               .block-container {
                    padding-top: 3.4rem;
                    padding-bottom: 0rem;
                    padding-left: 2rem;
                    padding-right: 2rem;
                }
        </style>
        """, unsafe_allow_html=True)
