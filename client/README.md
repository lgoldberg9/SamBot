# Chatroom

This folder contains the chatroom and UI python scripts.

To use the chatroom, execute the following command:

> python ./chatroom.py <username> <chatbot>

where <username> is any desired non-empty string, and the chatbot is a
chosen chatbot from a selection.

Currently, we only have one chatbot setup. List of chatbots:
- Sam Rebelsky

To use this chatbot, type in `sam` for the <chatbot> argument.

# Interface
The chabot interface loads with a greeting from the chosen character, and
instructions on how to send messages. The bot sends an inital message to
let the user know that the bot is waiting for a message. Once the user
types in a message to chatbox and clicks 'Enter', the message loads into
the chat screen. The bot then takes a moment to formulate a repsonse, which
is sent as a message, and viewed in the chatbox under the users
message. The UI keeps the entire conversation with the user as a regular
messaging app would do. The user is allowed to ask questions, make
statements, or generally interact with the bot in 80 character
sections. Once the user is satisified with the conversation, and wants to
end the user will enter the command '\quit' to exit the chatbot.
