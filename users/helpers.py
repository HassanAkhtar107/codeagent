from datetime import datetime

def generateRandom(email):
    return str(email) + str(datetime.date(datetime.now()))