import os
os.system("mkdir -p Filelist")

f=open("SkimmedTreesList.txt","r")
filepref="SkimmedTrees_"

pref="root://se01.indiacms.res.in:1094/"
filecount=1
lineminus1=""
lineminus2=""
fileopen=False
log=open("log.txt","w")

for line in f:
	if not line=="\n":
		fname=line.split()[-1]
	else:
		fname=""
		
	if fname.endswith(".root") and not fileopen:
		folder=pref+lineminus2[:-2]+"/"
#		print lineminus2
#        log.write(lineminus2.split("/")[-3]+" "+filepref+str(filecount)+".txt\n")          # For making a list of CRAB job outputs
		log.write(lineminus2.split("/")[-1][:-2]+" "+filepref+str(filecount)+".txt\n")      # For making a list of SkimmedTrees
		out=open("Filelist/"+filepref+str(filecount)+".txt","w")		
		out.write(folder+fname+"\n")
		filecount+=1
		fileopen=True
	elif fname.endswith(".root"):
		out.write(folder+fname+"\n")
	elif fileopen:
		out.close()
		fileopen=False
	
	lineminus2=lineminus1
	lineminus1=line
	
log.close()
f.close()
