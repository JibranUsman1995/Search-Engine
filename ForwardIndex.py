import sys
import argparse
import os
import bs4
import re
from nltk import PorterStemmer
from nltk import sent_tokenize, word_tokenize

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title', '!DOCTYPE html']:
        return False
    elif element == '\n':
        return False
    elif element == ' ':
        return False
    elif 'PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN' in element:
        return False
    elif '<div' in element:
        return False
    elif 'Google Analytics 2012' in element:
        return False
    elif 'Include the Omniture common js file for tracking' in element:
        return False


    return True

def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

#Main starting bellow

stopList = open('stoplist.txt', 'r', encoding='utf8', errors='ignore').read()
stopWords = re.findall(r'\w[\w]*', stopList)

totalFiles = len([name for name in os.listdir('C:\\Users\\pc\\PycharmProjects\\IR1\\corpus')])
stemmer = PorterStemmer()

DOCID = 0
TERMID = 0

docFile = open('docids.txt', 'w', errors='ignore')
termFile = open('termids.txt', 'w', errors='ignore')
indexFile = open('doc_index.txt', 'w', errors='ignore')

currentlyTraversed = 0
uniqueTokens = []

for directory in os.walk('C:\\Users\\pc\\PycharmProjects\\IR1\\corpus'):
    for sections in directory:
        for filename in sections:

            tokens = []
            tokens.clear()

            if(len(filename) > 1):

                currentlyTraversed = currentlyTraversed + 1
                DOCID = DOCID+1

                docFile.write(DOCID.__str__())
                docFile.write('\t')
                docFile.write(filename)
                docFile.write('\n')

                fpath = 'corpus/' + filename
                str = open(fpath, 'r', encoding="utf8", errors='ignore').read()

                soup = bs4.BeautifulSoup(str, 'html.parser')
                data = soup.findAll(text=True)
                newData = filter(visible, data)

                sentenceIndex = 0

                for sentence in newData:

                    if(sentenceIndex == 0):
                        sentenceIndex = 1
                        continue

                    words = re.findall(r'\w[\w]*', sentence)
                    for word in words:
                        word = word.lower()

                        if(word not in stopWords):
                            if(len(word) > 1):
                                tokens.append(stemmer.stem(word))

                #print(tokens)
                #print(len(tokens))

                #if(DOCID > 15):
                #    break
            uniqueTokens.extend(tokens)
            uniqueTokens = unique(uniqueTokens)
            #print(uniqueTokens)
            #print(len(uniqueTokens))

            unTokens = unique(tokens)

            while (TERMID < len(uniqueTokens)):

                TERMID = TERMID + 1
                termFile.write(TERMID.__str__())
                termFile.write('\t')
                termFile.write(uniqueTokens.__getitem__((TERMID - 1)))
                termFile.write('\n')

            tokpos = 1
            for tok in unTokens:
                id = uniqueTokens.index(tok) + 1

                indexFile.write(DOCID.__str__())
                indexFile.write('\t')
                indexFile.write(id.__str__())

                tokItr = 1
                for token in tokens:
                    if (tok in token):
                        indexFile.write('\t')
                        indexFile.write(tokItr.__str__())
                    tokItr = tokItr + 1
                indexFile.write('\n')

            print('Document:-', DOCID, ':', len(tokens), 'tokens')
            if((currentlyTraversed%20) == 0):
                print(currentlyTraversed, '/', totalFiles, 'done')
                print(len(uniqueTokens))

indexFile.close()
termFile.close()
docFile.close()