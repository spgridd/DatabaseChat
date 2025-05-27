import streamlit as st
from data_generation import main as data_page
from talk_to_data import main as talk_page


def main():
    st.set_page_config(layout="wide")
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Page", ("Data Page", "Talk to Data"), index=0, label_visibility="hidden")
    ddl = st.session_state.get("DDL_SCHEMA")
    df = st.session_state.get("CURRENT_DF")

    if page == "Data Page":
        data_page()
    elif page == "Talk to Data":
        talk_page()


if __name__ == "__main__":
    main()
