import json

# Input and output file paths
input_file = "full-test-results.json"
output_file = "filtered-results.json"

try:
    # Open and load the JSON file
    with open(input_file, "r") as file:
        data = json.load(file)

    # Check if the data is a list
    if isinstance(data, list):
        # Filter records where automatic_ind == 0
        filtered_data = [record for record in data if record.get("automatic_ind") == 0]

        # Save the filtered data to a new JSON file
        with open(output_file, "w") as file:
            json.dump(filtered_data, file, indent=4)

        print(f"Filtered data has been saved to '{output_file}'.")
    else:
        print("The JSON file does not contain a list of records.")

except FileNotFoundError:
    print(f"Error: The file '{input_file}' was not found.")
except json.JSONDecodeError:
    print(f"Error: The file '{input_file}' is not a valid JSON file.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")