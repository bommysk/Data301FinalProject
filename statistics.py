def get_kappa(confusionMatrix):
    if len(confusionMatrix) == 0: return 0.0
    overallTotal = sum(sum(confusionMatrix[row])
                         for row in range(len(confusionMatrix)))

    # Observed Accuracy
    # Sum of agreements over total number
    obs = 0.0
    for index in range(len(confusionMatrix)):
        obs += confusionMatrix[index][index]
    obs /= overallTotal

    # Expected Accuracy
    # For each class:
    #     Mult total classified, divide by overall total
    # Sum together
    # Divide by overall total
    exp = 0
    for index in range(len(confusionMatrix)):
        left = sum(confusionMatrix[index])
        up = sum([confusionMatrix[_][index]
                    for _ in range(len(confusionMatrix))])
        exp += (float(left * up) / overallTotal)
    exp /= overallTotal

    # Kappa
    try: return (obs - exp) / (1 - exp)
    except ZeroDivisionError: return 1.0

def get_FScore(confusionMatrix):
    if len(confusionMatrix) == 0: return 0.0
    overallTotal = sum(sum(confusionMatrix[row])
                         for row in range(len(confusionMatrix)))

    overallScaled = 0.0

    # For each speaker:
    for index in range(len(confusionMatrix)):
        tp = float(confusionMatrix[index][index])
        actual = sum([confusionMatrix[_][index]
                         for _ in range(len(confusionMatrix))])
        proportion = float(actual) / overallTotal

        if tp == 0:
            precision = 0.0
            recall = 0.0
            f = 0.0
        else:
            precision = tp / sum(confusionMatrix[index])
            recall = tp / actual
            f = (2 * precision * recall) / (precision + recall)

        overallScaled += proportion * f

    return overallScaled