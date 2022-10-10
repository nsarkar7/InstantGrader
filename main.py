import requests, json, random, time, threading
from datetime import datetime
from flask import Flask, render_template, request, redirect
from google.cloud import vision    
import io
import jwt
from jwt import PyJWKClient
from tinydb import TinyDB, Query
import json

app = Flask(__name__, template_folder='frontend')

db = TinyDB('static/db.json')

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
  class_name = str(request.args.get("class_name"))
  class_password = str(request.args.get("class_password"))
  teacher_id = str(request.args.get("teacher_id"))

  classes_list = db.search(Query().teacher_id == teacher_id)

  for individual_class in classes_list:
    print(individual_class)
    if individual_class['class_name'] == class_name:
      return {
        "Error" : "Classes cannot have the same name"
        }, 400

  db.insert({"teacher_id" : teacher_id, "class_name" : class_name, "class_password" : class_password, "assignments" : []})
  
  return "", 201
  
@app.route('/get_classes')
def get_class():
  teacher_id = str(request.args.get("teacher_id"))

  classes_list = db.search(Query().teacher_id == teacher_id)
  return classes_list, 200

@app.route('/new_assignment')
def new_assignment():
  teacher_id = str(request.args.get("teacher_id"))
  class_name = str(request.args.get("class_name"))
  assignment_name = str(request.args.get("assignment_name"))
  due_date = str(request.args.get("due_date"))
  
  individual_class = db.get(Query().fragment({'teacher_id': teacher_id, 'class_name': class_name}))
  individual_class = classes_list[0]

  assignment_list = individual_class.assignments
  new_assignment_list = []

  for assignment in assignment_list:
    new_assignment_list.append(assignment)
  
  new_assignment_list.append({
    "assignment_name" : assignment_name,
    "due_date" : due_date,
    "questions" : {},
    "scores" : {}
  })

  db.update({'assignments': new_assignment_list}, doc_ids=[individual_class.doc_id])
  
  return "", 201

  
  


@app.route('/app')
def main_app():
  return render_template("app.html")


if __name__ == '__main__':
    app.run(debug=True)