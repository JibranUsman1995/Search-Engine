import sys
import argparse
import os
import bs4
import re
from nltk import PorterStemmer
from nltk import sent_tokenize, word_tokenize
import numpy as np
import math


def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

def getID(term,key_value_Array):
    for x in key_value_Array:
        if x.__contains__(term):
            return 1,int(x[0])
    return 0,0

def getKeyText(id,key_value_Array):
    for x in key_value_Array:
        if x.__contains__(id):
            return 1,x[1]
    return 0,0

def getOffset(termID,key_value_Array):
    for x in key_value_Array:
        if x.__contains__(termID):
            return 1,x[1]
    return 0,0

def topicProcessing(filename):
    queryFile = open(filename, 'r', encoding="utf8", errors='ignore').read()
    soup = bs4.BeautifulSoup(queryFile, 'html.parser')

    ids = soup.findAll('topic')
    topicNos = []

    for id in ids:
        stt = str(id)
        w = 0

        while (stt[w] != '='):
            w += 1

        newstr = ''
        w += 2

        while (stt[w] != ' '):
            newstr += stt[w]
            w += 1

        topicNos.append(newstr[0:(len(newstr) - 1)])
    return topicNos

def queryProcessing(filename):
    queryFile=open(filename, 'r', encoding="utf8", errors='ignore').read()

    soup = bs4.BeautifulSoup(queryFile, 'html.parser')
    queries = soup.find_all('query')

    stopList = open('stoplist.txt', 'r', encoding='utf8', errors='ignore').read()
    stopWords = re.findall(r'\w[\w]*', stopList)

    stemmer = PorterStemmer()

    queryArrayTokens = []

    for sentence in queries:

        tokens = []
        words = re.findall(r'\w[\w]*', sentence.text)

        for word in words:
            word = word.lower()

            if(word not in stopWords):
                if(len(word) > 1):
                    tokens.append(stemmer.stem(word))

        tokens=unique(tokens)
        queryArrayTokens.append(tokens)

    return queryArrayTokens

#this func return array of format [termID , [docID, number of positions of term in this doc],[docID2, pos count of term in doc2]...so on]
def retrieve_info_processing(line):
    arr = []
    line = line.split("\t")

    arr.append(line[0])
    dID_curr = 0
    dID_prev = 0
    pos_count = 0

    line[1] = line[1].split(":")
    dID_prev = int(line[1][0])
    pos_count += 1

    for i in range(2, line.__len__()):
        line[i] = line[i].split(":")

        dID_curr = int(line[i][0])
        if dID_curr == 0:
            pos_count += 1

        else:

            temp = []
            temp.append(dID_prev)
            temp.append(pos_count)

            arr.append(temp)

            dID_prev = dID_prev + dID_curr
            pos_count = 1

    temp = []
    temp.append(dID_prev)
    temp.append(pos_count)
    arr.append(temp)

    return arr

def getDocInfo():
    ptr = open('doc_index.txt', 'r', errors='ignore')
    docInfo = []
    docItr = 1

    totalTerms = 0
    for line in ptr.readlines():
        lineInfo = line.split('\t')

        if(int(lineInfo[0]) == docItr):
            totalTerms += (len(lineInfo)-2)
        else:
            docInfo.append(totalTerms)
            totalTerms = 0
            docItr += 1
    docInfo.append(totalTerms)

    avg = 0
    for tups in docInfo:
        avg += tups
    avg = avg/len(docInfo)

    final =[]
    final.append(avg)
    final.append(docInfo)

    return final

def scoreJM(qList, qData, docInfo, topicList, lda):
    endFile = open('JM.txt', 'w', errors='ignore')

    i = 0
    for queri in qData:
        qVec = []
        dVec = []

        for terms in queri:
            k = 1
            while(k < len(terms)):
                dVec.append(int(terms[k][0]))
                k += 1
            dVec = unique(dVec)

        dVec.sort()

        oktf = 0
        qsumtf = 0
        qsumlen = 0
        for terms in queri:

            qsumlen = qsumlen + len(qList[i])
            qsumtf = qsumtf + 1

            oktf = ((lda * (1/len(qList[i]))) + ((1-lda)*(qsumtf/qsumlen)))
            qVec.append(oktf)

        docVector = []

        for docs in dVec:
            found = False
            Vec = []

            dsumtf = 0
            dsumlen = 0

            for terms in queri:

                okans = 0
                found = False
                k = 1
                while (k < len(terms)):
                    if(docs == terms[k][0]):
                        okans = int(terms[k][1])
                        found = True
                        break
                    k += 1
                if(found == True):
                    dsumtf = dsumtf + okans
                    dsumlen = dsumlen + int(docInfo[1][docs-1])
                    okans = ((lda*(okans/int(docInfo[1][docs-1]))) + ((1-lda)*(dsumtf/dsumlen)))
                    Vec.append(okans)
                else:
                    Vec.append(int(0))
                docVector.append(Vec)

        l = 0

        scores = []
        names = []
        qMag = np.sqrt(np.dot(qVec,qVec))
        while l < len(dVec):
            dMag = np.sqrt(np.dot(docVector[l], docVector[l]))
            score  = (np.dot(qVec, docVector[l])/(dMag * qMag))
            scores.append(score)
            names.append(docidsFile[dVec[l]-1][1])
            l += 1

        sorted_y_idx_list = sorted(range(len(scores)), key=lambda x: scores[x])
        docNames = [names[i] for i in sorted_y_idx_list]
        scores.sort()

        l = len(docNames)-1
        while l >= 0:
            #(getID(docNames[l], docidsFile))[1] docID
            endFile.write(topicList[i])
            endFile.write(' ')
            endFile.write('0 ')
            endFile.write(docNames[l])
            endFile.write(' ')
            endFile.write(str(len(docNames) - l))
            endFile.write(' ')
            endFile.write(str(scores[l]))
            endFile.write(' ')
            endFile.write('run1\n')
            l -= 1

        i += 1
    endFile.close()

def scoreBM25(qList, qData, docInfo, topicList, k1, k2, b):
    endFile = open('BM25.txt', 'w', errors='ignore')

    i = 0
    for queri in qData:
        dVec = []

        for terms in queri:
            k = 1
            while(k < len(terms)):
                dVec.append(int(terms[k][0]))
                k += 1
            dVec = unique(dVec)
        dVec.sort()

        scores = []

        for doc in dVec:
            sum = 0

            for terms in queri:
                tfdi = 0

                p = 1
                found = False

                while(p < len(terms) and found == False):
                    if(doc == int(terms[p][0])):
                        tfdi = int(terms[p][1])
                        found = True
                    p+=1

                ans  = math.log10(((len(docidsFile)-1)+0.5/(len(terms)-1)+0.5))
                K = k1*((1-b)+b*(int(docInfo[1][doc-1])/int(docInfo[0])))
                ans2 = ((1 + k1)*tfdi)/(K + tfdi)
                ans3 = ((1+k2)*1)/(k2+1)

                endans = ans*ans2*ans3
                sum = sum + endans

            scores.append(sum)

        names = []
        l=0

        while l < len(dVec):
            names.append(docidsFile[dVec[l] - 1][1])
            l += 1

        sorted_y_idx_list = sorted(range(len(scores)), key=lambda x: scores[x])
        docNames = [names[i] for i in sorted_y_idx_list]
        scores.sort()

        l = len(docNames)-1
        while l >= 0:
            #(getID(docNames[l], docidsFile))[1] docID
            endFile.write(topicList[i])
            endFile.write(' ')
            endFile.write('0 ')
            endFile.write(docNames[l])
            endFile.write(' ')
            endFile.write(str(len(docNames) - l))
            endFile.write(' ')
            endFile.write(str(scores[l]))
            endFile.write(' ')
            endFile.write('run1\n')
            l -= 1

        i += 1
    endFile.close()

def scoreTFIDF(qList, qData, docInfo, topicList):
    endFile = open('TFIDF.txt', 'w', errors='ignore')

    i = 0
    for queri in qData:
        qVec = []
        dVec = []

        for terms in queri:
            k = 1
            while(k < len(terms)):
                dVec.append(int(terms[k][0]))
                k += 1
            dVec = unique(dVec)

        dVec.sort()

        oktf = 0
        for terms in queri:
            oktf = (1/1 + 0.5 + (1.5*(len(qList[i])/int(docInfo[0]))))

            newterm = (docidsFile.__len__() - 1) / (len(terms) - 1)
            newterm = math.log10(newterm)
            oktf = oktf * newterm

            qVec.append(oktf)

        docVector = []

        for docs in dVec:
            found = False
            Vec = []
            for terms in queri:
                okans = 0
                found = False
                k = 1
                while (k < len(terms)):
                    if(docs == terms[k][0]):
                        okans = int(terms[k][1])
                        found = True
                        break
                    k += 1
                if(found == True):
                    okans = okans/(okans + 0.5 + (1.5*(int(docInfo[1][docs-1])/int(docInfo[0]))))

                    newterm = (docidsFile.__len__() - 1)/(len(terms) - 1)
                    newterm = math.log10(newterm)

                    okans = okans * newterm

                    Vec.append(okans)
                else:
                    Vec.append(int(0))
                docVector.append(Vec)

        l = 0

        scores = []
        names = []
        qMag = np.sqrt(np.dot(qVec,qVec))
        while l < len(dVec):
            dMag = np.sqrt(np.dot(docVector[l], docVector[l]))
            score  = (np.dot(qVec, docVector[l])/(dMag * qMag))
            scores.append(score)
            names.append(docidsFile[dVec[l]-1][1])
            l += 1

        sorted_y_idx_list = sorted(range(len(scores)), key=lambda x: scores[x])
        docNames = [names[i] for i in sorted_y_idx_list]
        scores.sort()

        l = len(docNames)-1
        while l >= 0:
            #(getID(docNames[l], docidsFile))[1] docID
            endFile.write(topicList[i])
            endFile.write(' ')
            endFile.write('0 ')
            endFile.write(docNames[l])
            endFile.write(' ')
            endFile.write(str(len(docNames) - l))
            endFile.write(' ')
            endFile.write(str(scores[l]))
            endFile.write(' ')
            endFile.write('run1\n')
            l -= 1

        i += 1
    endFile.close()

def scoreOkapiTF(qList, qData, docInfo, topicList):
    endFile = open('TF.txt', 'w', errors='ignore')

    i = 0
    for queri in qData:
        qVec = []
        dVec = []

        for terms in queri:
            k = 1
            while(k < len(terms)):
                dVec.append(int(terms[k][0]))
                k += 1
            dVec = unique(dVec)

        dVec.sort()

        oktf = 0
        for terms in queri:
            oktf = (1/1 + 0.5 + (1.5*(int(len(qList[i]))/int(docInfo[0]))))
            qVec.append(oktf)

        docVector = []

        for docs in dVec:
            found = False
            Vec = []
            for terms in queri:
                okans = 0
                found = False
                k = 1
                while (k < len(terms)):
                    if(docs == terms[k][0]):
                        okans = int(terms[k][1])
                        found = True
                        break
                    k += 1
                if(found == True):
                    okans = okans/(okans + 0.5 + (1.5*(int(docInfo[1][docs-1])/int(docInfo[0]))))
                    Vec.append(okans)
                else:
                    Vec.append(int(0))
                docVector.append(Vec)

        l = 0

        scores = []
        names = []
        qMag = np.sqrt(np.dot(qVec,qVec))
        while l < len(dVec):
            dMag = np.sqrt(np.dot(docVector[l], docVector[l]))
            score  = (np.dot(qVec, docVector[l])/(dMag * qMag))
            scores.append(score)
            names.append(docidsFile[dVec[l]-1][1])
            l += 1

        sorted_y_idx_list = sorted(range(len(scores)), key=lambda x: scores[x])
        docNames = [names[i] for i in sorted_y_idx_list]
        scores.sort()

        l = len(docNames)-1
        while l >= 0:
            #(getID(docNames[l], docidsFile))[1] docID
            endFile.write(topicList[i])
            endFile.write(' ')
            endFile.write('0 ')
            endFile.write(docNames[l])
            endFile.write(' ')
            endFile.write(str(len(docNames) - l))
            endFile.write(' ')
            endFile.write(str(scores[l]))
            endFile.write(' ')
            endFile.write('run1\n')
            l -= 1

        i += 1
    endFile.close()

parser = argparse.ArgumentParser(description = "Description for my parser")
parser.add_argument("-T", "--score", help = "Term ID required here", required = True, default = "")
argument = parser.parse_args()

queryList = queryProcessing("topics.xml")
topicList = topicProcessing("topics.xml")

#termIDs key-value pairs

termidsFile=open('termids.txt', 'r', errors='ignore').read()
termidsFile=termidsFile.split("\n")

for i in range(0,termidsFile.__len__()):
    termidsFile[i]=termidsFile[i].split("\t")

#docIDs key-value pairs

docidsFile=open('docids.txt', 'r', errors='ignore').read()
docidsFile=docidsFile.split("\n")

for i in range(0,docidsFile.__len__()):
    docidsFile[i]=docidsFile[i].split("\t")

#create term_offset array
term_infoFile = open('term_info.txt','r',errors='ignore').read()
term_offset=term_infoFile.split("\n")

for i in range(0,term_offset.__len__()):
    term_offset[i]=term_offset[i].split("\t")

#term_infoFile.close()

#create dic of term_info
term_infoFile = open('term_info.txt','r',errors='ignore')
term_indexFile = open('term_index.txt', 'r', errors='ignore')
term_info_Index = dict()


for line in term_infoFile.readlines():

    values = re.findall(r'\w[\w]*', line)
    term_info_Index[values[0]] = values
    #term_indexFile.seek(int(values[1]))
    #print(term_indexFile.readline())

#retrieve info from inverted-index

queryData = []
for query in queryList:
#query=queryList[0]
    data=[]
    for word in query:
        #print(word)
        tID=getID(word,termidsFile)
        if tID[0]==1:
            #print(tID[1])
            t_offset=getOffset(str(tID[1]),term_offset)
            if t_offset[0]==1:
                #print(t_offset[1])
                term_indexFile.seek(int(t_offset[1]))
                inverted_index_line=term_indexFile.readline()
                #print(inverted_index_line)

                data.append(retrieve_info_processing(inverted_index_line))
    queryData.append(data)

    ##<----------------Apply Scoring functions here------------->
print('Extracting Document data, please wait')
docData = getDocInfo()

print('Applying scoring function')

if argument.score:
    if(format(argument.score) == 'TF'):
        scoreOkapiTF(queryList, queryData, docData, topicList)
    elif(format(argument.score) == 'TF-IDF'):
        scoreTFIDF(queryList, queryData, docData, topicList)
    elif(format(argument.score) == 'BM25'):
        scoreBM25(queryList, queryData, docData, topicList, 1.2, 50, 0.75)
    elif(format(argument.score) == 'JM'):
        scoreJM(queryList, queryData, docData, topicList, 0.6)
    else:
        print('Invalid Input Arguments')
else:
    print('No scoring function specified')