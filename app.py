from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug import secure_filename
import classifer as classifier
import math
import pickle
import time
import bokeh_example as bokeh

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

@app.route('/appconcept')
def app_concept():
	return render_template('appconcept.html')

@app.route('/allafamiglia')
def alla_famiglia():
	return render_template('Alla_Famiglia.html')

@app.route('/goldenbuddha')
def golden_buddha():
	return render_template('Golden_Buddha.html')

@app.route('/pizzaparma')
def pizza_parma():
	return render_template('Pizza_Parma.html')

@app.route('/maxsalleghenytavern')
def maxs_allegheny_tavern():
	return render_template('Maxs_Allegheny_Tavern.html')

@app.route('/tasteofindia')
def taste_of_india():
	return render_template('Taste_of_India.html')

@app.route('/originaloysterhouse')
def original_oyster_house():
	return render_template('Original_Oyster_House.html')

@app.route('/pagedairymart')
def page_dairy_mart():
	return render_template('Page_Dairy_Mart.html')

@app.route('/phominh')
def pho_minh():
	return render_template('Pho_Minh.html')

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
      bokeh_result = bokeh.func()
      return render_template('upload.html', guess_data=guess_data_arr, actual_data=actual_data_arr, bokeh_div = bokeh_result[1]['Blue'], bokeh_script=bokeh_result[0])
      
if __name__ == "__main__":
    app.run(debug=True)