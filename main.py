import requests
import json
import argparse
import logging

def fetch_automatic_ind(degem_nm):
    """
    Fetch the 'automatic_ind' field for a given degem_nm.
    """
    api_url = "https://data.gov.il/api/3/action/datastore_search"
    resource_id = "142afde2-6228-49f9-8a29-9b6c3a0cbe40"  # Secondary datastore ID

    # Query parameters
    filters = {"degem_nm": degem_nm}  # Query by degem_nm
    params = {
        "resource_id": resource_id,
        "limit": 1,
        "filters": json.dumps(filters),  # Properly encode the filters as a JSON string
    }

    try:
        logging.debug(f"Querying API with parameters: {json.dumps(params, ensure_ascii=False, indent=4)}")
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            logging.debug(f"API Response: {json.dumps(data, ensure_ascii=False, indent=4)}")
            records = data.get("result", {}).get("records", [])
            if records:
                return records[0].get("automatic_ind", None)  # Return the 'automatic_ind' field
            else:
                logging.info(f"No matching record found for degem_nm={degem_nm}.")
        else:
            logging.warning(f"Failed to fetch automatic_ind for degem_nm={degem_nm}. HTTP {response.status_code}")
            logging.warning(f"Response: {response.text}")
    except Exception as e:
        logging.error(f"Error fetching automatic_ind: {e}")

    return None  # Return None if the field is not found or an error occurs


def fetch_automatic_ind_batch(degem_nm_list):
    """
    Fetch the 'automatic_ind' field for a batch of degem_nm values.
    """
    api_url = "https://data.gov.il/api/3/action/datastore_search"
    resource_id = "142afde2-6228-49f9-8a29-9b6c3a0cbe40"  # Secondary datastore ID

    # Query parameters
    filters = {"degem_nm": degem_nm_list}  # Query by a list of degem_nm
    params = {
        "resource_id": resource_id,
        "limit": len(degem_nm_list),
        "filters": json.dumps(filters),  # Properly encode the filters as a JSON string
    }

    try:
        logging.debug(f"Querying API with parameters: {json.dumps(params, ensure_ascii=False, indent=4)}")
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            logging.debug(f"API Response: {json.dumps(data, ensure_ascii=False, indent=4)}")
            records = data.get("result", {}).get("records", [])
            return {record.get("degem_nm"): record.get("automatic_ind", None) for record in records}
        else:
            logging.warning(f"Failed to fetch automatic_ind for degem_nm_list={degem_nm_list}. HTTP {response.status_code}")
            logging.warning(f"Response: {response.text}")
    except Exception as e:
        logging.error(f"Error fetching automatic_ind: {e}")

    return {degem_nm: None for degem_nm in degem_nm_list}  # Return None for all if an error occurs


def update_with_automatic_ind(input_file, output_file):
    """
    Update the records in the input JSON file with the 'automatic_ind' field.
    """
    # Load the sorted JSON file
    with open(input_file, "r", encoding="utf-8") as f:
        records = json.load(f)

    if not records:
        logging.info("No records found in the input file.")
        return

    # Track unique degem_nm values to minimize redundant calls
    queried_degem_nm = {}

    # Iterate through the records and fetch 'automatic_ind'
    for record in records:
        degem_nm = record.get("degem_nm")

        # Check if this degem_nm has already been queried
        if degem_nm not in queried_degem_nm:
            # Query the external data source
            automatic_ind = fetch_automatic_ind(degem_nm)
            queried_degem_nm[degem_nm] = automatic_ind  # Cache the result
        else:
            # Use the cached result
            automatic_ind = queried_degem_nm[degem_nm]

        # Update the record with the 'automatic_ind' field
        record["automatic_ind"] = automatic_ind

    # Save the updated records to a new JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

    logging.info(f"Updated records saved to {output_file}")


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="A script with debug and filtering options.")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode for detailed logging.")
    parser.add_argument("--8", action="store_true", help="Filter only records where 'mispar_rechev' has exactly 7 characters.")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Configure logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
        logging.debug("Debug mode is enabled.")
    else:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    # API endpoint
    api_url = "https://data.gov.il/api/3/action/datastore_search"

    # Parameters for the API request
    resource_id = "053cea08-09bc-40ec-8f7a-156f0677aff3"  # Correct resource ID
    chunk_size = 100000  # Number of records to fetch per request
    offset = 0  # Start from the first record

    # List to store filtered records
    filtered_records = []

    # Counter to limit the number of chunks in debug mode
    chunk_counter = 0
    max_chunks = 1 if args.debug else float('inf')  # Process only 1 chunk in debug mode

    while chunk_counter < max_chunks:
        # Fetch a chunk of data
        params = {
            "resource_id": resource_id,
            "limit": chunk_size,
            "offset": offset,
        }
        response = requests.get(api_url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            records = data.get("result", {}).get("records", [])

            # Debug: Print a summary of the response
            if args.debug:
                logging.debug(f"Chunk {chunk_counter + 10}: Fetched {len(records)} records.")
                # Optional: Print the first 5 records as a sample
                if records:
                    logging.debug(f"Sample records: {json.dumps(records[:5], ensure_ascii=False, indent=4)}")

            # Break the loop if no more records are returned
            if not records:
                break

            # Filter records based on the options
            filtered_chunk = [
                {
                    "mispar_rechev": record["mispar_rechev"],
                    "degem_cd": record.get("degem_cd"),  # Include degem_cd
                    "degem_nm": record.get("degem_nm"),  # Include degem_nm
                    "shnat_yitzur": record.get("shnat_yitzur"),  # Include shnat_yitzur
                    "kinuy_mishari": record.get("kinuy_mishari"),  # Include kinuy_mishari
                    "tozeret_nm": record.get("tozeret_nm"),  # Include tozeret_nm
                }
                for record in records
                if "mispar_rechev" in record
                and (len(str(record["mispar_rechev"])) == 8 if args.__dict__["8"] else True)  # Check for 7 characters if --7 is passed
                and str(record["mispar_rechev"])[0:3] == "770"  # Check if '770' starts from the 3rd character
            ]
            filtered_records.extend(filtered_chunk)

            # Print progress
            logging.info(f"Fetched {len(records)} records, {len(filtered_chunk)} matched the filter.")

            # Increment the offset for the next chunk
            offset += chunk_size

            # Increment the chunk counter
            chunk_counter += 1
        else:
            logging.error(f"Failed to retrieve data. HTTP Status Code: {response.status_code}")
            logging.error(f"Response: {response.text}")
            break

    # Remove duplicates based on 'mispar_rechev'
    unique_records = {}
    for record in filtered_records:
        mispar_rechev = record["mispar_rechev"]
        if mispar_rechev not in unique_records:
            unique_records[mispar_rechev] = record

    # Convert the unique records back to a list
    filtered_records = list(unique_records.values())

    # Sort the filtered records by degem_cd, degem_nm, and shnat_yitzur
    filtered_records = sorted(
        filtered_records,
        key=lambda record: (
            record.get("degem_cd", 0),  # Sort by degem_cd (default to 0 if missing)
            record.get("degem_nm", ""),  # Then by degem_nm (default to empty string if missing)
            record.get("shnat_yitzur", 0)  # Finally by shnat_yitzur (default to 0 if missing)
        )
    )

    # Save the sorted records to a JSON file
    plate_numbers_file = "8_plate_numbers_results_sorted.json"
    with open(plate_numbers_file, "w", encoding="utf-8") as f:
        json.dump(filtered_records, f, ensure_ascii=False, indent=4)

    logging.info(f"Sorted records saved to {plate_numbers_file}")

    logging.info(f"Total Filtered Records: {len(filtered_records)}")
    logging.info(f"Filtered records saved to {plate_numbers_file}")

    # Update the records with 'automatic_ind'
    update_with_automatic_ind(plate_numbers_file, "8_full-test-results.json")

if __name__ == "__main__":
    main()