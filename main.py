import requests, json, random, time, threading
from datetime import datetime
from flask import Flask, render_template, request, redirect
from google.cloud import vision    
import io
import jwt
from jwt import PyJWKClient
from tinydb import TinyDB, Query

app = Flask(__name__, template_folder='frontend')

db = TinyDB('db.json')

def detect_text(path):   
          
    client = vision.ImageAnnotatorClient()    
    with io.open(path, 'rb') as image_file:
      content = image_file.read()    
    image = vision.Image(content=content)    
    
    response = client.text_detection(image=image)    
    texts = response.text_annotations   
    
    print('Texts:')    
    for text in texts:        
        print('\n"{}"'.format(text.description))        
        vertices = (['({},{})'.format(vertex.x, vertex.y)                    
                    for vertex in text.bounding_poly.vertices])        
        print('bounds: {}'.format(','.join(vertices)))
#detect_text("data/test2.jpg")

@app.route('/')
def homepage():
  return render_template("index.html")


@app.route('/verify')
def verify_google_credentials():
  encoded = str(request.args.get("str"))
  url = "https://www.googleapis.com/oauth2/v3/certs"
  jwks_client = PyJWKClient(url)
  key = jwks_client.get_signing_key_from_jwt(encoded)
  decoded = jwt.decode(encoded, key.key, algorithms=['RS256'], audience="189268090877-v8g6klov9vgs5dehq1ir9vqna5gtbp7n.apps.googleusercontent.com")
  return decoded

@app.route('/new_class')
def create_class():
  id = int(request.args.get("id"))
  name = str(request.args.get("name"))
  

@app.route('/app')
def main_app():
  return render_template("app.html")


if __name__ == '__main__':
    app.run(debug=True)