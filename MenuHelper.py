import argparse
import sys, getopt
from nltk import PorterStemmer
import re

#Main starting below

parser = argparse.ArgumentParser(description = "Description for my parser")
parser.add_argument("-T", "--term", help = "Term ID required here", required = False, default = "")
parser.add_argument("-D", "--doc", help = "Document ID required here", required = False, default = "")

argument = parser.parse_args()

status = False
termStatus = False
docStatus = False

termStr = format(argument.term)
docStr = format(argument.doc)

stemmer = PorterStemmer()

if argument.term:
    status = True
    termStatus = True

if argument.doc:
    status = True
    docStatus = True

if not status:
    print("No arguments passed, atleast one argument must be passed")
    exit(1)
else:
    if(termStatus == True and docStatus == True):
        tFound = False
        dFound = False

        print('Term:- ', termStr)
        print('Document:- ', docStr)

        termStem = stemmer.stem(termStr)

        fileTrvs = open('termids.txt', 'r', encoding='utf8', errors='ignore')
        print(termStr)
        termID = 0

        for line in fileTrvs.readlines():
            termDetail = line.split()

            if (termDetail[1].__str__() == termStem):
                termID = termDetail[0]
                tFound = True
                print('Term ID:- ', termID.__str__())
                break

        if(tFound == False):
            print('No such term exists')
            exit(1)


        fileTrvs.close()

        fileDoc = open('docids.txt', 'r', encoding='utf8', errors='ignore')
        finished = False
        started = False

        print(docStr)
        docID = 0

        for line in fileDoc.readlines():
            docDet = line.split()

            if (docDet[1].__str__() == docStr):
                docID = docDet[0]
                dFound = True
                print('Doc ID', docID.__str__())
                break

        if(dFound == False):
            print('No such file exists')
            exit(1)


        fileDoc.close()

        fileDocInfo = open('doc_index.txt', 'r', encoding='utf8', errors='ignore')

        totalTerms = 0
        distinctTerms = 0

        for line in fileDocInfo.readlines():
            docInfo = line.split()

            if((docInfo[0] == docID.__str__()) and (docInfo[1] == termID.__str__())):
                print('Term Frequency in Document:- ', (len(docInfo) - 2))
                print('Positions are:- ')

                i = 2

                while(i < len(docInfo)):
                    print(docInfo[i].__str__(),' ', end='')
                    i = i + 1


        fileDocInfo.close()

    elif(termStatus == True):
        termStem = stemmer.stem(termStr)

        fileTrvs = open('termids.txt', 'r', encoding='utf8', errors='ignore')
        print(termStr)

        termFound = False

        for line in fileTrvs.readlines():
            termDetail = line.split()

            if(termDetail[1].__str__() == termStem):

                termFound = True
                fileTermInfo = open('term_info.txt', 'r', encoding='utf8', errors='ignore')

                for anotherline in fileTermInfo.readlines():
                    termInfoDetail = anotherline.split()

                    if(termInfoDetail[0] == termDetail[0]):

                        print('Term ID:- ', termInfoDetail[0].__str__())
                        print('Inverted List Offset:- ', termInfoDetail[1].__str__())
                        print('Term Frequency in Corpus:- ', termInfoDetail[2].__str__())
                        print('Number of Documents with term appearances:- ', termInfoDetail[3].__str__())

                        break

                fileTermInfo.close()
                break

        if(termFound == False):
            print('No such term exists')

        fileTrvs.close()

    elif(docStatus == True):
        fileDoc = open('docids.txt', 'r', encoding='utf8', errors='ignore')
        finished = False
        started = False

        print(docStr)
        docID = 0

        fileFound = False

        for line in fileDoc.readlines():
            docDet = line.split()

            if(docDet[1].__str__() == docStr):
                fileFound = True
                docID = docDet[0]
                break

        if(fileFound == False):
            print('No such file exists')
            exit(1)

        fileDocInfo = open('doc_index.txt', 'r', encoding='utf8', errors='ignore')

        totalTerms = 0
        distinctTerms = 0

        for line in fileDocInfo.readlines():
            docInfo = line.split()

            if(docInfo[0].__str__() == docID.__str__()):
                started = True
                distinctTerms = distinctTerms + 1
                totalTerms = totalTerms + (len(docInfo) - 2)

                continue
            else:
                if(started == True):
                    print('Doc ID:- ', docID)
                    print('Distinct Terms:- ', distinctTerms)
                    print('Total Terms:- ', totalTerms)

                    break

        fileDocInfo.close()
        fileDoc.close()