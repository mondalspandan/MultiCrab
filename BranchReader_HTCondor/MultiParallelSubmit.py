import os
folder="Filelists"
test=False

logs = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
listfolders = [f for f in os.listdir(folder) if not os.path.isfile(os.path.join(folder, f))]
#print logs
#print listfolders

if not test: os.system("chmod +x runAnalysis.sh")
for outdirs in ['error','log','output']:
    if not test: os.system("mkdir -p "+outdirs)

for foldname in listfolders:
#    os.system("mkdir -p data/"+foldname)
    run=foldname[9:]
    logfile=open(os.path.join(folder,"log_"+run+'.txt'),'r')
    sample={run:foldname}
    for line in logfile:
        sample[line.split()[1]]=line.split()[0]
    
    for listname in os.listdir(os.path.join(folder,foldname)):        
        inpfilename=os.path.join(folder,foldname,listname)
        outfoldname="data/"+foldname+"/"+sample[listname]
        if not test: os.system("mkdir -p "+outfoldname)
        
        submittemp=open("submit_parallel_temp.sub","w")
        submitfile=open("submit_parallel.sub","r")
        for line in submitfile:
            submittemp.write(line)                        
        submitfile.close()       
        
#        submittemp.write("arguments = $(rootfile)")
        submittemp.write("transfer_output_remaps = \"BROutput.root = "+outfoldname+"/BROuptut_$(Process).root\"\n")        
        submittemp.write("queue rootfile from "+inpfilename)
        submittemp.close()
        
        print "\n===============================\nSubmitting "+inpfilename+": "+ sample[listname]+"\n===============================\n"
        
        if not test: os.system("condor_submit submit_parallel_temp.sub")
    logfile.close()
