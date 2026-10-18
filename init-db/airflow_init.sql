-- 1. Create the dedicated Airflow user
CREATE USER airflow_user WITH PASSWORD 'airflow_pass';

-- 2. Create the dedicated Airflow metadata database
-- Assigning the owner here simplifies permissions significantly
CREATE DATABASE airflow_db OWNER airflow_user;

-- 3. Ensure the user has full control over their own DB
GRANT ALL PRIVILEGES ON DATABASE airflow_db TO airflow_user;