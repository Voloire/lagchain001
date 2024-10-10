import streamlit as st
from langchain import OpenAI, SQLDatabase, SQLDatabaseChain
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import tempfile
import os

# Set up Streamlit app
st.title("SQLite Database Explorer")

# File uploader for SQLite database
uploaded_file = st.file_uploader("Choose a SQLite database file", type="db")

if uploaded_file is not None:
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    # Create SQLAlchemy engine
    engine = create_engine(f'sqlite:///{tmp_file_path}')

    # Create LangChain SQLDatabase object
    db = SQLDatabase(engine)

    # Set up OpenAI language model
    llm = OpenAI(temperature=0, verbose=True)

    # Create SQLDatabaseToolkit
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    # Create SQL agent
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True
    )

    # User input for natural language query
    user_input = st.text_input("Enter your natural language query:")

    if user_input:
        try:
            # Run the agent to get the SQL query
            result = agent.run(user_input)
            st.write("Result:", result)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    # Clean up temporary file
    os.unlink(tmp_file_path)
