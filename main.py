import requests, json, random, time, threading
from datetime import datetime
from flask import Flask, render_template, request, redirect
from google.cloud import vision, storage
import io
import jwt
from jwt import PyJWKClient
from tinydb import TinyDB, Query
import json
import base64
import urllib.parse

app = Flask(__name__, template_folder='frontend')

db = TinyDB('static/db.json')


def detect_text(base64_img):   
    client = vision.ImageAnnotatorClient()
    content = base64.b64decode(base64_img)  

    image_context = vision.ImageContext(
        language_hints=['en-t-i0-handwrit'])


    image = vision.Image(content=content)    
    
    response = client.text_detection(image=image, image_context=image_context)    
    texts = response.text_annotations   
    text_string = ""
    for text in texts:        
      text_string += text.description
 

    return text_string 
        
def upload_to_bucket(base64_img, name):
  storage_client = storage.Client()
  bucket = storage_client.bucket("cac-image-storage")
  blob = bucket.blob(name)
  content = base64.b64decode(base64_img)

  blob.upload_from_string(content, content_type="image/jpeg")

  print(f"{name} with contents {content} uploaded to cac-image-storage.")



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

@app.route('/new_class', methods=['POST'])
def create_class():
  class_name = str(request.json.get("class_name"))
  class_password = str(request.json.get("class_password"))
  teacher_id = str(request.json.get("teacher_id"))
  student_data = request.json.get("student_data")
  print(student_data[1])
  classes_list = db.search(Query().teacher_id == teacher_id)

  for individual_class in classes_list:

    if individual_class['class_name'] == class_name:
      return {
        "Error" : "Classes cannot have the same name"
        }, 400

  db.insert({"teacher_id" : teacher_id, "class_name" : class_name, "class_password" : class_password, "assignments" : [], "student_data" : student_data})
  
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

  assignment_list = individual_class.get("assignments")
  new_assignment_list = assignment_list

  submit_link = "/student/submit/" + urllib.parse.quote(teacher_id, safe='') + "/" + urllib.parse.quote(class_name, safe='') + "/" + urllib.parse.quote(assignment_name, safe='')

  new_assignment_list.append({
    "submit_link" : submit_link,
    "assignment_name" : assignment_name,
    "due_date" : due_date,
    "questions" : answers,
    "scores" : []
  })

  db.update({'assignments': new_assignment_list}, doc_ids=[individual_class.doc_id])

  return "", 201

def render_submit_page():
  print("sus")
  return render_template("submit.html")

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
  student_id = str(request.json.get("student_id"))
  class_password = str(request.json.get("class_password"))
  image_b64 = str(request.json.get("assignment_image"))
  assignment_details = {}
  image_b64 = image_b64.replace("data:image/jpeg;base64,", '')
  number_correct = 0
  number_incorrect = 0
  text_string = detect_text(image_b64)

  individual_class = db.get(Query().fragment({'teacher_id': teacher_id, 'class_name': class_name}))
  assignments = individual_class["assignments"]
  
  for assignment in individual_class["assignments"]:
    if assignment["assignment_name"] == assignment_name:
      assignment_details = assignment

    questions = assignment_details["questions"]

  for question in questions.items():
    if str(question[1]) in text_string:
      number_correct += 1
    else:
      number_incorrect += 1
  
  score = str(number_correct) + "/" + str(number_correct+number_incorrect)
  name = last_name + ", " + first_name

  upload_to_bucket(image_b64, student_id+assignment_name)

  assignment_details["scores"].append({
    "first_name" : first_name,
    "last_name" : last_name,
    "student_id" : student_id,
    "score" : score,
    "unique_url_end" : student_id+assignment_name
  })

  for assignment in assignments:
    if assignment["assignment_name"] == assignment_details["assignment_name"]:
      assignment = assignment_details
  
  db.update({'assignments': assignments}, doc_ids=[individual_class.doc_id])

  return "", 201

@app.route('/change_score')
def change_score():
  teacher_id = str(request.args.get("teacher_id"))
  student_id = str(request.args.get("student_id"))
  assignment_name = str(request.args.get("assignment_name"))
  new_score = str(request.args.get("new_score"))
  class_name = str(request.args.get("class_name"))
  assignment_details = {}

  individual_class = db.get(Query().fragment({'teacher_id': teacher_id, 'class_name': class_name}))
  assignments = individual_class["assignments"]
  
  for assignment in individual_class["assignments"]:
    if assignment["assignment_name"] == assignment_name:
      assignment_details = assignment

  for student in assignment_details["scores"]:
    if student["student_id"] == student_id:
      student["score"] = new_score
  
  for assignment in assignments:
    if assignment["assignment_name"] == assignment_details["assignment_name"]:
      assignment = assignment_details
  
  db.update({'assignments': assignments}, doc_ids=[individual_class.doc_id])

  return "", 201

@app.route('/student/submit/<teacher_id>/<class_name>/<assignment_name>')
def route_submit_pages(teacher_id, class_name, assignment_name):
  individual_class = db.get(Query().fragment({'teacher_id': teacher_id, 'class_name': class_name}))
  assignment_list = individual_class.get("assignments")


  for assignment in assignment_list:
    if assignment["assignment_name"] == assignment_name:

      return render_template("submit.html")
  
  return "", 400
  

if __name__ == '__main__':
    app.run(debug=True)