def create_confusion_matrix(reviews, classifier):
	# List of classifications (1-5 star reviews)
	classes = [1,2,3,4,5]

	# Confusion matrix
	# One row and one column per class.  Initialized to zero.
	#
	#              ACTUAL
	#       [ 0 , 0 , 0 , 0 , 0 ]
	#       [ 0 , 0 , 0 , 0 , 0 ]
	# GUESS [ 0 , 0 , 0 , 0 , 0 ]
	#       [ 0 , 0 , 0 , 0 , 0 ]
	#       [ 0 , 0 , 0 , 0 , 0 ]
	matrix = [[0] * len(classes) for _ in xrange(len(classes))]

	# Iterate through reviews.
	# For each review, run it through the classifier to get the guess.
	# Update the confusion matrix according to the guess and the answer.
	for review in reviews:
	    # this should get the guess from the classifier
	    guess = classifier.classify(review)
	    
	    # this should access the correct answer
	    actual = review.rating
	    
	    # Update the matrix using indices from the class list.
	    matrix[classes.index(guess)][classes.index(actual)] += 1

	return matrix