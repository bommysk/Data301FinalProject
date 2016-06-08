from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug import secure_filename
import classifer as classifier
import math
import pickle
import time

app = Flask(__name__)

app.secret_key = 'some_secret'

classifier_obj = None

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/aboutus')
def aboutus():
    return render_template("aboutus.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/reviewinterface')
def review_interface():
	return render_template('reviewinterface.html')

@app.route('/handlereview', methods=['POST'])
def my_form_post():
	classifier_obj = pickle.load( open( "save.p", "rb" ) )
	print("classifier object")
	print(classifier_obj)
	review_text = request.form['review_text']
	print(review_text)
	sample_entry = classifier.Entry(review_text, -1, classifier.process_sentiment_score)
	print(sample_entry)

	guess = classifier_obj.classify(sample_entry.get_tuple()[0])
	print("GUESS: " + str(guess))

	if guess > 5:
	    guess = 5
	elif guess < 1:
	    guess = 1
	else:
	    guess = round(guess)

	return str(guess)

@app.route('/upload')
def upload():
   return render_template('upload.html')

@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
      classifier_obj = classifier.main(f.filename)
      print('file uploaded successfully')
      return redirect(url_for('upload'))
      
if __name__ == "__main__":
    app.run(debug=True)