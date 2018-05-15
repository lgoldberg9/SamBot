# LDA Trainer

This folder contains the python scripts needed to train a corpus using a
given a data set. The data set may be fed in as any sort of collection of
documents that has a lower granularity than sentences.

To run the script, you will need to open this workbook using ipython via Jupyter. The script should run out of the box. If you need to change the bot to train, redirect the paths given in the file.

To signal progress, this script will indicate how far along in the process
the script has processed the documents.

When the script has finished, it will output 3 files corresponding to the
corpus, the LDA_model, and the dominant topics table. All three of these
files must be moved to the approrpiate chatbot folder under chatroom.

This script also generates a number of files in /tmp that will need to be
moved out prior to shutting down or logging off the computer (any event
that would trigger /tmp to wipe). These scripts will also have a name
relevant to mallet. Here are a few examples to search for in /tmp:

* corpus.mallet
* corpus.mallet.infer
* corpus.txt
* doctopics.txt
* doctopics.infer
* topickeys.txt
* corpus.txt

After a reboot happens or this script is moved to a separate computer, you
will need to run the mallet_initializer script with the given chatbot to
prepare the chatbot for initialization. Failing to do so will result in
undefined behavior.
