PATH = './Yoda_QUOTE.txt'
YODA = 'Yoda: '
YODA_LENGTH = len(YODA)
DIR = './yoda_quotes/'

with open(PATH) as file:
    content = file.readlines()
    for idx, line in enumerate(content):
        f = open(DIR + str(idx), 'w')
        f.write(line[YODA_LENGTH:])
        f.close()
