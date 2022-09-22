import requests, json, random, time, threading
from datetime import datetime
from flask import Flask, render_template, request, redirect
from google.cloud import vision    
import io
app = Flask(__name__, template_folder='frontend')
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

if __name__ == '__main__':
    app.run(debug=True)