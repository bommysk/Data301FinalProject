import string
import json
import nltk
import re
import os
import pandas as pd
from pprint import pprint
from random import shuffle
from nltk.corpus import stopwords
from nltk.corpus import subjectivity
from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.sentiment.util import *
from nltk.classify import SklearnClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import SVC
import statistics
import confusion_matrix
from sklearn.metrics import mean_squared_error
from math import sqrt
import pickle

class Entry:
    def __init__(self, text, rating, process_func, business_id, user_id):
        self.text = text
        self.rating = rating
        self.bag_of_words = process_func(text)
        self.business_id = business_id
        self.user_id = user_id

    def get_tuple(self):
        return (self.bag_of_words, self.rating)

class ClassifierError:
    def __init__(self, classifier, process_func_str, mse, me):
        self.classifier = classifier
        self.process_func_str = process_func_str
        self.mse = mse
        self.me = me

def get_sentiment_score(sentence):
    score_dict = {}
    sid = SentimentIntensityAnalyzer()
    ss = sid.polarity_scores(sentence)
    for k in sorted(ss):
        # print('{0}: {1}, '.format(k, ss[k]), end='')
        score_dict[k] = ss[k]

    return score_dict

def process_word_count(text):
    return {len(text.split()) : True}

def process_capital_word_count(text):
    capital_word_count = 0

    for word in text.split():
        for letter in word:
            if letter.isupper():
                capital_word_count += 1

    return {capital_word_count : True}

def process_exclamation_points(text):
    exclamation_point_count = 0

    for word in text.split():
        for letter in word:
            if letter == "!":
                exclamation_point_count += 1

    return {exclamation_point_count : True}

def process_sentiment_score(text):
    compound_avg = 0
    negative_avg = 0
    neutral_avg = 0
    positive_avg = 0
    sentence_count = 0
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)

    for sentence in sentences:
        stop = stopwords.words('english')
        split_text = ' '.join(word.strip(string.punctuation) for word in sentence.split() if word not in stop)
        scores_dict = get_sentiment_score(split_text)
        compound_avg += scores_dict["compound"]
        negative_avg += scores_dict["neg"]
        neutral_avg += scores_dict["neu"]
        positive_avg += scores_dict["pos"]
        sentence_count += 1

    return {
        "compound_avg" : compound_avg / sentence_count,
        "negative_avg" : negative_avg / sentence_count,
        "neutral_avg" : neutral_avg / sentence_count,
        "positive_avg" : positive_avg / sentence_count
    }

def process_bigram(text):
    dictionary_bag = {}
    split_text = ' '.join(word.strip(string.punctuation) for word in text.split())

    stop = stopwords.words('english')
    split_text = [word for word in split_text.split() if word not in stop] # take out stoppage words

    for i in range(len(split_text) - 1):
        dictionary_bag[split_text[i] + "_" + split_text[i + 1]] = True

    return dictionary_bag

def process_unigram(text):
    dictionary_bag = {}
    split_text = ' '.join(word.strip(string.punctuation) for word in text.split())

    stop = stopwords.words('english')
    split_text = [word for word in split_text.split() if word not in stop] # take out stoppage words

    for i in range(len(split_text) ):
        dictionary_bag[split_text[i]] = True

    return dictionary_bag

# Create Classifier and return
def train(training_entries, classifier):
    data = [entry.get_tuple() for entry in training_entries]

    return classifier.train(data)

def get_entries(json_arr, process_function):
    entries = []
    counter = 0

    for jsonline in json_arr:
        try:
            json_data = json.loads(jsonline)
        except:
            print("Json Load Error")
            continue
        print("Before Entry Creation")
        entry = Entry(json_data["text"], json_data["stars"], process_function, json_data["business_id"], json_data["user_id"])
        entries.append(entry) # return entries for that particular process function
        print("After Entry Creation " + str(counter))
        counter += 1

    return entries

def rating_difference(rating1, rating2):
    return abs(rating1 - rating2) <= 1

def get_review_rating(trained_classifier, review_text):
    guess = trained_classifier.classify(entry.get_tuple()[0])
    return guess

def main(json_file):
    counter = 1
    proc_counter = 0
    count = 0
    data_file = open(json_file)
    classifier_error_arr = []
    # process_functions = [process_bigram, process_unigram, process_sentiment_score, process_word_count, \
                         # process_capital_word_count, process_exclamation_points]

    #nltk.classify.DecisionTreeClassifier, 
    #nltk.classify.NaiveBayesClassifier,
    #SklearnClassifier(BernoulliNB())
    process_functions = [process_bigram, process_unigram, process_word_count, \
                         process_capital_word_count, process_exclamation_points]
    classifiers = [nltk.classify.NaiveBayesClassifier, nltk.classify.DecisionTreeClassifier]
    entries_lists = []
    
    json_arr = data_file.read().split("\n")

    print("Splitting line")

    # make feature set based on each type of process function, and get entries for each type of process function
    for process_function in process_functions:
        print("In the process of creating entries")
        entries_lists.append(get_entries(json_arr[0:100001], process_function))

    print("Done Creating Entries")

    classifier_to_return = None

    for classifier in classifiers:
        # there is a different entry list for each feature set
        print(classifier)
        proc_counter = 0
        for entries_list in entries_lists:
            y_true = []
            y_pred = []
            review_text = []
            business_ids = []
            user_ids = []
            shuffle(entries_list)
            length = len(entries_list)
            # will want to pass in only a subet of the entries for trianing, 70%
            training = entries_list[:int(length * 0.7)]
            test = entries_list[int(length * 0.7):]
            print()
            print("About to train")

            trained_classifier = train(entries_list, classifier)
            accuracy = 0
            total_classify_count = 0

            for entry in test:
                guess = trained_classifier.classify(entry.get_tuple()[0])

                print("Guess: " + str(guess))

                if guess > 5:
                    guess = 5
                elif guess < 1:
                    guess = 1
                else:
                    guess = round(guess)

                review_text.append(entry.text)
                y_pred.append(guess)
                y_true.append(entry.rating)
                business_ids.append(entry.business_id)
                user_ids.append(entry.user_id)

                accuracy += (abs(entry.rating - guess))

                total_classify_count += 1

            d = {'Review Text': review_text, 'Guess Rating': y_pred, 'Actual Rating': y_true, "Business Id": business_ids, "User Id": user_ids}
            df = pd.DataFrame(data=d)
            pickle.dump( df, open( "reviewDataFrame.p" + str(counter), "wb" ) )
            df_obj = pickle.load( open( "reviewDataFrame.p" + str(counter), "rb" ) )
            counter += 1

            mse = mean_squared_error(y_true, y_pred)
            me = accuracy / total_classify_count
            print("Mean Squared Error: " + str(mean_squared_error(y_true, y_pred)))
            print("Mean Error: " + str(accuracy / total_classify_count))
            classifier_error = ClassifierError(str(classifier.__name__), str(process_functions[proc_counter].__name__), mse, me)
            proc_counter += 1

            print("appending " + str(count))
            count += 1
            classifier_error_arr.append(classifier_error)
   
    print("RETURN LENGTH: " + str(len(classifier_error_arr)))
    return classifier_error_arr

if __name__ == "__main__":
    main("zerodata.json")