import requests
import json
import logging

def fetch_filtered_records(resource_id, chunk_size, debug_mode):
    """
    Fetch and filter records from the API based on the 'mispar_rechev' field.
    :param resource_id: The resource ID for the API.
    :param chunk_size: Number of records to fetch per request.
    :param debug_mode: Boolean indicating whether debug mode is enabled.
    :return: List of filtered records.
    """
    api_url = "https://data.gov.il/api/3/action/datastore_search"
    offset = 0
    filtered_records = []
    chunk_counter = 0
    max_chunks = 3 if debug_mode else float('inf')  # Process only 3 chunks in debug mode

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
            if debug_mode:
                logging.debug(f"Chunk {chunk_counter + 1}: Fetched {len(records)} records.")
                if records:
                    logging.debug(f"Sample records: {json.dumps(records[:5], ensure_ascii=False, indent=4)}")

            # Break the loop if no more records are returned
            if not records:
                break

            # Filter records based on the options
            filtered_chunk = [
                {
                    "mispar_rechev": record["mispar_rechev"],
                    "degem_cd": record.get("degem_cd"),
                    "degem_nm": record.get("degem_nm"),
                }
                for record in records
                if "mispar_rechev" in record
                and str(record["mispar_rechev"])[2:5] == "770"  # Check if '770' starts from the 3rd character
            ]
            filtered_records.extend(filtered_chunk)

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
    return list(unique_records.values())