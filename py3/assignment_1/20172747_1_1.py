# 1. (3 points) Write a Python script for demonstrating "Raw
# Network Conversation." Use the socket library to request
# ip-api JSON endpoint(https://ip-api.com/docs/api:json) to GET
# your IP Geolocation such as city, regionName, country, lat,
# lon.
# parameters = {'fields':'city,regionName,country,lat,lon',
# 'lang':'fr'}
# Hint: Take a reference from Chapter 1, Listing 1-4 (search.py)
# Note: Don't use any other library(such as requests,
# http.client, etc.) for an API request.

import socket # Import socket for network communication
import json # Import json for parsing json data

def get_ip_geolocation(address):
    # Define the parameters for the request
    parameters = {'fields': 'city,regionName,country,lat,lon', 'lang': 'fr'}

    # Split the address into a list
    split_address = address.split('/')

    # Prepare the HTTP GET request string for ip-api/json/121.157.24.227
    request = f"GET /json?{split_address[2]}fields={parameters['fields']}&lang={parameters['lang']} HTTP/1.1\r\nHost: {split_address[0]}\r\nConnection: close\r\n\r\n"

    # Create a socket in IPV4 and TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    # Make a connection to ip-api/json/24.48.0.1
    s.connect(('ip-api.com', 80))

    # Send request
    s.sendall(request.encode('ascii'))

    # Make a variable to store the response
    raw_reply = b''

    # Receive the response
    while True:
        data = s.recv(4096)
        if not data:
            break
        raw_reply += data
    print(request)

    # Close the socket
    s.close()

    # Decode the response into a string
    response_str = raw_reply.decode()
    # Split the response into headers and body
    headers, body = response_str.split("\r\n\r\n")
    # Extract the JSON payload from the HTTP response
    geolocation_data = json.loads(body)


    return geolocation_data


if __name__ == "__main__":
    # Get the geolocation data from ip-api/json/121.157.24.227
    myIPlocation = get_ip_geolocation('ip-api.com/json/121.157.24.227')
    # Print the geolocation data
    print("City:", myIPlocation["city"])
    print("Region:", myIPlocation["regionName"])
    print("Country:", myIPlocation["country"])
    print("Latitude:", myIPlocation["lat"])
    print("Longitude:", myIPlocation["lon"])