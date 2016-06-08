import string
import simplejson as json
import nltk
import re
import os
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
    def __init__(self, text, rating, process_func):
        self.text = text
        self.rating = rating
        self.bag_of_words = process_func(text)

    def get_tuple(self):
        return (self.bag_of_words, self.rating)

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

    for word in text_split():
        for letter in word:
            if letter.isupper():
                capital_word_count += 1

    return {capital_word_count : True}

def process_exclamation_points(text):
    exclamation_point_count = 0

    for word in text_split():
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
        # entry = Entry(json_data["text"], json_data["stars"], process_bigram)
        print("Before Entry Creation")
        entry = Entry(json_data["text"], json_data["stars"], process_function)
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
    y_true = []
    y_pred = []
    data_file = open(json_file)
    # process_functions = [process_bigram, prcess_unigram, process_sentiment_score, process_word_count, \
                         # process_capital_word_count, process_exclamation_points]

    #nltk.classify.DecisionTreeClassifier, 
    #nltk.classify.NaiveBayesClassifier,
    #SklearnClassifier(BernoulliNB())
    process_functions = [process_sentiment_score] #test
    classifiers = [nltk.classify.NaiveBayesClassifier]
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
        for entries_list in entries_lists:
            shuffle(entries_list)
            length = len(entries_list)
            # will want to pass in only a subet of the entries for trianing, 70%
            training = entries_list[:int(length * 0.7)]
            test = entries_list[int(length * 0.7):]
            print()
            print("About to train")
            trained_classifier = train(training, classifier) # make these into methods to get different components for app
            # conf_matrix = confusion_matrix.create_confusion_matrix(test, trained_classifier)

            # print("Resulto: " + str(statistics.get_kappa(conf_matrix)))
            # print(classifier)
            # we are measuring accuracy for each classifier/feature set combination

            classifier_to_return = trained_classifier

            accuracy = 0
            total_classify_count = 0

            for entry in test:
                guess = trained_classifier.classify(entry.get_tuple()[0])

                if guess > 5:
                    guess = 5
                elif guess < 1:
                    guess = 1
                else:
                    guess = round(guess)

                y_pred.append(guess)
                y_true.append(entry.rating)
                # if rating_difference(guess, entry.rating):
                accuracy += (abs(entry.rating - guess))

                # print(entry.text)
                # print("Guess: %s" % guess)
                # print("Answer: %s" % entry.rating)
                # print("")

                total_classify_count += 1

            print()
            print("Feature Set: Sentiment Analysis")
            print(classifier)
            # print(str((accuracy / total_classify_count) * 100) + "%")
            print()
        
        print("Mean Squared Error: " + str(mean_squared_error(y_true, y_pred)))
        print("Mean Error: " + str(accuracy / total_classify_count))
        print("classifier to return")
        print(classifier_to_return)
        return classifier_to_return

if __name__ == "__main__":
    direct = "/Users/shubham.kahal/Downloads/"
    fpath = os.path.join(direct, "yelp_academic_dataset_review.json")
    print(fpath)
    pickle.dump( main(fpath), open( "saveNaiveBayes.p", "wb" ) )
