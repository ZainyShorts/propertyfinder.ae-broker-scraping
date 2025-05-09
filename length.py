import json

# Read the JSON file
with open('brokers_data.json', 'r') as file:
    data = json.load(file)

# Get the length of objects inside the list
length_of_objects = len(data)

print(f"Number of objects inside the list: {length_of_objects}")
