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

import socket # socket for network communication
import ssl # ssl for secure socket layer for security
from urllib.parse import quote_plus # quote_plus for encoding
import json

# request_text = """\
# GET /search?q={}&format=json HTTP/1.1\r\n\
# Host: nominatim.openstreetmap.org\r\n\
# User-Agent: Foundations of Python Network Programming example search4.py\r\n\
# Connection: close\r\n\
# \r\n\
# """

def get_ip_geolocation():
    # Define the parameters for the request
    parameters = {'fields': 'city,regionName,country,lat,lon', 'lang': 'fr'}

    # Prepare the HTTP GET request string
    request = f"GET /json?fields={parameters['fields']}&lang={parameters['lang']} HTTP/1.1\r\nHost: ip-api.com\r\nConnection: close\r\n\r\n"


    # Create a socket and connect to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('ip-api.com', 80))

    # Send the request
    s.sendall(request.encode('ascii'))

    # Receive the response
    response = b""
    while True:
        data = s.recv(1024)
        if not data:
            break
        response += data
    s.close()

    # Extract the JSON payload from the HTTP response
    response_str = response.decode()
    headers, body = response_str.split("\r\n\r\n")
    geolocation_data = json.loads(body)

    return geolocation_data

if __name__ == "__main__":
    geolocation = get_ip_geolocation()
    print("City:", geolocation["city"])
    print("Region Name:", geolocation["regionName"])
    print("Country:", geolocation["country"])
    print("Latitude:", geolocation["lat"])
    print("Longitude:", geolocation["lon"])