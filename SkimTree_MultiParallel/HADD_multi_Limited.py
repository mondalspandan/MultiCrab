import os
folder="data"

listfolders = [f for f in os.listdir(folder) if not os.path.isfile(os.path.join(folder, f))]

for fold1 in listfolders:
    fold2list = [f for f in os.listdir(os.path.join(folder, fold1)) if not os.path.isfile(os.path.join(folder, fold1, f))]
    for fold2 in fold2list:
        if fold2 != "WJetsToLNu_HT-70To100_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_MC25ns_LegacyMC_20170328": continue
        filelist = sorted([f for f in os.listdir(os.path.join(folder, fold1, fold2)) if os.path.isfile(os.path.join(folder, fold1, fold2, f))])
        filestr = ""
        
        #Limit number of files:
        size=os.path.getsize(os.path.join(folder, fold1, fold2, filelist[0]))
        lim=int(1024**3/size)+1
        nfiles=min(lim,len(filelist))
        print "Processing",nfiles,"of",len(filelist),"files =",nfiles*size/(1024)**2,"MB (approx.)"
                
        for ifile in range(nfiles):
            filestr += os.path.join(folder, fold1, fold2, filelist[ifile]) + " "
        os.system("mkdir -p SkimmedTrees_Temp/")
        command = "hadd SkimmedTrees_Temp/"+fold2+".root "+filestr
        os.system(command)
#        print command
        print "Exported SkimmedTrees_Temp/"+fold2+".root"
        print
