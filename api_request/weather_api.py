import os
import yaml
import requests
from dotenv import load_dotenv

def fetch_data():
    """
    Handles the Extraction phase of the pipeline by interfacing with the Weatherstack API.
    Resolves configuration paths, manages authentication via environment variables,
    and performs error-checked HTTP requests.
    """
    
    # --- PATH RESOLUTION ---
    # Dynamically locate the project root directory to ensure config files are found 
    # whether running locally or inside a Docker container.
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config.yaml")
    env_path = os.path.join(base_dir, ".env")

    # --- SECRET MANAGEMENT ---
    # Injects environment variables from the .env file into the system environment.
    load_dotenv(dotenv_path=env_path)
    
    # --- CONFIGURATION LOADING ---
    # Parses the YAML configuration file for non-sensitive parameters (API URL, target city, units).
    try:
        with open(config_path, "r") as f:
            yaml_data = yaml.safe_load(f)
    except Exception as e:
        print(f"Config Error: {e}")
        return None

    # --- AUTHENTICATION VALIDATION ---
    # Ensures the mandatory API key is present before attempting a network call.
    api_key = os.getenv("WEATHERSTACK_API_KEY")
    if not api_key:
        print("Error: WEATHERSTACK_API_KEY not found in .env file")
        return None

    # --- REQUEST PREPARATION ---
    # Builds the parameter dictionary required by the Weatherstack REST API.
    params = {
        "access_key": api_key,
        "query": yaml_data['api']['city'],
        "units": yaml_data['api']['units']
    }

    print(f"Requesting LIVE weather data for {params['query']}...")
    
    try:             
        # --- EXECUTE LIVE API CALL ---
        # Performs a GET request to the Weatherstack endpoint.
        response = requests.get(yaml_data['api']['base_url'], params=params)
        
        # Validates that the HTTP response code is 200 (Success). 
        # Raises an exception for 4xx (Client) or 5xx (Server) errors.
        response.raise_for_status() 
        data = response.json()
        
        # --- API-LEVEL ERROR HANDLING ---
        # Weatherstack often returns a 200 OK with an internal 'error' object 
        # for logic issues like 'invalid_access_key' or 'quota_exceeded'.
        if "error" in data:
            print(f"API Logic Error: {data['error']['info']}")
            return None

        print("Live data fetched successfully.")
        print(f"Current temperature in {params['query']}: {data['current']['temperature']} Celcius")
        return data

    except requests.exceptions.RequestException as e:
        # Catch-all for network-level failures (DNS issues, connection timeouts, etc.)
        print(f"Network/HTTP Error: {e}")
        return None
    except Exception as e:
        # Catch-all for unexpected logical failures during data processing.
        print(f"Unexpected Error: {e}")
        raise

if __name__ == "__main__":
    # Allows for standalone execution and testing of the extraction module.
    fetch_data()