'''
CS432 Programming Assignment 1
ProxyServer.py: a simple python-based proxy server using the socket library with page caching

Based on starting code, modified to make it more readable.
TEST WITH FIREFOX!
Added bypass for favicon.ico for "proper" Chrome handling.

Usage:
"python ProxyServer.py server_ip"
[server_ip] : IP Address of Proxy Server

Then open up a browser and visit the desired website as follows:
server_ip:5000/www.website.com/subdomain

CURRENT PROBLEMS
Websites with external .css and .js files do not transmit properly, the client only receives HTML files.
Slow

Author: Calvin Stewart
Email: cstewar2@uoregon.edu
'''

from socket import *
import sys
import os

def main():
    # check for the IP in argv
    if len(sys.argv) <= 1:
        print('''
              Usage : "python ProxyServer.py server_ip"
              [server_ip] : IP Address of Proxy Server
              ''')
        sys.exit(2)

    # define the server IP and port from argv
    SERVER = sys.argv[1] # localhost resolves to 127.0.0.1
    PORT = 5000 # arbitrary

    # create a server socket, bing it to a port and start listening
    tcpSerSock = socket(AF_INET, SOCK_STREAM) # Init socket
    tcpSerSock.bind((SERVER, PORT)) # Bind socket to port
    tcpSerSock.listen(1) # Listen for page requests

    # while the socket is open, keep receiving requests
    while tcpSerSock:
        # start receiving data from the client
        print("[STARTUP] Ready to accept requests")
        tcpCliSock, addr = tcpSerSock.accept() # accept a request from client
        print(f"[CONN] Received connection from: {addr}")
        message = tcpCliSock.recv(8190) # ~8KB
        print(f"[MESSAGE] Message received: \n{message}")

        # Extract hostname and filename from the message
        fullURL = message.split()[1][1:].decode() # decode URL into utf-8
        if fullURL == "favicon.ico":
            continue
        print(f"[INFO] URL: {fullURL}")
        hostname = fullURL.partition('/')[0].replace("www.", "", 1)
        filename = fullURL.partition('/')[2]
        print(f"[INFO] Host: {hostname} File: {filename}")

        fileExist = False
        filetouse = f"./{hostname}{filename}"

        try: # Check to see if the file is in the cache
            print(f"[CACHE] Opening file {filetouse}")
            if not os.path.exists(filetouse):
                raise IOError
            f = open(filetouse, "r")
            outputdata = f.readlines()
            fileExist = True
            print("[CACHE] Cache hit")

            # Proxy finds a cache hit and generates a response
            tcpCliSock.send("HTTP/1.1 200 OK\r\n".encode())
            tcpCliSock.send("Content-Type:text/html\r\n".encode())
            # Send the output data from the cache hit
            for data in outputdata:
                tcpCliSock.send(data.encode())
            print("[CACHE] Read from cache")

        except IOError: # handling if the file isn't cached
            if fileExist == False:
                print("[CACHE] Cache miss")
                # create an external connection socket on the proxy
                c = socket(AF_INET, SOCK_STREAM)
                # hostname already extracted
                try:
                    # connect to the host over port 80
                    c.connect((hostname, 80))
                    print(f"[CONNECT] connecting to {hostname}:80")
                    # create temp file and ask port 80 to write to it
                    fileobj = c.makefile('rwb', 0)
                    fileobj.write(f"GET /{filename} HTTP/1.1\r\nHost: {hostname}\r\nConnection: keep-alive\r\n\r\n".encode())

                    # Create a new file in the cache for the requested file
                    # Also send the response in the buffer to client socket 
                    # and the corresponding file in the cache
                    tmpFile = open(filetouse, "wb")

                    contentLen = -1
                    while contentLen != 0:
                        data = fileobj.readline()
                        if data.split():
                            if data.split()[0] == b'Content-Length:':
                                contentLen = int(data.split()[1]) + 2 # needs the extra two for the \r\n after the header
                                print(f"[INFO] Content Length: {contentLen}")
                            else:
                                if contentLen > 0:
                                    contentLen = contentLen - len(data)

                        else:
                            if contentLen > 0:
                                contentLen = contentLen - len(data)

                        tmpFile.write(data)
                        tcpCliSock.send(data)
                            

                    # close files
                    if tmpFile:
                        tmpFile.close()
                    if fileobj:
                        fileobj.close()

                except Exception as e:
                    print(f"[ERROR] Exception:\n{e}")
                    if tmpFile:
                        tmpFile.close()
                    if fileobj:
                        fileobj.close()
                
                # close connection
                if c:
                    c.close()
            
            else: # something weird happened, no file found
                print("[ERROR] 404: file not found")

        # Close client socket
        tcpCliSock.close()


if __name__ == '__main__':
    main()
