'''
CS432 Programming Assignment 1
ProxyServer.py: a simple python-based proxy server using the socket library with page caching

Author: Calvin Stewart
Email: cstewar2@uoregon.edu
'''

from socket import *
import sys


if len(sys.argv) <= 1:
    print(
        'Usage : "python ProxyServer.py server_ip"\n[server_ip] : IP Address of Proxy Server')
    sys.exit(2)


# Create a server socket, bind it to a port and start listening
HOST = sys.argv[1]
PORT = 5000

tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind((HOST, PORT))
tcpSerSock.listen(1)

while True:
    # Start receiving data from the client
    print(f'[INFO] Open on {HOST}')
    tcpCliSock, addr = tcpSerSock.accept()
    print(f'[COMM] Received a connection from: {addr[0]}')
    message = tcpCliSock.recv(8190)
    print(f"[COMM] Received HTTP request:\n{message}")

    # Extract the URL and additional information from the given message
    fullURL = message.split()[1][1:].decode()
    userAgent = message.split()[6].decode()
    print(f"[INFO] Extracted URL: {fullURL}\n[INFO] Extracted Agent: {userAgent}")
    fileExist = "false"
    

    try:
        # Check wether the file exist in the cache
        f = open(fullURL, "r")
        outputdata = f.readlines()
        fileExist = "true"

        # ProxyServer finds a cache hit and generates a response message
        tcpCliSock.send("HTTP/1.1 200 OK\r\n")
        tcpCliSock.send("Content-Type:text/html\r\n")
        # TODO: Generate response from cache

        print(f"[CACHE] Read {fullURL} from cache")


    # Error handling for file not found in cache
    except IOError:
        if fileExist == "false":
            # Create a socket on the proxyserver
            c = socket(AF_INET, SOCK_STREAM)
            hostname = fullURL.split('/')[0]
            filename = fullURL.split('/')[1]
            print(f"[URL] hostname: {hostname}\n[URL] filename: {filename}")

            try:
                # Connect to the socket to port 80
                print(f"[COMM] Connecting to {hostname}")
                c.connect((hostname, 80))

                # Create a temporary file on this socket and ask port 80 for the file requested by the client
                fileobj = c.makefile('rw', encoding='utf-8')
                fileobj.write(f'GET /{filename}')
                #fileobj.write(b'GET /' + bytes(filename) + b' HTTP/1.1\r\nHost: ' + bytes(hostname) + b':' + 80 + b'\r\nUser-Agent: ' + bytes(userAgent) + b'\r\n\r\n')
                # Read the response into buffer
                # TODO

                print("[INFO] Response read into buffer")

                # Create a new file in the cache for the requested file.
                # Also send the response in the buffer to client socket and the corresponding file in the cache
                tmpFile = open(f"./{hostname}/{filename}", "wb")
                # TODO: copy response into tmpFile, pass along, and add to the cache

            except:
                print("[ERR] Illegal request")
                tcpCliSock.send(b'HTTP/1.1 400 Bad Request\n')
                tcpCliSock.send(b'''
                                <html>
                                <body>
                                <h1>400 Bad Request</h1>
                                <p>uh oh!</p>
                                </body>
                                </html>
                                ''')
            
            # Close the connection to the host
            c.close()

        else:
            # HTTP response message for file not found
            tcpCliSock.send(b'HTTP/1.1 404 Not Found\n')
            tcpCliSock.send(b'''
                            <html>
                            <body>
                            <h1>404 Not Found</h1>
                            <p>uh oh!</p>
                            </body>
                            </html>
                            ''')
    
    # keyboard interrupt check to shut down cleanly
    except KeyboardInterrupt:
        if tcpCliSock:
            tcpCliSock.close()
        tcpSerSock.close()

    # shut down client connection after each request
    if tcpCliSock:
        tcpCliSock.close()

    
        
  
