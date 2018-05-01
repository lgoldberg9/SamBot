import random


bot_template = "BOT : {0}"
user_template = "USER : {0}"

def hello_name(message):
    bot_message = "Hello:" + message
    return bot_message;

#sends a message to the bot
def send_message(message):
    print(user_template.format(message))
    response = respond(message)
    print(bot_template.format(response))


name = "Greg"
weather = "cloudy"

# Define a dictionary with the predefined responses
# These responses will be scrapped from the literary characters
responses = {
  "what's your name?": [
      "my name is {0}".format(name),
      "they call me {0}".format(name),
      "I go by {0}".format(name)
   ],
  "what's today's weather?": [
      "the weather is {0}".format(weather),
      "it's {0} today".format(weather)
    ],
    "default": ["default message"]
}

def respond(message):
    # Check for a question mark
    if message.endswith("?"):
        # Return a random question
        return random.choice(responses["question"])
    # Return a random statement
    return random.choice(responses["statement"])
