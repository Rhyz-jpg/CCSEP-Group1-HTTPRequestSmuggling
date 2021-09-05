from mitmproxy import http

def request(flow):
    print(flow.request.content)
    if '/admin' in flow.request.url:
        flow.response = http.HTTPResponse.make(403, b"For Admins only\n")
    
    #I couldnt get this to work with while using a docker, but the attack still works.
        
