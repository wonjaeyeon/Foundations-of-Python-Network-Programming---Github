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

import socket # socket for network communication
import ssl # ssl for secure socket layer for security
from urllib.parse import quote_plus # quote_plus for encoding
import json
from urllib.parse import urlencode

# request_text = """\
# GET /search?q={}&format=json HTTP/1.1\r\n\
# Host: ip-api.com\r\n\
# User-Agent: Foundations of Python Network Programming example search4.py\r\n\
# Connection: close\r\n\
# \r\n\
# """

def get_ip_geolocation(address):
    # Define the parameters for the request
    parameters = {'fields': 'city,regionName,country,lat,lon,query', 'lang': 'fr'}

    query_string = urlencode(parameters)

    split_address = address.split('/')

    # Prepare the HTTP GET request string for ip-api/json/121.157.24.227
    request = f"GET /json?fields={parameters['fields']}&lang={parameters['lang']}121.157.24.227 HTTP/1.1\r\nHost: ip-api.com\r\nConnection: close\r\n\r\n"

    # make unencrypted connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # make a connection to ip-api/json/24.48.0.1
    s.connect(('ip-api.com', 80))

    # send request
    s.sendall(request.encode('ascii'))
    raw_reply = b''
    while True:
        data = s.recv(4096)
        if not data:
            break
        raw_reply += data
    # request = raw_reply.decode('utf-8')
    print(request)
    s.close()

    # Extract the JSON payload from the HTTP response
    response_str = raw_reply.decode()
    headers, body = response_str.split("\r\n\r\n")
    geolocation_data = json.loads(body)


    return geolocation_data


if __name__ == "__main__":
    myIPlocation = get_ip_geolocation('ip-api.com/json/121.157.24.227')
    print("City:", myIPlocation["city"])
    print("Region:", myIPlocation["regionName"])
    print("Country:", myIPlocation["country"])
    print("Latitude:", myIPlocation["lat"])
    print("Longitude:", myIPlocation["lon"])
    print("Query:", myIPlocation["query"])