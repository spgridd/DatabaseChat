import streamlit as st
import pandas as pd
import json
import logging
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from architecture.chat_client import ChatClient

load_dotenv()

dummy_data = {
    "Date": pd.date_range(start="2023-01-01", periods=5, freq="D"),
    "Customer": ["Alice", "Bob", "Charlie", "Diana", "Ethan"],
    "Product": ["Widget A", "Widget B", "Widget A", "Widget C", "Widget B"],
    "Quantity": [3, 5, 2, 1, 4],
    "Price": [19.99, 24.99, 19.99, 29.99, 24.99],
    "Total": [59.97, 124.95, 39.98, 29.99, 99.96]
}

logging.basicConfig(level=logging.INFO)

@st.cache_data
def convert_for_download(tables):
    return json.dumps(tables, indent=2)

def main():
    st.title("DatabaseChat")

    if "chat" not in st.session_state:
        st.session_state.chat = ChatClient()

    chat = st.session_state.chat
    
    # Container to generate the data
    with st.container(border=True):
        # Generate prompt input
        generate_input = st.text_input(label="Prompt", placeholder="Enter your prompt here...")

        # File uploader
        ddl_file = st.file_uploader("Choose a DDL schema file", type=["sql", "ddl", "txt"])

        if ddl_file:
            st.session_state.ddl_schema = ddl_file.read().decode("utf-8")
            st.success("DDL schema uploaded successfully.")

        st.markdown("**Advanced Parameters**")
        col_temp, col_tokens = st.columns([1, 1])
        with col_temp:
            temperature = st.slider("Temperature", 0.0, 1.0, 0.5)
        with col_tokens:
            max_tokens = st.number_input("Max Tokens", 1, 8192, 1000)

        # Generate Button
        if st.button("Generate", use_container_width=False):
            if "ddl_schema" not in st.session_state:
                st.warning("Please upload a DDL schema first.")
            else:
                with st.spinner("Generating for all tables..."):
                    response = chat.generate_data(
                        prompt=generate_input,
                        ddl_schema=st.session_state.ddl_schema,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    try:
                        logging.info(f"\nRESPONSE:\n{response}\n")
                        decoded = json.loads(response)
                        logging.info(f"\nDECODED:\n{decoded}\n")
                        st.session_state.last_response = decoded
                    except json.JSONDecodeError as e:
                        st.error("Response was too long! Increase Max Tokens or simplify your prompt")
                        st.session_state.last_response = None
                        logging.error(f"JSON decode error: {e}")
                    except TypeError as e:
                        st.error("Unfortunately I can't help you with this issue.")
                        st.session_state.last_response = None

                        

    # Container to display and edit dfs
    with st.container(border=True):
        # DataFrame Visualization
        if "last_response" in st.session_state and st.session_state.last_response:
            if st.session_state.last_response.get("data"):
                table_names = list(st.session_state.last_response["data"].keys())

                col_text, col_download, col_selectbox = st.columns([6, 2, 1])
                with col_selectbox:
                    selected_table = st.selectbox("", options=table_names)
                
                with col_download:
                    file_to_save = convert_for_download(st.session_state.last_response)

                    st.download_button(
                        label="Download",
                        data=file_to_save,
                        file_name="data.json",
                        mime="application/json",
                        icon=":material/download:",
                    )

                with col_text:
                    st.subheader("Data preview")
                    
                if selected_table:
                    df = pd.DataFrame(st.session_state.last_response["data"][selected_table])
                    st.dataframe(df, use_container_width=True)
        else:
            st.subheader("Data preview")
            all_dataframes = []
            dummy_df = pd.DataFrame(dummy_data)
            all_dataframes.append(dummy_df)
            st.dataframe(dummy_df, use_container_width=True)
            st.write("*Dummy data")
        
        col_input, separator, col_button = st.columns([7, 0.25, 3])
        # Edit df input
        with col_input:
            edit_input = st.text_input(label="Quick edit", placeholder="Enter quick edit instructions...", label_visibility='hidden')

        # Submit button
        with col_button:
            st.markdown("")
            st.markdown("")
            if st.button("Submit", use_container_width=True):
                if edit_input:
                    if "last_response" in st.session_state:
                        with st.spinner("Processing your query..."):
                            response = chat.edit_data(
                                prompt=edit_input,
                                dataframes=st.session_state.last_response,
                                temperature=temperature,
                                max_tokens=max_tokens
                            )
                            try:
                                decoded = json.loads(response)
                                st.session_state.last_response = decoded
                            except json.JSONDecodeError as e:
                                st.error("Response was too long! Increase Max Tokens param or simplify your prompt")
                                st.session_state.last_response = None
                                logging.error(f"JSON decode error: {e}")
                            except TypeError as e:
                                st.error("Unfortunately I can't help you with this issue.")
                                st.session_state.last_response = None
                else:
                    st.warning("Please enter a question.")

    with st.container():
        if "last_response" in st.session_state and st.session_state.last_response:
            if st.session_state.last_response.get("data"):
                if st.button("Save locally"):
                    table_names = list(st.session_state.last_response["data"].keys())
                    user = os.getenv("POSTGRESQL_USER")
                    password = os.getenv("POSTGRESQL_PASSWORD")
                    db = os.getenv("POSTGRESQL_DB")
                    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@localhost:5432/{db}")
                    
                    for table_name in table_names:
                        df = pd.DataFrame(st.session_state.last_response["data"][table_name])
                        if not df.empty:
                            df.to_sql(table_name, engine, if_exists="replace", index=False)
                            st.success(f"Saved table: {table_name}")
                        else:
                            st.warning(f"Table {table_name} is empty and was skipped.")




if __name__ == "__main__":
    main()
