import streamlit as st
import pandas as pd
import json
from architecture.chat_client import ChatClient

dummy_data = {
    "Date": pd.date_range(start="2023-01-01", periods=5, freq="D"),
    "Customer": ["Alice", "Bob", "Charlie", "Diana", "Ethan"],
    "Product": ["Widget A", "Widget B", "Widget A", "Widget C", "Widget B"],
    "Quantity": [3, 5, 2, 1, 4],
    "Price": [19.99, 24.99, 19.99, 29.99, 24.99],
    "Total": [59.97, 124.95, 39.98, 29.99, 99.96]
}

def main():
    st.set_page_config(layout="wide")
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
                with st.spinner("Generating based on schema..."):
                    response = chat.generate_data(
                        prompt=generate_input,
                        ddl_schema=st.session_state.ddl_schema,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    try:
                        decoded = json.loads(response)
                        st.session_state.last_response = decoded
                    except json.JSONDecodeError as e:
                        st.error("Response was too long! Increase Max Tokens param or simplify your prompt")
                        st.session_state.last_response = None
                        print("JSON decode error:", e)
                        

    # Container to display and edit dfs
    with st.container(border=True):
        # DataFrame Visualization
        if "last_response" in st.session_state and st.session_state.last_response:
            if st.session_state.last_response.get("data"):
                table_names = list(st.session_state.last_response["data"].keys())

                # all_dataframes = []
                # for _, val in st.session_state.last_response["data"].items():
                #     all_dataframes.append(pd.DataFrame(val))

                col_text, col_selectbox = st.columns([6,1])
                with col_selectbox:
                    selected_table = st.selectbox("", options=table_names)
                
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
        
        col_input, separator, col_button = st.columns([7, 0.25, 1])
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
                                print("JSON decode error:", e)
                else:
                    st.warning("Please enter a question.")


if __name__ == "__main__":
    main()
