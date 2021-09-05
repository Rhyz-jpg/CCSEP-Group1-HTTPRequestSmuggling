from flask import Flask, request
import requests
app = Flask(__name__)

@app.route("/")
def default():
    print(request.method)
    print(request.headers)
    print(request.data)
    return "You made it to our lovely website\n\n"


@app.route("/admin")
def admin():
    return "Super secret admin content"

@app.route("/page2")
def page2():
    return "page 2"

#if __name__ == "__name__":
 #   app.run(debug=True, host='127.0.0.1', port=8000)
