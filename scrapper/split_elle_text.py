PATH = './Elle_Woods_Quotes.txt'
ELLE = '* '
ELLE_LENGTH = len(ELLE)
DIR = './elle_quotes/'

with open(PATH) as file:
    content = file.readlines()
    for idx, line in enumerate(content):
        f = open(DIR + str(idx), 'w')
        f.write(line[ELLE_LENGTH:])
        f.close()
