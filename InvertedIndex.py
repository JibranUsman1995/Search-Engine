from operator import itemgetter

file_docIndex=open("doc_index.txt",'r')
file_termIndex=open("term_index.txt",'w')


lines=file_docIndex.readlines()


for x in range(0,lines.__len__()):
    lines[x]=list(map(int,lines[x].split()))

lines.sort(key=itemgetter(1))


inverted_index=[]
termIDCount=[]
docIDCount=[]
tID=0
tCount=0
dCount=0
prevdID=0
prevPos=0

for i in range(0,lines.__len__()):

    if int(tID)==int(lines[i][1]):

        file_termIndex.write("\t"+str(int(lines[i][0])-prevdID)+":"+lines[i][2].__str__())
        tCount+=1

        if prevdID!=lines[i][0]:
            prevdID=int(lines[i][0])
            prevPos=int(lines[i][2])
            dCount+=1

        count=lines[i].__len__()
        if count>3:
            for j in range(3,count):
                file_termIndex.write("\t"+str(int(lines[i][0])-prevdID)+":"+str(int(lines[i][j])-int(prevPos)))
                prevPos = lines[i][j]
                tCount+=1

    else:
        if i>0:
            file_termIndex.write("\n")
            #file_termInfo.write(str(tID)+"\t"+str(offset[i-1])+"\t"+str(tCount)+"\t"+str(dCount)+"\n")
            termIDCount.append(str(tCount))
            docIDCount.append(str(dCount))



        tID=lines[i][1]
        tCount=0
        dCount=0
        prevdID=lines[i][0]
        prevPos=lines[i][2]

        file_termIndex.write(tID.__str__() + "\t" + lines[i][0].__str__() + ":" + lines[i][2].__str__())
        tCount += 1

        count = lines[i].__len__()
        if count > 3:
            for j in range(3, count):
                file_termIndex.write("\t" + (int(lines[i][0])-int(prevdID)).__str__() + ":" + str(int(lines[i][j])-int(prevPos)))
                prevPos = lines[i][j]
                tCount += 1

termIDCount.append(str(tCount))
docIDCount.append(str(dCount))

file_termIndex.close()
file_termInfo=open("term_info.txt",'w')
file_termIndex=open("term_index.txt",'r')

termIndexLines=file_termIndex.readlines()

sumOffset=0
offset=[]
offset.append(0)
for i in range(0,termIndexLines.__len__()):
    offset.append(int(termIndexLines[i].__len__())+1+sumOffset)
    sumOffset+=(int(termIndexLines[i].__len__())+1)

print(termIndexLines.__len__())
print(offset.__len__())
print(termIDCount.__len__())
print(docIDCount.__len__())


for i in range(0,termIndexLines.__len__()):
    termIndexLines[i]=termIndexLines[i].split()
    file_termInfo.write(termIndexLines[i][0]+"\t"+str(offset[i])+"\t"+str(termIDCount[i])+"\t"+str(docIDCount[i])+"\n")



file_termInfo.close()

