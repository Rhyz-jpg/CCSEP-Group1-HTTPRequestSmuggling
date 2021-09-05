FROM mitmproxy/mitmproxy
WORKDIR /usr/src/proxyApp
COPY blockAdmin.py blockAdmin.py

RUN apt-get update && apt-get install -y mitmproxy

ENTRYPOINT mitmdump --mode reverse:http://172.17.0.1:8000 -p 8002 -s blockAdmin.py --no-http2




