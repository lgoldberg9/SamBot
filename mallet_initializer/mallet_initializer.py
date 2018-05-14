import sys
import os
import shutil
import zipfile

PATH = '../client/chatbots/'

def main():
    bot_name = sys.argv[1]
    bot_path = PATH + bot_name + '/'

    try:
        zip_ref = zipfile.ZipFile(bot_path + bot_name + '_mallet.zip', 'r')
        zip_ref.extractall('/tmp')
        zip_ref.close()
    except IOError:
        print "Bot does not exist."
        
if __name__ == '__main__':
    main()
