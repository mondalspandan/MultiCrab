def getAll():
    allquantlist=[]
            
    for region in ['sr','Zmumucr','Zeecr','Wmucr','Wecr','TOPcr']:                               # Jets: Makes all combinations of region, jet number, etc.
        for jetprop in ['pT','eta','phi','csv']:
            for jetnum in [1,2]:
                allquantlist.append('jet'+str(jetnum)+"_"+jetprop+"_"+region+"1")
                
            for jetnum in [1,2,3]:
                allquantlist.append('jet'+str(jetnum)+"_"+jetprop+"_"+region+"2")                                         

    for nSR in ['1','2']:                                                   # Leptons: Makes all combinations of region, lepton number, etc.
        for lep in ['mu','el']:
            props = ['pT','eta','phi']
            if lep=='mu':
              props.append('iso')  
              for lepprop in props:
                 for nCR in ['1','2']:       # For ZCR, because Z has 2 mu or 2 ele
                       allquantlist.append(lep+nCR+"_"+lepprop+"_Zmumucr"+nSR)
                 for region in ['Wecr','Wmucr','TOPcr']:          # For ZCR, only 1 mu and/or ele
                       allquantlist.append(lep+"1_"+lepprop+"_"+region+nSR)
            if lep=='el':
              for lepprop in props:
                 for nCR in ['1','2']:       # For ZCR, because Z has 2 mu or 2 ele
                       allquantlist.append(lep+nCR+"_"+lepprop+"_Zeecr"+nSR)
                 for region in ['Wecr','Wmucr','TOPcr']:          # For ZCR, only 1 mu and/or ele
                       allquantlist.append(lep+"1_"+lepprop+"_"+region+nSR)        
                
    allquantlist+=['min_dPhi_sr1','min_dPhi_sr2','ZhadronRecoil1mumu','ZhadronRecoil1ee','Zmass1mumu','Zmass1ee','ZpT1mumu','ZpT1ee','WhadronRecoil1mu','WhadronRecoil1e','WpT1mu','WpT1e','Wmass1mu','Wmass1e','WpT1','TOPRecoil1','ZhadronRecoil2mumu','ZhadronRecoil2ee','Zmass2mumu','Zmass2ee','ZpT2mumu','ZpT2ee','WhadronRecoil2mu','WhadronRecoil2e','Wmass2mu','Wmass2e','WpT2mu','WpT2e','TOPRecoil2']
    
    return allquantlist

def getPresel():
    preselquantlist=['presel_jet1_csv_sr1','presel_jet2_csv_sr1','presel_jet1_csv_sr2','presel_jet2_csv_sr2','presel_jet3_csv_sr2']
    return preselquantlist
