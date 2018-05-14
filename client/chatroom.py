from ui import *
import re
import sys
import numpy as np
import threading
import pandas as pd
from operator import itemgetter
from gensim.utils import simple_preprocess
from gensim.corpora import Dictionary
from gensim.models.wrappers import LdaMallet
from nltk.corpus import stopwords
from random import random, randint
from multiprocessing import Queue, Process, Lock, Condition

CHATTINESS = 0.8
INITIAL_CHATTINESS = 0.95
UI_LOCK = Lock()
QUEUE_WAIT = Condition()
message_queue = Queue()

character_directory = {
    'Sam': ('chatbots/sam/sam_lda_model.mm', 'chatbots/sam/sam_dict.dict', 'chatbots/sam/sam_dominant_topics.csv')
}

def chatbot_thread(bot_name, lda_path, dict_path, dom_path):
    
    # Get the stop words
    stop_words = stopwords.words('english')

    # Load pre-trained modules
    lda = LdaMallet.load(lda_path)
    dictionary = Dictionary.load(dict_path)
    dominant_topics = pd.read_csv(dom_path)

    # Announce bots entrance
    post_message(bot_name, "Hello there!", True)

    # Loop forever until program termination
    while True:
        while message_queue.empty():
            continue

        
        user_message = message_queue.get()
        
        prob_still_chat = min(random(), INITIAL_CHATTINESS)

        # Loop forever to elicit multiple responses to a single query with decreasing probability
        responding = True
        while responding:
            response = get_response(user_message, lda, dictionary, dominant_topics, stop_words)
            post_message(bot_name, response, True)
            if prob_still_chat < CHATTINESS:
                responding = False
            else:
                prob_still_chat *= prob_still_chat            

def get_response(message, model, dictionary, dominant_topics, stop_words):
    query_dominant_topic = get_topic_query(message, model, dictionary, stop_words)
    related_sentences = dominant_topics[dominant_topics['Dominant_Topic'] == query_dominant_topic].reset_index(drop=True)
    return related_sentences.loc[randint(0,len(related_sentences))]['Text']
    
def get_topic_query(message, model, dictionary, stop_words):
    lowered_message = message.lower()
    words = re.findall(r'\w+', lowered_message, flags = re.UNICODE | re.LOCALE)
    
    important_words = [word for word in simple_preprocess(str(words)) if word not in stop_words]
    ques_vec = dictionary.doc2bow(important_words)

    topic_vec = model[[ques_vec]]
    likely_topic = max(topic_vec[0], key=itemgetter(1))[0]
    
    return likely_topic

def post_message(username, message, is_bot):
    global UI_LOCK
    UI_LOCK.acquire()
    try:
        ui_add_message(username, message, is_bot)
    finally:
        UI_LOCK.release()

def send_message(message):
    message_queue.put(message)
    notify_bots()

def notify_bots():
    QUEUE_WAIT.acquire()
    try:
        QUEUE_WAIT.notify_all()
    except RuntimeError:
        pass
    QUEUE_WAIT.release()

def main():
    if len(sys.argv) != 3:
        print("Usage: {} <username> <character>".format(sys.argv[0]))
        exit()

    # Load username and character chat name
    username = sys.argv[1]
    dat_character = sys.argv[2]

    if dat_character not in character_directory:
        print("Character not available: {}".format(dat_character))
        exit()

    lda_path, dict_path, dom_path = character_directory[dat_character]
        
    chatbot = Process(target = chatbot_thread, args = (dat_character, lda_path, dict_path, dom_path))
    
    # Initialize UI with basic text
    ui_init()
    ui_add_message(None, "Type your message and hit <ENTER> to post.", False);

    # Start chatbot process
    chatbot.start()
    
    while True:
        message = ui_read_input()
        if (message == '\\quit'):
            break
        elif (len(message) > 0):
            post_message(username, message, False)
            send_message(message)

    # Exit the program
    RUNNING_THREAD = False
    
    chatbot.terminate()
    ui_shutdown()
    
if __name__ == '__main__':
    main()
