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
	sample_entry = classifier.Entry(review_text, -1, classifier.process_sentiment_score, None, None)
	print(sample_entry)

	guess = classifier_obj.classify(sample_entry.get_tuple()[0])

	if guess > 5:
	    guess = 5
	elif guess < 1:
	    guess = 1
	else:
	    guess = round(guess)

	return str(guess)

@app.route('/upload')
def upload():

   return render_template('upload.html', guess_data=None, actual_data=None)

@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
      classifier_obj = classifier.main(f.filename)
      guess_counts = classifier_obj[1]
      actual_counts = classifier_obj[2]
      print('file uploaded successfully')
      guess_data_arr = [guess_counts["1Star"], guess_counts["2Star"], guess_counts["3Star"], guess_counts["4Star"], guess_counts["5Star"]]
      actual_data_arr = [actual_counts["1Star"], actual_counts["2Star"], actual_counts["3Star"], actual_counts["4Star"], actual_counts["5Star"]]
      return render_template('upload.html', guess_data=guess_data_arr, actual_data=actual_data_arr)
      
if __name__ == "__main__":
    app.run(debug=True)