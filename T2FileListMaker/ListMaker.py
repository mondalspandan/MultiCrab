f=open("BkgRun3Dir.txt","r")

pref="root://se01.indiacms.res.in:1094/"
filepref="bkg_run3_"
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
		log.write(lineminus2.split("/")[-3]+" "+filepref+str(filecount)+".txt\n")
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
