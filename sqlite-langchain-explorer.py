import streamlit as st
from langchain_community.llms import OpenAI
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from sqlalchemy import create_engine
import tempfile
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up Streamlit app
st.title("SQLite Database Explorer")

# File uploader for SQLite database
uploaded_file = st.file_uploader("Choose a SQLite database file", type="db")

if uploaded_file is not None:
    try:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        logger.info(f"Temporary file created at: {tmp_file_path}")

        # Create SQLAlchemy engine
        engine = create_engine(f'sqlite:///{tmp_file_path}')
        logger.info("SQLAlchemy engine created")

        # Create LangChain SQLDatabase object
        db = SQLDatabase.from_uri(f'sqlite:///{tmp_file_path}')
        logger.info("LangChain SQLDatabase object created")

        # Set up OpenAI language model
        llm = OpenAI(temperature=0)
        logger.info("OpenAI language model initialized")

        # Create SQLDatabaseToolkit
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        logger.info("SQLDatabaseToolkit created")

        # Create SQL agent
        agent = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True,
            agent_type="zero-shot-react-description"
        )
        logger.info("SQL agent created")

        # User input for natural language query
        user_input = st.text_input("Enter your natural language query:")

        if user_input:
            try:
                # Run the agent to get the SQL query
                result = agent.run(user_input)
                st.write("Result:", result)
            except Exception as e:
                logger.error(f"Error during agent execution: {str(e)}")
                st.error(f"An error occurred while processing your query: {str(e)}")

    except Exception as e:
        logger.error(f"Error during setup: {str(e)}")
        st.error(f"An error occurred during setup: {str(e)}")

    finally:
        # Clean up temporary file
        if 'tmp_file_path' in locals():
            os.unlink(tmp_file_path)
            logger.info(f"Temporary file removed: {tmp_file_path}")

else:
    st.info("Please upload a SQLite database file to begin.")