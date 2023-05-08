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

#####################################################################
import socket
from urllib.parse import urlencode, quote_plus
import json

def get_ip_geolocation(address):
    # Define the parameters for the request
    parameters = {'fields': 'city,regionName,country,lat,lon,query', 'lang': 'fr'}

    # Encode the parameters
    encoded_parameters = urlencode({k: quote_plus(v) for k, v in parameters.items()})

    # Prepare the HTTP GET request string
    request = f"GET /json/{address}?{encoded_parameters} HTTP/1.1\r\nHost: ip-api.com\r\nConnection: close\r\n\r\n"

    # Create a socket in IPV4 and TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Make a connection to ip-api.com
    s.connect(('ip-api.com', 80))

    # Send request
    s.sendall(request.encode('ascii'))
    raw_reply = b''
    while True:
        data = s.recv(4096)
        if not data:
            break
        raw_reply += data
    s.close()

    # Extract the JSON payload from the HTTP response
    response_str = raw_reply.decode()
    headers, body = response_str.split("\r\n\r\n")
    geolocation_data = json.loads(body)

    return geolocation_data

ip_address = '121.157.24.227'
geolocation_data = get_ip_geolocation(ip_address)
print(geolocation_data)