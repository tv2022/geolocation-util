import requests
import sys
import re

COUNTRY_CODE = "US"
COORDS_BY_LOCATION_ENDPOINT = "http://api.openweathermap.org/geo/1.0/direct"
CORDS_BY_ZIPCODE_ENDPOINT = "http://api.openweathermap.org/geo/1.0/zip"
API_KEY = "f897a99d971b5eef57be6fafa0d83239"

def is_valid_zip_code(zip_code: str) -> bool:
	
	return bool(re.fullmatch(r"^\d{5}$", zip_code))

def fetch_coordinates_by_zip(zip_code: str) -> dict:
	response = requests.get(f"{CORDS_BY_ZIPCODE_ENDPOINT}?zip={zip_code}&appid={API_KEY}")
	return response.json() if response.status_code == 200 else {}

def fetch_coordinates_by_location(city: str, state: str = "") -> dict:
	url = f"{COORDS_BY_LOCATION_ENDPOINT}?q={city},{state},{COUNTRY_CODE}&limit=5&appid={API_KEY}"
	response = requests.get(url)
	return response.json() if response.status_code == 200 else {}

def print_location_details(item: str, details: dict):
	print(f"\033[32m\nDetails of location/Zipcode: \033[1m{item}\033[0m")
	if 'state' in details:
		print(f"City: {details['name']}, Latitude: {details['lat']}, Longitude: {details['lon']}, State: {details['state']}, Country: {details['country']}\n")
	else:
		print(f"City: {details['name']}, Latitude: {details['lat']}, Longitude: {details['lon']}, Country: {details['country']}\n")
  	

def process_location(item: str):
	orginal = item
	item = format_input(item)
	print(f"\033[1mProcessing Location/Zipcode: \033[0m{orginal}")
	if is_valid_zip_code(item):
		data = fetch_coordinates_by_zip(item)
	else:

		# Split the location into city and state (if provided)
		if "," in item and item.count(",") == 1:
			city, state = item.split(",")
		else:
			# Assume the value given is always city name to get multple results. 
			city=item
			state=""
		
		data = fetch_coordinates_by_location(city, state)
	
	if isinstance(data, list) and len(data) >= 1:
		# If multiple results are returned, take the first result
		if len(data) > 1:
			print("\033[1mReturned more than one result, taking first result.\033[0m")
		details = data[0]
	elif isinstance(data, dict) and len(data) > 0:
		details = data
	else:
		print(f"\033[38;5;196mNo data found for given location/Zipcode: {orginal}. Correct the input and try again!\033[0m\n")
		return
	print_location_details(orginal, details)

def format_input(input: str) -> str:
	input = input.strip()
	return re.sub(r',+', ',', input)

def remove_duplicates(locations: dict) -> dict:
	unique_values = {}
	seen_values = set()

	for k, v in locations.items():
		if k.lower() not in seen_values:
			unique_values[k] = k
			seen_values.add(k.lower())
	return unique_values

def main():
	args = sys.argv
	if len(args) < 2:
		print("\033[38;5;196mProvide at least one commandline argument, either location or Zipcode\033[0m")
		print('Examples: \n\tpython3 geolocation_util.py "75035" "Madison, WI"')
		return
	locations = args[1:]
	locations = dict.fromkeys(locations)
	locations = remove_duplicates(locations)

	print("\n============================================================================")
	for count, item in enumerate(locations, 1):
		if len(item) !=0:
			print(f"{count}. ", end="")
			process_location(item)
	
	print("\033[1m\nDONE PROCESSING \033[0m\n")
	print("============================================================================")

if __name__ == "__main__":
	main()
