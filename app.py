from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug import secure_filename
import classifer as classifier
import multiclassifier as multiclassifier
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

@app.route('/appconceptbusinesses')
def app_concept_businesses():
	return render_template('appconceptbusinesses.html')

@app.route('/appconceptusers')
def app_concept_users():
	return render_template('appconceptusers.html')

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

@app.route('/86lPnxq14I4n2STeK07FEw')
def user1():
	return render_template("86lPnxq14I4n2STeK07FEw.html")

@app.route('/iTmWHtltCtk0Gm55AOxrUA')
def user2():
	return render_template("iTmWHtltCtk0Gm55AOxrUA.html")

@app.route('/nEYPahVwXGD2Pjvgkm7QqQ')
def user3():
	return render_template("nEYPahVwXGD2Pjvgkm7QqQ.html")

@app.route('/Q3fFv_ft17OyV-NRF1iQxw')
def user4():
	return render_template("Q3fFv_ft17OyV-NRF1iQxw.html")

@app.route('/q7MrNVt1FE23rwtWmPYWHg')
def user5():
	return render_template("q7MrNVt1FE23rwtWmPYWHg.html")

@app.route('/So32N7bSbUd1RwhFtI6jTQ')
def user6():
	return render_template("So32N7bSbUd1RwhFtI6jTQ.html")

@app.route('/WzaaorVCmUTQvu4mScunNg')
def user7():
	return render_template("WzaaorVCmUTQvu4mScunNg.html")

@app.route('/zk0SnIEa8ju2iK0mW8ccRQ')
def user8():
	return render_template("zk0SnIEa8ju2iK0mW8ccRQ.html")

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

@app.route('/classifiercomparison')
def classifiercomparison():
   return render_template('classifiercomparison.html', mse_arr=None, me_arr=None)

@app.route('/classifiercomparitor', methods=['GET', 'POST'])
def classifiercomparitor():
   mse_arr = []
   me_arr = []
   labels = []

   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
      multi_classifier_obj = multiclassifier.main(f.filename)
      len(multi_classifier_obj)
      print('file uploaded successfully')
      for obj in multi_classifier_obj:
      	print("MSE")
      	print(obj.mse)
      	labels.append(obj.process_func_str)
      	mse_arr.append(obj.mse)
      	me_arr.append(obj.me)

      	print (mse_arr[0:5])
      
      print(labels)
      return render_template('classifiercomparison.html', labels=labels, mse_arr_1=mse_arr[0:5], mse_arr_2=mse_arr[5:], me_arr_1=me_arr[0:5], me_arr_2=me_arr[5:])

if __name__ == "__main__":
    app.run(debug=True)