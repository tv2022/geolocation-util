import pytest
import random
import requests
import sys
import re
from io import StringIO

from geolocation_util import *

# Test case for methods in util.
def test_valid_single_zip_code():
  zip_code = "10001"
  
  data = fetch_coordinates_by_zip(zip_code)
  
  assert isinstance(data, dict)
  assert len(data) > 0
  assert "lat" in data
  assert "lon" in data
  assert data['name'] == "New York"
  assert data['country'] == "US"


def test_invalid_zip_code():
  zip_code = "99999"

  data = fetch_coordinates_by_zip(zip_code)

  assert isinstance(data, dict)
  assert len(data) == 0

def test_empty_value():
  zip_code = ""

  data = fetch_coordinates_by_zip(zip_code)

  assert isinstance(data, dict)
  assert len(data) == 0

def test__value():
  zip_code = ""

  data = fetch_coordinates_by_zip(zip_code)

  assert isinstance(data, dict)
  assert len(data) == 0


def test_valid_city_and_state():
  city_and_state = "Sunnyvale, CA"
  
  data = fetch_coordinates_by_location("Sunnyvale", "CA")

  assert isinstance(data, list)
  assert len(data) > 0
  assert "lat" in data[0]
  assert "lon" in data[0]
  assert data[0]['name'] == "Sunnyvale"
  assert data[0]['state'] == "California"


def test_valid_case_sensitivity():
  city_and_state = "SUNNYvale, ca"
  
  data = fetch_coordinates_by_location("SUNNYvale", "ca")

  assert isinstance(data, list)
  assert len(data) > 0
  assert "lat" in data[0]
  assert "lon" in data[0]
  assert data[0]['name'] == "Sunnyvale"
  assert data[0]['state'] == "California"


def test_valid_state_name_expanded():
  city_and_state = "Irving, Texas"
  
  data = fetch_coordinates_by_location("Irving", "Texas")

  assert isinstance(data, list)
  assert len(data) > 0
  assert "lat" in data[0]
  assert "lon" in data[0]
  assert data[0]['name'] == "Irving"
  assert data[0]['state'] == "Texas"

def test_special_characters_in_names():
  city_and_state = "!#%*San José, CA"
  
  data = fetch_coordinates_by_location("San José", "CA")

  assert isinstance(data, list)
  assert len(data) > 0
  assert "lat" in data[0]
  assert "lon" in data[0]
  assert data[0]['name'] == "San Jose"
  assert data[0]['state'] == "California"



def test_invalid_city_and_state_format():
  location = "New York NY"

  data = fetch_coordinates_by_location(location)
  assert isinstance(data, list)
  assert len(data) == 0


@pytest.mark.parametrize("city, state", [
  ("Frisco", ""),
])
def test_multiple_results(city, state):
  data = fetch_coordinates_by_location(city, state)
  
  assert len(data) > 1
  assert "name" in data[0]
  assert "lat" in data[0]
  assert "lon" in data[0]
  assert data[0]['name'] == "Frisco"

# Test cases for commandline inputs.

def get_recrods_count(result: str) -> int:
  return result.count("Processing Location/Zipcode")

def test_fetch_single_zip_code_commandline(capsys):
  sys.argv = ["geolocation_util", "95035"]
  main()
  res = capsys.readouterr()
  print(res)

  assert "City: Milpitas, Latitude: 37.4352, Longitude: -121.895, Country: US" in res.out
  assert get_recrods_count(res.out) == 1


def test_fetch_multiple_zip_code_commandline(capsys):
  sys.argv = ["geolocation_util", "95035", "75023"]
  main()
  res = capsys.readouterr()
  print(res)

  assert "City: Milpitas, Latitude: 37.4352, Longitude: -121.895, Country: US" in res.out
  assert "City: Plano, Latitude: 33.055, Longitude: -96.7365, Country: US" in res.out
  assert get_recrods_count(res.out) == 2

def test_fetch_single_location_commandline(capsys):
  sys.argv = ["geolocation_util", "Milpitas, CA"]
  main()
  res = capsys.readouterr()
  print(res)

  assert "City: Milpitas, Latitude: 37.4332273, Longitude: -121.8989248, State: California, Country: US" in res.out

  assert get_recrods_count(res.out) == 1


def test_fetch_multiple_location_commandline(capsys):
  sys.argv = ["geolocation_util", "Milpitas, CA", "Chicago, IL"]
  main()
  res = capsys.readouterr()
  print(res)

  assert "City: Chicago, Latitude: 41.8755616, Longitude: -87.6244212, State: Illinois, Country: US" in res.out
  assert "City: Milpitas, Latitude: 37.4332273, Longitude: -121.8989248, State: California, Country: US" in res.out

  assert get_recrods_count(res.out) == 2


def test_fetch_multiple_zip_code_locations_boundary_case_commandline(capsys):
  sys.argv = ["geolocation_util", "Southlake, TX", "95032", "75023", "Tracy, CA", "Mckinney, TX"]
  main()
  res = capsys.readouterr()
  print(res)

  assert "City: Southlake, Latitude: 32.9412363, Longitude: -97.1341783, State: Texas, Country: US" in res.out # first records.
  assert "City: San Jose, Latitude: 37.2417, Longitude: -121.9554, Country: US" in res.out # Zipcode
  assert "City: McKinney, Latitude: 33.1976496, Longitude: -96.6154471, State: Texas, Country: US" in res.out # last record.

  assert get_recrods_count(res.out) == 5


def test_no_input_commandline(capsys):
  sys.argv = ["geolocation_util"]
  main()
  res = capsys.readouterr()
  print(res)

  assert "Provide at least one commandline argument, either location or Zipcode" in res.out

def test_invalid_input_location_commandline(capsys):
  sys.argv = ["geolocation_util", "dummy city"]
  main()
  res = capsys.readouterr()
  print(res)

  assert "No data found for given location/Zipcode: dummy city" in res.out

def test_invalid_input_Zipcode_commandline(capsys):
  sys.argv = ["geolocation_util", "99999"]
  main()
  res = capsys.readouterr()
  print(res)

  assert "No data found for given location/Zipcode: 99999" in res.out

def test_special_characters_in_names_commandline(capsys):
  sys.argv = ["geolocation_util", "San José, CA"]
  main()
  res = capsys.readouterr()
  print(res)

  assert "City: San Jose, Latitude: 37.3361663, Longitude: -121.890591, State: California, Country: US" in res.out


# Commenting out for the sake of performance and rate limit issues.

# def test_large_input_commandline(capsys):
#   cities = [f"{random.choice(['Chicago', 'Austin', 'Seattle', 'Denver', 'Miami'])}, {random.choice(['WI', 'IL', 'TX', 'WA'])}" for _ in range(3000)]

#   sys.argv = ["geolocation_util", "San José, CA"]
#   main()
#   res = capsys.readouterr()
#   print(res)
#   count = res.out.count("Processing Location/Zipcode")
#   assert count == 3000

def test_muliple_locations_valid_invalid_values_commandline(capsys):
  sys.argv = ["geolocation_util", "94086", "Frisco, TX", "99999", "Madison WI"]
  main()
  res = capsys.readouterr()
  print(res)

  assert "City: Sunnyvale, Latitude: 37.3764, Longitude: -122.0238, Country: US" in res.out
  assert "City: Frisco, Latitude: 33.1506744, Longitude: -96.8236116, State: Texas, Country: US" in res.out
  assert re.search("No data found for given location/Zipcode: Madison WI", res.out, re.IGNORECASE)


def test_multiple_input_blank_values_commandline(capsys):
  sys.argv = ["geolocation_util", "", "New Jersy, NJ", "Palo Alto, CA", ""]
  main()
  res = capsys.readouterr()
  print(res)
  count = res.out.count("Processing Location/Zipcode")
  assert count == 2

def test_duplicate_values_case_sensitive_commandline(capsys):
  sys.argv = ["geolocation_util", "", "New Jersy, nj", "Palo Alto, CA", "new Jersy, NJ"]
  main()
  res = capsys.readouterr()
  print(res)
  count = res.out.count("Processing Location/Zipcode")
  assert count == 2

if __name__ == '__main__':
  pytest.main()
