import streamlit as st
from data_generation import main as data_page
from talk_to_data import main as talk_page
from streamlit_option_menu import option_menu
import os
import shutil
import atexit

def cleanup_plots():
    folder = "outputs/generated_plots"
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

def main():
    st.set_page_config(layout="wide")

    with st.sidebar:
        selected = option_menu(
            menu_title="Data Assistant",
            options=["Data Generation", "Talk to Data"],
            icons=["database-fill", "chat-text-fill"],
            menu_icon="back",
            default_index=0,
            styles={
                "container": {
                    "padding": "10px",
                    "background-color": "#E9ECEF",
                },
                "icon": {"color": "#0B5ED7", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "5px 0",
                    "color": "#212529",
                    "--hover-color": "#D6DBE0"
                },
                "nav-link-selected": {
                    "background-color": "#D0E2FF",
                    "color": "#0B5ED7",
                    "font-weight": "bold",
                }
            }
        )

    # Page logic
    if selected == "Data Generation":
        st.title("Data Generation")
        data_page()
    elif selected == "Talk to Data":
        st.title("Talk to Data")
        talk_page()


if __name__ == "__main__":
    atexit.register(cleanup_plots)
    main()
