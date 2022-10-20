import requests, json, random, time, threading
from datetime import datetime
from flask import Flask, render_template, request, redirect
from google.cloud import vision    
import io
import jwt
from jwt import PyJWKClient
from tinydb import TinyDB, Query
import json
import base64

app = Flask(__name__, template_folder='frontend')

db = TinyDB('static/db.json')


def detect_text2(base64_img):   
    client = vision.ImageAnnotatorClient()
    content = base64.b64decode(base64_img)  

    image_context = vision.ImageContext(
        language_hints=['en-t-i0-handwrit'])


    image = vision.Image(content=content)    
    
    response = client.text_detection(image=image, image_context=image_context)    
    texts = response.text_annotations   
    
    print('Texts:')    
    for text in texts:        
        print('\n"{}"'.format(text.description))        
        
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
  answers = json.loads(str((request.args.get(("answers")))))
  
  individual_class = db.get(Query().fragment({'teacher_id': teacher_id, 'class_name': class_name}))
  print(individual_class)
  print(answers)
  assignment_list = individual_class.get("assignments")
  new_assignment_list = []
  for assignment in assignment_list:
    new_assignment_list.append(assignment)
  
  submit_link = "/student/submit/" + teacher_id + "/" + class_name + "/" + assignment_name

  new_assignment_list.append({
    "submit_link" : submit_link,
    "assignment_name" : assignment_name,
    "due_date" : due_date,
    "questions" : answers,
    "scores" : {}
  })

  db.update({'assignments': new_assignment_list}, doc_ids=[individual_class.doc_id])
  
  return "", 201

def render_submit_page():
  return render_template("submit.html")

def route_submit_pages():
  database = db.all()
  
  for individual_class in database:
    assignments = individual_class["assignments"]
    teacher_id = individual_class["teacher_id"]
    class_name = individual_class["class_name"]

    for assignment in assignments:
      assignment_name = assignment["assignment_name"]
      link = "/student/submit/" + teacher_id + "/" + class_name + "/" + assignment_name

      app.add_url_rule(link, 'render_submit_page', render_submit_page)
    
      


@app.route('/app')
def main_app():
  return render_template("app.html")

@app.route('/submit',  methods=['POST'])
def record_score():
  teacher_id = str(request.json.get("teacher_id"))
  class_name = str(request.json.get("class_name"))
  assignment_name = str(request.json.get("assignment_name"))
  first_name = str(request.json.get("first_name"))
  last_name = str(request.json.get("last_name"))
  class_password = str(request.json.get("class_password"))
  image_b64 = str(request.json.get("assignment_image"))

  image_b64 = image_b64.replace("data:image/jpeg;base64,", '')

  detect_text2(image_b64)



  return "", 201

route_submit_pages()

if __name__ == '__main__':
    app.run(debug=True)