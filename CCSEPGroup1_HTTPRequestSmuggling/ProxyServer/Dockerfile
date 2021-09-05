FROM mitmproxy/mitmproxy
WORKDIR /usr/src/proxyApp
COPY blockAdmin.py blockAdmin.py
#RUN apt-get update && apt-get install -y python3 python3-pip mitmproxy
RUN apt-get update && apt-get install -y mitmproxy
#EXPOSE 8001
#ENTRYPOINT mitmdump --mode reverse:http://172.17.0.1:8000 -p 8002 -s blockAdmin.py --no-http2
#ENTRYPOINT mitmdump --mode reverse:http://host.docker.internal:8000 -p 8002 -s blockAdmin.py --no-http2
#ENTRYPOINT mitmdump --mode reverse:http://0.0.0.0:8000 -p 8002 -s blockAdmin.py --no-http2
ENTRYPOINT mitmdump --mode reverse:http://172.17.0.1:8000 -p 8002 -s blockAdmin.py --no-http2




