import os
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    # Streamlit Cloud secrets first, then .env / environment variables
    try:
        import streamlit as st
        user     = st.secrets["POSTGRES_USER"]
        password = st.secrets["POSTGRES_PASSWORD"]
        host     = st.secrets["POSTGRES_HOST"]
        port     = st.secrets["POSTGRES_PORT"]
        db       = st.secrets["POSTGRES_DB"]
    except Exception:
        user     = os.getenv('POSTGRES_USER', 'postgres')
        password = os.getenv('POSTGRES_PASSWORD', '')
        host     = os.getenv('POSTGRES_HOST', 'localhost')
        port     = os.getenv('POSTGRES_PORT', '5432')
        db       = os.getenv('POSTGRES_DB', 'postgres')

    encoded_password = quote_plus(password)
    # +psycopg2 forces the driver we actually install
    conn_str = f'postgresql+psycopg2://{user}:{encoded_password}@{host}:{port}/{db}'
    return create_engine(conn_str)

if __name__ == '__main__':
    engine = get_engine()
    print('Connected!')