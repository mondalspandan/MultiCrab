import os
os.system("mkdir -p Filelist")

f=open("Filelist_SkimmedTrees_MET_180115.txt","r")
filepref="SkimmedTrees_MET_180115"

pref="root://se01.indiacms.res.in:1094/"
filecount=1
lineminus1=""
lineminus2=""
fileopen=False
failedfile=False
log=open("log.txt","w")

for line in f:
	if not line=="\n":
		fname=line.split()[-1]
	else:
		fname=""
		
	if fname.endswith(".root") and not fileopen:
		folder=pref+lineminus2[:-2]+"/"
#		print lineminus2
		if lineminus2.split("/")[-1].strip()=="failed:": failedfile=True
		if not failedfile:
#			log.write(lineminus2.split("/")[-3]+" "+filepref+str(filecount)+".txt\n")          # For making a list of CRAB job outputs
			log.write(lineminus2.split("/")[-1][:-2]+" "+filepref+str(filecount)+".txt\n")      # For making a list of SkimmedTrees
			out=open("Filelist/"+filepref+str(filecount)+".txt","w")		
			out.write(folder+fname+"\n")
			filecount+=1
		fileopen=True
	elif fname.endswith(".root"):
		if not failedfile: out.write(folder+fname+"\n")
	elif fileopen:
	    if not failedfile: out.close()
	    fileopen=False
	    failedfile=False
	
	lineminus2=lineminus1
	lineminus1=line
	
log.close()
f.close()
