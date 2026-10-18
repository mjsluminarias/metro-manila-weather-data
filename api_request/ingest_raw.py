# api_request/ingest_raw.py
import psycopg2
import os
from api_request.weather_api import fetch_data
from dotenv import load_dotenv   

def connect_db(host, port):  
    """
    Establishes a connection to the PostgreSQL database using environment variables.
    Supports dynamic routing for both local and Docker-containerized environments.
    """
    print(f"Connecting to postgres db at {host}:{port}...")
    try:        
        conn = psycopg2.connect(
            host = host,  
            port = port,  
            dbname = os.getenv("POSTGRES_DB"),
            user = os.getenv("POSTGRES_USER"),
            password = os.getenv("POSTGRES_PASSWORD")
        )        
        print("Connection established successfully.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"Network/Operational Error: {e}")
        return None
    except psycopg2.Error as e:
        print(f"General Database Error: {e}")
        return None

def create_table(conn):
    """
    Ensures the target schema and raw ingestion table exist (Bronze Layer).
    Implements a persistent schema for the Medallion Architecture.
    """
    print("Creating table if not exists...")
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE SCHEMA IF NOT EXISTS dev; 
            CREATE TABLE IF NOT EXISTS dev.raw_weather_data(
                id SERIAL PRIMARY KEY,
                city VARCHAR(100),
                temp FLOAT,
                weather_desc TEXT,
                windspeed FLOAT,
                local_time TIMESTAMP,
                _ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                utc_offset VARCHAR(10)
            );                       
        """)
        conn.commit()
        print("Schema and Table are ready.")
        cur.close()
    except psycopg2.Error as e:
        print(f"Failed to create table: {e}")
        # Rollback transaction to maintain database integrity
        conn.rollback()
        raise

def insert_data(conn, data):
    """
    Parses the JSON response from the weather API and executes the INSERT.
    Maps external API keys to internal database columns.
    """
    print("Inserting data into postgres...")
    try:
        # Extract nested attributes from API JSON payload
        weather = data['current']
        loc = data['location']
        
        city = loc['name']
        temp = weather['temperature']
        desc = weather['weather_descriptions'][0]
        wind = weather['wind_speed']
        local_time = loc['localtime']
        utc_offset = loc['utc_offset']

        cur = conn.cursor()
        cur.execute("""
            INSERT INTO dev.raw_weather_data (
                city, temp, weather_desc, windspeed, local_time, utc_offset
            )           
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (city, temp, desc, wind, local_time, utc_offset))
        
        conn.commit()
        print(f"Data for {city} ingested successfully.")
        cur.close()
        return city, local_time 
        
    except psycopg2.Error as e:
        print(f"Insert failed: {e}")
        conn.rollback()
        raise

def main():
    """
    Execution entry point. Manages environment detection and coordinates 
    the Extract-Load (EL) workflow.
    """
    load_dotenv() 
    
    # Environment Detection: Determines if code is running inside Airflow container or local venv
    is_docker = os.getenv("AIRFLOW_HOME") is not None
    db_host = "db" if is_docker else "localhost"
    db_port = 5432 if is_docker else 5000

    conn = None
    try:
        # Pass dynamically resolved host/port to the connection handler
        conn = connect_db(db_host, db_port) 
        
        if conn:            
            create_table(conn)                        
            
            # Request live weather data from external API
            data = fetch_data()           
            
            # Perform database insertion
            city_name, event_time = insert_data(conn, data)       

    except Exception as e:
        print(f"An error occurred during execution: {e}")
        # Explicitly raise exception to ensure Airflow marks the task as failed
        raise
    finally:
        # Finalize resource cleanup
        if conn:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    main()