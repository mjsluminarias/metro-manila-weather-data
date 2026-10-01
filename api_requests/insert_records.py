from api_request import fetch_mock_data
import psycopg2

# print(fetch_mock_data())

def connect_to_db():
    print("Connect to the PostgreSQL database...")
    try:
        conn = psycopg2.connect(
            host = "localhost",
            port = 5000,
            dbname = "db",
            user = "db_user",
            password = "db_password"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection failed: {e}")
        raise

def create_table(conn):
    print("Creating table if not exist...")
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS dev;
            CREATE TABLE IF NOT EXISTS dev.raw_weather_data (
                id SERIAL PRIMARY KEY,
                city TEXT,
                temperature FLOAT,
                weather_description TEXT,
                wind_speed FLOAT,
                time TIMESTAMP,
                inserted_at TIMESTAMP DEFAULT NOW(),
                utc_offset TEXT
            );
        """)
        conn.commit()
        print("Table successfully created...")
    except psycopg2.Error as e:
        print(f"Failed to create table: {e}")
        raise

def insert_records(conn, data):
    print("Inserting weather data into the database...")
    weather = data["current"]
    location = data["location"]
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO dev.raw_weather_data (
                city,
                temperature,
                weather_description,
                wind_speed,
                time,
                inserted_at,
                utc_offset
            ) VALUES (%s, %s, %s, %s, %s, NOW(), %s)
        """, (
            location["name"],
            weather["temperature"],
            weather["weather_descriptions"],
            weather["wind_speed"],
            location["localtime"],
            location["utc_offset"]
        ))
        conn.commit()
        print("Data successfully inserted...")
    except psycopg2.Error as e:
        print(f"Error inserting data into the database: {e}")
        raise

data = fetch_mock_data()
conn = connect_to_db()
create_table(conn)
insert_records(conn, data)