#!/usr/bin/env python
from ROOT import TFile, TTree, TH1F, TH1D, TH1, TCanvas, TChain,TGraphAsymmErrors, TMath, TH2D, TLorentzVector, TF1, AddressOf
import ROOT as ROOT
import os
import sys, optparse
from array import array
import math

ROOT.gROOT.SetBatch(True)
from MonoHbbQuantities import *
from PileUpWeights import PUWeight

ROOT.gROOT.ProcessLine('.L BTagCalibrationStandalone.cpp+') 

#ROOT.gROOT.ProcessLine('.L TheaCorrection.cpp+') 

######################################
## set up running mode of the code.
######################################

#ROOT.gROOT.ProcessLine('.L PileUpWeights.h')

#print "puweight = ",PUWEIGHT(10)
usage = "usage: %prog [options] arg1 arg2"
parser = optparse.OptionParser(usage)

## data will be true if -d is passed and will be false if -m is passed
parser.add_option("-i", "--inputfile",  dest="inputfile")
parser.add_option("-o", "--outputfile", dest="outputfile")
parser.add_option("-D", "--outputdir", dest="outputdir")

parser.add_option("-a", "--analyze", action="store_true",  dest="analyze")

parser.add_option("-e", "--efficiency", action="store_true",  dest="efficiency")
parser.add_option("-F", "--farmout", action="store_true",  dest="farmout")
parser.add_option("-t", "--table", action="store_true",  dest="table")
parser.add_option("-P", "--OtherPlots", action="store_true",  dest="OtherPlots")

########################################################################################################################
########################## cut values########################################################################
########################################################################################################################

parser.add_option("--dbt", action="store_true",  dest="dbt")
parser.add_option( "--dbtcut", type=float,  dest="dbtcut")

parser.add_option("--theac", action="store_true",  dest="theac")

(options, args) = parser.parse_args()

if options.farmout==None:
    isfarmout = False
else:
    isfarmout = options.farmout


#print 'options = ',[options.inputfile]
inputfilename = options.inputfile
outputdir = options.outputdir

#print inputfilename
pathlist = inputfilename.split("/")
sizeoflist = len(pathlist)
#print ('sizeoflist = ',sizeoflist)
rootfile='tmphist'
rootfile = pathlist[sizeoflist-1]
textfile = rootfile+".txt"

#outputdir='bbMETSamples/'
if outputdir!='.': os.system('mkdir -p '+outputdir)

if options.outputfile is None or options.outputfile==rootfile:
   outputfilename = "/Output_"+rootfile
else:
   outputfilename = "/"+options.outputfile

#if isfarmout:
outfilename = outputdir + outputfilename
#else:
#    outfilename = options.outputfile    

print "Input:",options.inputfile, "; Output:", outfilename

skimmedTree = TChain("outTree")


#bbMET_tree = TTree( 'bbMET_tree', 'outputTree' )
#print isfarmout



def WhichSample(filename):
    samplename = 'all'
    if filename.find('WJets')>-1:
        samplename = 'WJETS'
    elif filename.find('ZJets')>-1:
        samplename = 'ZJETS'
    elif filename.find('TT')>-1:
        samplename  = 'TT'
    else:
        samplename = 'all'
    return samplename
    


def TheaCorrection(puppipt=200.0,  puppieta=0.0):
    puppisd_corrGEN      = TF1("puppisd_corrGEN","[0]+[1]*pow(x*[2],-[3])");
    puppisd_corrGEN.SetParameters(
        1.00626,
        -1.06161,
        0.07999,
        1.20454
        )
    puppisd_corrRECO_cen =  TF1("puppisd_corrRECO_cen","[0]+[1]*x+[2]*pow(x,2)+[3]*pow(x,3)+[4]*pow(x,4)+[5]*pow(x,5)");
    puppisd_corrRECO_cen.SetParameters(
        1.05807,
        -5.91971e-05,
        2.296e-07,
        -1.98795e-10,
        6.67382e-14,
        -7.80604e-18
        )
    
    puppisd_corrRECO_for = TF1("puppisd_corrRECO_for","[0]+[1]*x+[2]*pow(x,2)+[3]*pow(x,3)+[4]*pow(x,4)+[5]*pow(x,5)");
    puppisd_corrRECO_for.SetParameters(
        1.26638,
        -0.000658496,
        9.73779e-07,
        -5.93843e-10,
        1.61619e-13,
        -1.6272e-17)
    
    genCorr  = 1.
    recoCorr = 1.
    totalWeight = 1.
    
    genCorr =  puppisd_corrGEN.Eval( puppipt )
    if ( abs(puppieta)  <= 1.3 ) :
        recoCorr = puppisd_corrRECO_cen.Eval( puppipt )
    elif( abs(puppieta) > 1.3 ) :
        recoCorr = puppisd_corrRECO_for.Eval( puppipt )
        
    totalWeight = genCorr * recoCorr
    return totalWeight
    



h_t = TH1F('h_t','h_t',2,0,2)
h_t_weight = TH1F('h_t_weight','h_t_weight',2,0,2)

samplename = 'all'
if isfarmout:
    infile = open(inputfilename)
    for ifile in infile: 
        skimmedTree.Add(ifile.rstrip())
        samplename = WhichSample(ifile.rstrip())
        ## for histograms
        f_tmp = TFile.Open(ifile.rstrip(),'READ')
        h_tmp = f_tmp.Get('h_total')
        h_tmp_weight = f_tmp.Get('h_total_mcweight')
        h_t.Add(h_tmp)
        h_t_weight.Add(h_tmp_weight)

if not isfarmout:
    skimmedTree.Add(inputfilename)
    samplename = WhichSample(inputfilename)
    ## for histograms
    f_tmp = TFile(inputfilename,'READ')
    h_tmp = f_tmp.Get('h_total')
    h_tmp_weight = f_tmp.Get('h_total_mcweight')
    h_t.Add(h_tmp)
    h_t_weight.Add(h_tmp_weight)

debug = False 

def AnalyzeDataSet():
    ## Input rootfile name
    
    #rootfilename = inputfilename
    #print (rootfilename,inputfilename)
    #f = TFile(rootfilename,'READ')
    #skimmedTree = f.Get('tree/treeMaker')
    NEntries = skimmedTree.GetEntries()
    print 'NEntries = '+str(NEntries)
    npass = 0
    #print [rootfilename, NEntries]
    cutStatus={'preselection':NEntries}
    cutStatusSR1={'preselection':NEntries}
    cutStatusSR2={'preselection':NEntries}
    
#    cutStatus['trigger'] = 0
#    cutStatus['filter'] = 0
    cutStatus['pfmet'] =  0
#    cutStatus['njetSR1']=  0
#    cutStatus['njet1SR1'] = 0
#    cutStatus['njet2SR1'] = 0
#    cutStatus['njetSR2'] = 0
#    cutStatus['njet1SR2'] = 0
#    cutStatus['njet2SR2'] = 0
#    cutStatus['njet2SR2'] = 0    
    cutStatus['isinSR'] = 0
    cutStatus['jet1'] = 0
    cutStatus['jet2/3'] = 0
    cutStatus['btaggedjet'] = 0
#    cutStatus['btag'] = 0
#    cutStatus['dphi'] = 0
#    cutStatus['ThinJetVeto'] = 0
#    cutStatus['bVeto'] = 0
#    cutStatus['eleveto'] = 0
#    cutStatus['muveto'] = 0
#    cutStatus['tauveto'] = 0

    cutStatusSR1['njet'] = 0
    cutStatusSR1['jet1'] = 0
    cutStatusSR1['jet2'] = 0
    cutStatusSR1['btaggedjet'] = 0
    
    cutStatusSR2['njet'] = 0
    cutStatusSR2['jet1pT'] = 0
    cutStatusSR2['jet1phi'] = 0
    cutStatusSR2['jet2pT'] = 0
    cutStatusSR2['jet2phi'] = 0
    cutStatusSR2['jet3pT'] = 0
    cutStatusSR2['jet3phi'] = 0
    cutStatusSR2['jet1'] = 0
    cutStatusSR2['jet2'] = 0
    cutStatusSR2['jet3'] = 0
    cutStatusSR2['btaggedjet1'] = 0
    cutStatusSR2['btaggedjet2'] = 0
    
    CRs=['ZCRSR1','ZCRSR2','WCRSR1','WCRSR2','TopCRSR1','TopCRSR2']
    
    CRStatus={'total':NEntries}
    for CRname in CRs:
        CRStatus[CRname]=0
    
    
    #print outfilename
    allquantities = MonoHbbQuantities(outfilename)
    allquantities.defineHisto()

#    for attr, value in allquantities.__dict__.iteritems():
#       print attr, value
#       if isinstance(value, float):
#          bbMET_tree.Branch('bbMETvariables',AddressOf(allquantities,'histo'),'histo/D')
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # BTag Scale Factor Initialisation
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    othersys = ROOT.std.vector('string')()
    othersys.push_back('down')
    othersys.push_back('up')
    ## ThinJets
    calib1 = ROOT.BTagCalibrationStandalone('csvv2', 'CSVv2_ichep.csv')
    reader1 = ROOT.BTagCalibrationStandaloneReader( 0, "central", othersys)    
    reader1.load(calib1, 0,  "comb" )  
    reader1.load(calib1, 1,  "comb" )  
    reader1.load(calib1, 2,  "incl" )  
    
    h_total = TH1F('h_total','h_total',2,0,2)
    h_total_mcweight = TH1F('h_total_mcweight','h_total_mcweight',2,0,2)
    
    
    
    for ievent in range(NEntries):
    #for ievent in range(501):
        
        ##
        sf_resolved1 = []
        sf_resolved2 = []
        sf_resolved3 = []
        #print "event number = ",ievent
        skimmedTree.GetEntry(ievent)
        
        ## Get all relevant branches
        
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        ## Extract branches
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        run                        = skimmedTree.__getattr__('st_runId')
        lumi                       = skimmedTree.__getattr__('st_lumiSection')
        event                      = skimmedTree.__getattr__('st_eventId')

        #if event != 4126: continue                                
        #if lumi  != 42: continue                                
        if ievent%10000==0: print (ievent)
        #trigName                   = skimmedTree.__getattr__('st_hlt_trigName')
        #trigResult                 = skimmedTree.__getattr__('st_hlt_trigResult')
        #filterName                 = skimmedTree.__getattr__('st_hlt_filterName')
        #filterResult               = skimmedTree.__getattr__('st_hlt_filterResult')
         
        pfMet                      = skimmedTree.__getattr__('st_pfMetCorrPt')
        pfMetPhi                   = skimmedTree.__getattr__('st_pfMetCorrPhi')
        
        nTHINJets                  = skimmedTree.__getattr__('st_THINnJet')
        thinjetP4                  = skimmedTree.__getattr__('st_THINjetP4')
        thinJetCSV                 = skimmedTree.__getattr__('st_THINjetCISVV2')
        #passThinJetLooseID         = skimmedTree.__getattr__('st_THINjetPassIDLoose')
        #passThinJetPUID            = skimmedTree.__getattr__('st_THINisPUJetID')
        THINjetHadronFlavor        = skimmedTree.__getattr__('st_THINjetHadronFlavor')
        thinjetNhadEF              = skimmedTree.__getattr__('st_THINjetNHadEF')
        thinjetChadEF              = skimmedTree.__getattr__('st_THINjetCHadEF')
        
        nEle                       = skimmedTree.__getattr__('st_nEle')
        eleP4                      = skimmedTree.__getattr__('st_eleP4')
        eleIsPassLoose             = skimmedTree.__getattr__('st_eleIsPassLoose')
        eleIsPassMedium            = skimmedTree.__getattr__('st_eleIsPassMedium')
        eleIsPassTight             = skimmedTree.__getattr__('st_eleIsPassTight')
        
        nMu                        = skimmedTree.__getattr__('st_nMu')
        muP4                       = skimmedTree.__getattr__('st_muP4')
        isLooseMuon                = skimmedTree.__getattr__('st_isLooseMuon')
        isMediumMuon               = skimmedTree.__getattr__('st_isMediumMuon')
        isTightMuon                = skimmedTree.__getattr__('st_isTightMuon')
        muChHadIso                 = skimmedTree.__getattr__('st_muChHadIso')
        muNeHadIso                 = skimmedTree.__getattr__('st_muNeHadIso')
        muGamIso                   = skimmedTree.__getattr__('st_muGamIso')
        muPUPt                     = skimmedTree.__getattr__('st_muPUPt')
        
        nTau                       = skimmedTree.__getattr__('st_HPSTau_n')
        tauP4                      = skimmedTree.__getattr__('st_HPSTau_4Momentum')
        #isDecayModeFinding         = skimmedTree.__getattr__('st_disc_decayModeFinding')
        #passLooseTauIso            = skimmedTree.__getattr__('st_disc_byLooseIsolationMVA3oldDMwLT')
        
        isData                     = skimmedTree.__getattr__('st_isData')
        mcWeight                   = skimmedTree.__getattr__('mcweight')
        pu_nTrueInt                = int(skimmedTree.__getattr__('st_pu_nTrueInt'))
        
        nGenPar                    = skimmedTree.__getattr__('st_nGenPar')
        genParId                   = skimmedTree.__getattr__('st_genParId')
        genMomParId                = skimmedTree.__getattr__('st_genMomParId')
        genParSt                   = skimmedTree.__getattr__('st_genParSt')
        genParP4                   = skimmedTree.__getattr__('st_genParP4')
        
        WenuRecoil                 = skimmedTree.__getattr__('WenuRecoil')
        Wenumass                   = skimmedTree.__getattr__('Wenumass')
        WmunuRecoil                = skimmedTree.__getattr__('WmunuRecoil')
        Wmunumass                  = skimmedTree.__getattr__('Wmunumass')
        ZeeRecoil                  = skimmedTree.__getattr__('ZeeRecoil')
        ZeeMass                    = skimmedTree.__getattr__('ZeeMass')
        ZmumuRecoil                = skimmedTree.__getattr__('ZmumuRecoil')
        ZmumuMass                  = skimmedTree.__getattr__('ZmumuMass')
        TOPRecoil                  = skimmedTree.__getattr__('TOPRecoil')
             
        jetSR1Info           = []
        jetSR2Info           = []
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # MC Weights ----------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        mcweight = 0.0 
        if isData==1:   mcweight =  1.0
        if not isData :
            if mcWeight<0:  mcweight = -1.0
            if mcWeight>0:  mcweight =  1.0
        
        
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        #
        ##number of bjets without any selection
        mybjets=[]
        for nb in range(nTHINJets):
            if thinJetCSV[nb] < 0.8 : continue
            mybjets.append(nb)

        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        ## PFMET Selection
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------        
        pfmetstatus = ( pfMet > 200.0 )   
#        if pfmetstatus == False : continue       
        if pfmetstatus: cutStatus['pfmet'] += 1
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        #----------------------------------------------------------------------------------------------------------------------------------------------------------------
        #Calculate Muon Relative PF isolation:
        MuIso = [((muChHadIso[imu]+ max(0., muNeHadIso[imu] + muGamIso[imu] - 0.5*muPUPt[imu]))/muP4[imu].Pt()) for imu in range(nMu)]
        

        ## list comprehensation
        
        inSR1=False
        inSR2=False
        
        if nTHINJets == 2:
            inSR1=True
            if pfmetstatus: cutStatusSR1['njet'] +=1
        elif nTHINJets == 3:
            inSR2=True
            if pfmetstatus: cutStatusSR2['njet'] +=1
        else:
            continue 
        
        if pfmetstatus: cutStatus['isinSR'] += 1        # The event qualifies to be in either of the SRs based on njet
        
        allquantities.presel_jet1_csv_sr1 = None
        allquantities.presel_jet2_csv_sr1 = None
        allquantities.presel_jet1_csv_sr2 = None
        allquantities.presel_jet2_csv_sr2 = None
        allquantities.presel_jet3_csv_sr2 = None
        ## for SR1
         # 2 jets and 1 btagged 
         
        if inSR1:                  
            
            if thinjetP4[0].Pt()>thinjetP4[1].Pt():   # Set lead jet as j1, second jet as j2
                ifirstjet=0
                isecondjet=1
            else:
                ifirstjet=1
                isecondjet=0
                
            j1=thinjetP4[ifirstjet]
            j2=thinjetP4[isecondjet]
            
            if j1.Pt() < 50.0: continue
            if DeltaPhi(j1.Phi(),pfMetPhi) < 0.5: continue            
            if thinjetNhadEF[ifirstjet] > 0.8 : continue
            if thinjetChadEF[ifirstjet]< 0.1: continue
            
            if pfmetstatus: cutStatus['jet1'] += 1              # Lead jet satisfies required criteria
            if pfmetstatus: cutStatusSR1['jet1'] +=1
                            
            if j2.Pt() < 30.0: continue
            if DeltaPhi(j2.Phi(),pfMetPhi) < 0.5: continue
            
            if pfmetstatus: cutStatus['jet2/3'] += 1           # Jet 2 satisfies the required criteria
            if pfmetstatus: cutStatusSR1['jet2'] +=1
            
            #===CSVs before any selection===
            allquantities.presel_jet1_csv_sr1=thinJetCSV[ifirstjet]		
            allquantities.presel_jet2_csv_sr1=thinJetCSV[isecondjet]		
            allquantities.FillPreSel()		
            #===     
            jet1csv = thinJetCSV[ifirstjet]
            jet2csv = thinJetCSV[isecondjet]
            if thinJetCSV[ifirstjet] < 0.8: continue            # Lead jet has to be b-tagged
            
            if pfmetstatus: cutStatus['btaggedjet'] += 1         # The b-jet criteria is fulfilled 
            if pfmetstatus: cutStatusSR1['btaggedjet'] +=1
            
            jet1pt = j1.Pt()
            jet1phi = j1.Phi()
            jet1eta = j1.Eta()
            
            jet2pt = j2.Pt()
            jet2phi = j2.Phi()
            jet2eta = j2.Eta()            
            
            jet1csv = thinJetCSV[ifirstjet]
            jet2csv = thinJetCSV[isecondjet]
            
            min_dPhi=min(DeltaPhi(j1.Phi(),pfMetPhi),DeltaPhi(j2.Phi(),pfMetPhi))

            jetSR1Info.append([jet1pt,jet1eta,jet1phi,jet1csv])
            jetSR1Info.append([jet2pt,jet2eta,jet2phi,jet2csv])
            jetSR1Info.append(min_dPhi)
          
     
     ## for SR2
        # 3 jets and 2 btagged 
        
        if inSR2:
        
            alljetPT=[jet.Pt() for jet in thinjetP4]
            jetindex=[0,1,2]
                        
            sortedjets=[jet for pt,jet in sorted(zip(alljetPT,thinjetP4), reverse=True)]      # This gives a list of jets with their pTs in descending order
            sortedindex=[jetindex for pt,jetindex in sorted(zip(alljetPT,jetindex), reverse=True)]     # Indices of jets in thinjetP4 in decscending order of jetPT
            
            j1=sortedjets[0]
            j2=sortedjets[1]
            j3=sortedjets[2]
            
            ifirstjet=sortedindex[0]
            isecondjet=sortedindex[1]
            ithirdjet=sortedindex[2]
            
            if j1.Pt() < 50.0: continue
            if pfmetstatus: cutStatusSR2['jet1pT'] += 1 
            if DeltaPhi(j1.Phi(),pfMetPhi) < 0.5: continue            
            if thinjetNhadEF[ifirstjet] > 0.8 : continue
            if thinjetChadEF[ifirstjet]< 0.1: continue
            
            if pfmetstatus: cutStatus['jet1'] += 1              # Lead jet satisfies required criteria
            
            if pfmetstatus: cutStatusSR2['jet1'] += 1
            if pfmetstatus: cutStatusSR2['jet1phi'] += 1
            
            if j2.Pt() < 50.0: continue
            if pfmetstatus: cutStatusSR2['jet2pT'] += 1
            if DeltaPhi(j2.Phi(),pfMetPhi) < 0.5: continue
            
            if pfmetstatus: cutStatusSR2['jet2phi'] += 1
            if pfmetstatus: cutStatusSR2['jet2'] += 1
            
            if j3.Pt() < 30.0: continue
            if pfmetstatus: cutStatusSR2['jet3pT'] += 1
            if DeltaPhi(j3.Phi(),pfMetPhi) < 0.5: continue
            if pfmetstatus: cutStatusSR2['jet3phi'] += 1
            if pfmetstatus: cutStatusSR2['jet3'] += 1
            
            
            if pfmetstatus: cutStatus['jet2/3'] += 1           # The jets 2 and 3 satisfy the required criteria
            
            #===CSVs before any selection===		
            allquantities.presel_jet1_csv_sr2=thinJetCSV[ifirstjet]
            allquantities.presel_jet2_csv_sr2=thinJetCSV[isecondjet]
            allquantities.presel_jet3_csv_sr2=thinJetCSV[ithirdjet]
            allquantities.FillPreSel()		
            #===  
            jet1csv = thinJetCSV[ifirstjet]
            jet2csv = thinJetCSV[isecondjet]
            jet3csv = thinJetCSV[ithirdjet]
            
            if thinJetCSV[ifirstjet] < 0.8: continue            # Lead jet has to be b-tagged
            if pfmetstatus: cutStatusSR2['btaggedjet1'] += 1
            
            if thinJetCSV[isecondjet] < 0.8: continue           # Second jet has to be b-tagged
            if pfmetstatus: cutStatusSR2['btaggedjet2'] += 1
            
            if pfmetstatus: cutStatus['btaggedjet'] += 1         # The b-jet criteria is fulfilled 
            
            jet1pt = j1.Pt()
            jet1phi = j1.Phi()
            jet1eta = j1.Eta()
            
            jet2pt = j2.Pt()
            jet2phi = j2.Phi()
            jet2eta = j2.Eta()
            
            jet3pt = j3.Pt()
            jet3phi = j3.Phi()
            jet3eta = j3.Eta()
            
            jet1csv = thinJetCSV[ifirstjet]
            jet2csv = thinJetCSV[isecondjet]
            jet3csv = thinJetCSV[ithirdjet]
            
            min_dPhi=min(DeltaPhi(j1.Phi(),pfMetPhi),DeltaPhi(j2.Phi(),pfMetPhi),DeltaPhi(j3.Phi(),pfMetPhi))

            jetSR2Info.append([jet1pt,jet1eta,jet1phi,jet1csv])
            jetSR2Info.append([jet2pt,jet2eta,jet2phi,jet2csv])
            jetSR2Info.append([jet3pt,jet3eta,jet3phi,jet3csv])
            jetSR2Info.append(min_dPhi)

        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        ## Leptons Info
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        myEles=[]
        for iele in range(nEle):
            if eleP4[iele].Pt() < 10 : continue
            if abs(eleP4[iele].Eta()) >2.5: continue
            myEles.append(iele)
        
        myMuos = []
        for imu in range(nMu):
            if muP4[imu].Pt()<10 : continue
            if abs(muP4[imu].Eta()) > 2.4  : continue
            myMuos.append(imu)

        myTaus=[]
        for itau in range(nTau):
            if tauP4[itau].Pt()<20 : continue
            if abs(tauP4[itau].Eta())>2.3 : continue
            myTaus.append(itau);
# --------------------------------------------------------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------------------------------------------------------

        #Control Regions
        
        #=================================================================
        #  Z control region
        #=================================================================
        zCR=True
        
        zCREle=False
        zCRMu=False
        
        if nEle==2 and nMu==0 and nTau==0:
            zCREle=True
            LepP4=eleP4
            isLoose=eleIsPassLoose
            isTight=eleIsPassTight
            zmass=ZeeMass
            hadrecoil=ZeeRecoil
        elif nMu==2 and nEle==0 and nTau==0:
            zCRMu=True
            LepP4=muP4
            isLoose=isLooseMuon
            isTight=isTightMuon
            zmass=ZmumuMass
            hadrecoil=ZmumuRecoil
        else:
            zCR=False
        
        if zCR:                                                 # Just to reduce reduntant computation
            if LepP4[0].Pt() > LepP4[1].Pt():
                iLeadLep=0
                iSecondLep=1
            else:
                iLeadLep=1
                iSecondLep=0
            
            # Leading lepton conditions:
            if LepP4[iLeadLep].Pt() < 30.: zCR=False
            print "isLoose: "+str(isLoose[iLeadLep])            #To see the data type in case of bugs (if any)
            if not isTight[iLeadLep]: zCR=False
            
            # Sub-leading lepton conditions:
            if LepP4[iSecondLep].Pt() < 10.: zCR=False
            if not isLoose[iSecondLep]: zCR=False
            
           
            Zmu1pT = None
            Zmu1eta = None
            Zmu1phi = None
            Zele1pT = None
            Zele1eta = None
            Zele1phi = None
            Zmu2pT = None
            Zmu2eta = None
            Zmu2phi = None
            Zele2pT = None
            Zele2eta = None
            Zele2phi = None
            Zmu1Iso  = None
            Zmu2Iso  = None
            if zCRMu:                                           # Special isolation requirement for Muon                
                if MuIso[iLeadLep] > 0.15: zCR=False             
                if MuIso[iSecondLep] > 0.25: zCR=False
                Zmu1Iso = MuIso[iLeadLep]
                Zmu2Iso = MuIso[iSecondLep]
                Zmu1pT  = LepP4[iLeadLep].Pt()
                Zmu1eta = LepP4[iLeadLep].Eta()
                Zmu1phi = LepP4[iLeadLep].Phi()
                Zmu2pT = LepP4[iSecondLep].Pt()
                Zmu2eta = LepP4[iSecondLep].Eta()
                Zmu2phi = LepP4[iSecondLep].Phi()                
                
            if zCREle:
                Zele1pT  = LepP4[iLeadLep].Pt()
                Zele1eta = LepP4[iLeadLep].Eta()
                Zele1phi = LepP4[iLeadLep].Phi()
                Zele2pT =  LepP4[iSecondLep].Pt()
                Zele2eta = LepP4[iSecondLep].Eta()
                Zele2phi = LepP4[iSecondLep].Phi()
                
            ZpT = math.sqrt( (LepP4[iLeadLep].Px()+LepP4[iSecondLep].Px())*(LepP4[iLeadLep].Px()+LepP4[iSecondLep].Px()) + (LepP4[iLeadLep].Py()+LepP4[iSecondLep].Py())*(LepP4[iLeadLep].Py()+LepP4[iSecondLep].Py()) )        #Identical for Mu and Ele
            
            # Z Mass condition:
            if zmass <= 70. or zmass >= 110.: zCR=False             
            
            # Hadronic recoil:
            if hadrecoil <= 200.: zCR=False 
            
        if zCR:
            if inSR1:
                CRStatus['ZCRSR1']+=1
            if inSR2:
                CRStatus['ZCRSR2']+=1
        #=================================================================
        #  W control region
        #=================================================================       
        wCR=True
        
        wCREle=False
        wCRMu=False
        
        if nEle==1 and nMu==0 and nTau==0:
            wCREle=True
            LepP4=eleP4
            isTight=eleIsPassTight
            wmass=Wenumass
            hadrecoil=WenuRecoil
        elif nMu==1 and nEle==0 and nTau==0:
            wCRMu=True
            LepP4=muP4
            isTight=isTightMuon
            wmass=Wmunumass
            hadrecoil=WmunuRecoil
        else:
            wCR=False
            
        if wCR:        
            # Leading lepton conditions:
            if LepP4[0].Pt() < 30.: wCR=False
            if not isTight[0]: wCR=False
            Wmu1pT = None
            Wmu1eta = None
            Wmu1phi = None
            Wele1pT = None
            Wele1eta = None
            Wele1phi = None
            Wmu1Iso  = None
            if wCRMu:
                if MuIso[0] > 0.15: wCR=False
                Wmu1Iso = MuIso[0]
                Wmu1pT  = LepP4[0].Pt()
                Wmu1eta = LepP4[0].Eta()
                Wmu1phi = LepP4[0].Phi()                
            
            if wCREle:
                Wele1pT  = LepP4[0].Pt()
                Wele1eta = LepP4[0].Eta()
                Wele1phi = LepP4[0].Phi()
                
            WpT = math.sqrt( ( pfMet*math.cos(pfMetPhi) + LepP4[0].Px())*( pfMet*math.cos(pfMetPhi) + LepP4[0].Px()) + ( pfMet*math.sin(pfMetPhi) + LepP4[0].Py())*( pfMet*math.sin(pfMetPhi) + LepP4[0].Py()) )        #Identical for Mu and Ele
            # W Mass condition:
            if wmass <= 50. or wmass >= 160.: wCR=False    
            
            # Hadronic recoil:
            if hadrecoil <= 200.: wCR=False 
            
        if wCR:
            if inSR1:
                CRStatus['WCRSR1']+=1
            if inSR2:
                CRStatus['WCRSR2']+=1
        #=================================================================
        #  Top control region
        #================================================================= 
        TopCR=False
        
        if nEle==1 and nMu==1 and nTau==0:
            TopCR=True
            
            # Muon
            if muP4[0].Pt() < 30.: TopCR=False
            if MuIso[0] > 0.15: TopCR=False                  
            if not isTightMuon[0]: TopCR=False                   
            
            # Electron
            if eleP4[0].Pt() < 30.: TopCR=False
            if not eleIsPassTight[0]: TopCR=False
            
            # Hadronic recoil:
            if TOPRecoil <= 200.: TopCR=False
            
            TOPmu1Iso = MuIso[0]
            
            TOPmu1pT   = muP4[0].Pt()
            TOPmu1eta  = muP4[0].Eta()
            TOPmu1phi  = muP4[0].Phi()
            TOPele1pT  = eleP4[0].Pt()
            TOPele1eta = eleP4[0].Eta()
            TOPele1phi = eleP4[0].Phi()
            
        if TopCR:
            if inSR1:
                CRStatus['TopCRSR1']+=1
            if inSR2:
                CRStatus['TopCRSR2']+=1
        
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        ## min DPhi
        ## nT<hinJets
        ## b-jet Veto
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        ## Lepton Veto
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        nleptons_ = (len(myTaus) + len(myMuos) + len(myEles))
        
        #if not (nleptons_ >= nlepton) : continue 
        #if not (nleptons_ < nLepton) : continue  
        
        #regime = False
        #if isboosted: regime = True
        #if isresolved: regime = False
        
        
        #if regime: 
         #   mt_ = MT(fatjetP4[HIndex].Pt(), pfMet, Phi_mpi_pi(pfMetPhi-fatjetP4[HIndex].Phi()) )
        #if not regime: 
         #   mt_ = MT(HiggsInfo[0][3], pfMet, Phi_mpi_pi(pfMetPhi-HiggsInfo[0][4]) )
        
        #if mt_ < 450.0: continue 
        
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        ## Photon Veto
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----to be added in future---------------------------------------------------------------------------------------------------------------------------------------
        
        
        if pfmetstatus: npass = npass + 1
        
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # EWK Reweighting And Top pT Reweighting--------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        genpTReweighting = 1.0 
        if isData==1:   genpTReweighting  =  1.0
        if not isData :  genpTReweighting = GenWeightProducer(samplename, nGenPar, genParId, genMomParId, genParSt,genParP4)
        
        
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        ## Pileup weight
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        allpuweights = PUWeight()
        len_puweight = len(allpuweights)
        puweight = 0.0
        if isData: puweight = 1.0 
        if not isData:
            if pu_nTrueInt  <= len_puweight: puweight = allpuweights[pu_nTrueInt-1]
            if pu_nTrueInt  > len_puweight : puweight = 0.0 
        #print (len_puweight, pu_nTrueInt, puweight)
        

        #----------------------------------------------------------------------------------------------------------------------------------------------------------------
        #----------------------------------------------------------------------------------------------------------------------------------------------------------------
        #All Weights ----------------------------------------------------------------------------------------------------------------------------------------------------
        #----------------------------------------------------------------------------------------------------------------------------------------------------------------
        #----------------------------------------------------------------------------------------------------------------------------------------------------------------
        #allweights = puweight * mcweight * genpTReweighting
        allweights = mcweight * genpTReweighting 
                
        
        ##-------------------------------------------------------------------------------------------------
        ##-------------------------------------------------------------------------------------------------
        ##------------fill all variables needed for further processing-------------------------------------
        ##-------------------------------------------------------------------------------------------------
        ##-------------------------------------------------------------------------------------------------


        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        ## BTag Scale Factor 
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        if inSR1:
            ij = ifirstjet
            jj = isecondjet
            
            flav1 = jetflav(THINjetHadronFlavor[ij])
            flav2 = jetflav(THINjetHadronFlavor[jj])

#            print ("ij, flav, pt, eta, ",ij, flav1, thinjetP4[ij].Pt(), thinjetP4[ij].Eta())
            reader1.eval_auto_bounds('central', 0, 1.2, 50.)
            sf_resolved1 = weightbtag(reader1, flav1, thinjetP4[ij].Pt(), thinjetP4[ij].Eta())
            sf_resolved2 = weightbtag(reader1, flav2, thinjetP4[jj].Pt(), thinjetP4[jj].Eta())
            
#            print (sf_resolved1, sf_resolved2)
        elif inSR2:
            ij = ifirstjet
            jj = isecondjet
            jk = ithirdjet
         
            flav1 = jetflav(THINjetHadronFlavor[ij])
            flav2 = jetflav(THINjetHadronFlavor[jj])
            flav3 = jetflav(THINjetHadronFlavor[jj])

#            print ("ij, flav, pt, eta, ",ij, flav1, thinjetP4[ij].Pt(), thinjetP4[ij].Eta())
            reader1.eval_auto_bounds('central', 0, 1.2, 50.)
            sf_resolved1 = weightbtag(reader1, flav1, thinjetP4[ij].Pt(), thinjetP4[ij].Eta())
            sf_resolved2 = weightbtag(reader1, flav2, thinjetP4[jj].Pt(), thinjetP4[jj].Eta())
            sf_resolved3 = weightbtag(reader1, flav3, thinjetP4[jk].Pt(), thinjetP4[jk].Eta())
            
#            print (sf_resolved1, sf_resolved2, sf_resolved3)
            
        if inSR1:
            allweights = allweights * sf_resolved1[0] * sf_resolved2[0]
        if inSR2:
            allweights = allweights * sf_resolved1[0] * sf_resolved2[0] * sf_resolved3[0]
       
        if isData: allweights = 1.0 
        allquantities.met        = pfMet

        allquantities.N_e             = len(myEles)
        allquantities.N_mu            = len(myMuos)
        allquantities.N_tau           = len(myTaus)
        allquantities.N_Pho           = 0
        allquantities.N_b             = len(mybjets)
        allquantities.N_j             = nTHINJets

        allquantities.weight    = allweights
        allquantities.totalevents = 1
        
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
                           allquantlist.append(lep+"1_"+lepprop+region+nSR)
                if lep=='el':
                  for lepprop in props:
                     for nCR in ['1','2']:       # For ZCR, because Z has 2 mu or 2 ele
                           allquantlist.append(lep+nCR+"_"+lepprop+"_Zeecr"+nSR)
                     for region in ['Wecr','Wmucr','TOPcr']:          # For ZCR, only 1 mu and/or ele
                           allquantlist.append(lep+"1_"+lepprop+region+nSR)        
                    
        allquantlist+=['ZhadronRecoil1mumu','ZhadronRecoil1ee','Zmass1mumu','Zmass1ee','ZpT1mumu','ZpT1ee','WhadronRecoil1mu','WhadronRecoil1e','Wmass1mu','Wmass1e','WpT1','TOPRecoil1','ZhadronRecoil2mumu','ZhadronRecoil2ee','Zmass2mumu','Zmass2ee','ZpT2mumu','ZpT2ee','WhadronRecoil2mu','WhadronRecoil2e','Wmass2mu','Wmass2e','WpT2mu','WpT2e','TOPRecoil2']
        
        for quant in allquantlist:
            exec("allquantities."+quant+" = None")                              # Presets all quantities to None  
                 
        if inSR1:            
           allquantities.jet1_pT_sr1     = jetSR1Info[0][0]
           allquantities.jet1_eta_sr1    = jetSR1Info[0][1]
           allquantities.jet1_phi_sr1    = jetSR1Info[0][2]
           allquantities.jet1_csv_sr1    = jetSR1Info[0][3]
           allquantities.jet2_pT_sr1     = jetSR1Info[1][0]
           allquantities.jet2_eta_sr1    = jetSR1Info[1][1]
           allquantities.jet2_phi_sr1    = jetSR1Info[1][2]
           allquantities.jet2_csv_sr1    = jetSR1Info[1][3]
           allquantities.min_dPhi_sr1    = jetSR1Info[2]
           
        elif inSR2:
           allquantities.jet1_pT_sr2     = jetSR2Info[0][0]
           allquantities.jet1_eta_sr2    = jetSR2Info[0][1]
           allquantities.jet1_phi_sr2    = jetSR2Info[0][2]
           allquantities.jet1_csv_sr2    = jetSR2Info[0][3]
           allquantities.jet2_pT_sr2     = jetSR2Info[1][0]
           allquantities.jet2_eta_sr2    = jetSR2Info[1][1]
           allquantities.jet2_phi_sr2    = jetSR2Info[1][2]
           allquantities.jet2_csv_sr2    = jetSR2Info[1][3]
           allquantities.jet3_pT_sr2     = jetSR2Info[2][0]
           allquantities.jet3_eta_sr2    = jetSR2Info[2][1]
           allquantities.jet3_phi_sr2    = jetSR2Info[2][2]
           allquantities.jet3_csv_sr2    = jetSR2Info[2][3]
           allquantities.min_dPhi_sr2    = jetSR2Info[3]
           
        else:
            continue       
           
        ## to fill for ZCR
        if inSR1 and zCR:
           if zCRMu:
               allquantities.jet1_pT_Zmumucr1     = jetSR1Info[0][0]
               allquantities.jet1_eta_Zmumucr1    = jetSR1Info[0][1]
               allquantities.jet1_phi_Zmumucr1    = jetSR1Info[0][2]
               allquantities.jet1_csv_Zmumucr1    = jetSR1Info[0][3]
               allquantities.jet2_pT_Zmumucr1     = jetSR1Info[1][0]
               allquantities.jet2_eta_Zmumucr1    = jetSR1Info[1][1]
               allquantities.jet2_phi_Zmumucr1    = jetSR1Info[1][2]
               allquantities.jet2_csv_Zmumucr1    = jetSR1Info[1][3]
               allquantities.ZhadronRecoil1mumu    = hadrecoil
               allquantities.Zmass1mumu            = zmass
               allquantities.ZpT1mumu              = ZpT
               allquantities.mu1_pT_Zmumucr1       = Zmu1pT
               allquantities.mu2_pT_Zmumucr1       = Zmu2pT
               allquantities.mu1_eta_Zmumucr1      = Zmu1eta
               allquantities.mu2_eta_Zmumucr1      = Zmu2eta
               allquantities.mu1_phi_Zmumucr1      = Zmu1phi
               allquantities.mu2_phi_Zmumucr1      = Zmu2phi
               allquantities.mu1_iso_Zmumucr1      = Zmu1Iso
               allquantities.mu2_iso_Zmumucr1      = Zmu2Iso
           if zCREle:
               allquantities.jet1_pT_Zeecr1     = jetSR1Info[0][0]
               allquantities.jet1_eta_Zeecr1    = jetSR1Info[0][1]
               allquantities.jet1_phi_Zeecr1    = jetSR1Info[0][2]
               allquantities.jet1_csv_Zeecr1    = jetSR1Info[0][3]
               allquantities.jet2_pT_Zeecr1     = jetSR1Info[1][0]
               allquantities.jet2_eta_Zeecr1    = jetSR1Info[1][1]
               allquantities.jet2_phi_Zeecr1    = jetSR1Info[1][2]
               allquantities.jet2_csv_Zeecr1    = jetSR1Info[1][3]
               allquantities.ZhadronRecoil1ee    = hadrecoil
               allquantities.Zmass1ee            = zmass
               allquantities.ZpT1ee              = ZpT
               allquantities.el1_pT_Zeecr1       = Zele1pT
               allquantities.el2_pT_Zeecr1       = Zele2pT
               allquantities.el1_eta_Zeecr1      = Zele1eta
               allquantities.el2_eta_Zeecr1      = Zele2eta
               allquantities.el1_phi_Zeecr1      = Zele1phi
               allquantities.el2_phi_Zeecr1      = Zele2phi
        
        elif inSR2 and zCR:
           if zCRMu:
               allquantities.jet1_pT_Zmumucr2     = jetSR2Info[0][0]
               allquantities.jet1_eta_Zmumucr2    = jetSR2Info[0][1]
               allquantities.jet1_phi_Zmumucr2    = jetSR2Info[0][2]
               allquantities.jet1_csv_Zmumucr2    = jetSR2Info[0][3]
               allquantities.jet2_pT_Zmumucr2     = jetSR2Info[1][0]
               allquantities.jet2_eta_Zmumucr2    = jetSR2Info[1][1]
               allquantities.jet2_phi_Zmumucr2    = jetSR2Info[1][2]
               allquantities.jet2_csv_Zmumucr2    = jetSR2Info[1][3]
               allquantities.jet3_pT_Zmumucr2     = jetSR2Info[2][0]
               allquantities.jet3_eta_Zmumucr2    = jetSR2Info[2][1]
               allquantities.jet3_phi_Zmumucr2    = jetSR2Info[2][2]
               allquantities.jet3_csv_Zmumucr2    = jetSR2Info[2][3]
               allquantities.ZhadronRecoil2mumu    = hadrecoil
               allquantities.Zmass2mumu            = zmass
               allquantities.ZpT2mumu              = ZpT
               allquantities.mu1_pT_Zmumucr2       = Zmu1pT
               allquantities.mu2_pT_Zmumucr2       = Zmu2pT
               allquantities.mu1_eta_Zmumucr2      = Zmu1eta
               allquantities.mu2_eta_Zmumucr2      = Zmu2eta
               allquantities.mu1_phi_Zmumucr2      = Zmu1phi
               allquantities.mu2_phi_Zmumucr2      = Zmu2phi
               allquantities.mu1_iso_Zmumucr2      = Zmu1Iso
               allquantities.mu2_iso_Zmumucr2      = Zmu2Iso
           if zCREle:
               allquantities.jet1_pT_Zeecr2     = jetSR2Info[0][0]
               allquantities.jet1_eta_Zeecr2    = jetSR2Info[0][1]
               allquantities.jet1_phi_Zeecr2    = jetSR2Info[0][2]
               allquantities.jet1_csv_Zeecr2    = jetSR2Info[0][3]
               allquantities.jet2_pT_Zeecr2     = jetSR2Info[1][0]
               allquantities.jet2_eta_Zeecr2    = jetSR2Info[1][1]
               allquantities.jet2_phi_Zeecr2    = jetSR2Info[1][2]
               allquantities.jet2_csv_Zeecr2    = jetSR2Info[1][3]
               allquantities.jet3_pT_Zeecr2     = jetSR2Info[2][0]
               allquantities.jet3_eta_Zeecr2    = jetSR2Info[2][1]
               allquantities.jet3_phi_Zeecr2    = jetSR2Info[2][2]
               allquantities.jet3_csv_Zeecr2    = jetSR2Info[2][3]
               allquantities.ZhadronRecoil2ee    = hadrecoil
               allquantities.Zmass2ee            = zmass
               allquantities.ZpT2ee              = ZpT
               allquantities.el1_pT_Zeecr2       = Zele1pT
               allquantities.el2_pT_Zeecr2       = Zele2pT
               allquantities.el1_eta_Zeecr2      = Zele1eta
               allquantities.el2_eta_Zeecr2      = Zele2eta
               allquantities.el1_phi_Zeecr2      = Zele1phi
               allquantities.el2_phi_Zeecr2      = Zele2phi
           
        ##To fill WCR region
        if inSR1 and wCR:
           if wCRMu:
               allquantities.jet1_pT_Wmucr1     = jetSR1Info[0][0]
               allquantities.jet1_eta_Wmucr1    = jetSR1Info[0][1]
               allquantities.jet1_phi_Wmucr1    = jetSR1Info[0][2]
               allquantities.jet1_csv_Wmucr1    = jetSR1Info[0][3]
               allquantities.jet2_pT_Wmucr1     = jetSR1Info[1][0]
               allquantities.jet2_eta_Wmucr1    = jetSR1Info[1][1]
               allquantities.jet2_phi_Wmucr1    = jetSR1Info[1][2]
               allquantities.jet2_csv_Wmucr1    = jetSR1Info[1][3]
               allquantities.WhadronRecoil1mu    = hadrecoil
               allquantities.Wmass1mu            = wmass
               allquantities.WpT1mu              = WpT
               allquantities.mu1_pT_Wmucr1       = Wmu1pT
               allquantities.mu1_eta_Wmucr1      = Wmu1eta
               allquantities.mu1_phi_Wmucr1      = Wmu1phi
               allquantities.mu1_iso_Wmucr1      = Wmu1Iso
           if wCREle:
               allquantities.jet1_pT_Wecr1     = jetSR1Info[0][0]
               allquantities.jet1_eta_Wecr1    = jetSR1Info[0][1]
               allquantities.jet1_phi_Wecr1    = jetSR1Info[0][2]
               allquantities.jet1_csv_Wecr1    = jetSR1Info[0][3]
               allquantities.jet2_pT_Wecr1     = jetSR1Info[1][0]
               allquantities.jet2_eta_Wecr1    = jetSR1Info[1][1]
               allquantities.jet2_phi_Wecr1    = jetSR1Info[1][2]
               allquantities.jet2_csv_Wecr1    = jetSR1Info[1][3]
               allquantities.WhadronRecoil1e    = hadrecoil
               allquantities.Wmass1e            = wmass
               allquantities.WpT1e              = WpT
               allquantities.el1_pT_Wecr1       = Wele1pT
               allquantities.el1_eta_Wecr1      = Wele1eta
               allquantities.el1_phi_Wecr1      = Wele1phi
        
        elif inSR2 and wCR:
           if wCRMu:
               allquantities.jet1_pT_Wmucr2     = jetSR2Info[0][0]
               allquantities.jet1_eta_Wmucr2    = jetSR2Info[0][1]
               allquantities.jet1_phi_Wmucr2    = jetSR2Info[0][2]
               allquantities.jet1_csv_Wmucr2    = jetSR2Info[0][3]
               allquantities.jet2_pT_Wmucr2     = jetSR2Info[1][0]
               allquantities.jet2_eta_Wmucr2    = jetSR2Info[1][1]
               allquantities.jet2_phi_Wmucr2    = jetSR2Info[1][2]
               allquantities.jet2_csv_Wmucr2    = jetSR2Info[1][3]
               allquantities.jet3_pT_Wmucr2     = jetSR2Info[2][0]
               allquantities.jet3_eta_Wmucr2    = jetSR2Info[2][1]
               allquantities.jet3_phi_Wmucr2    = jetSR2Info[2][2]
               allquantities.jet3_csv_Wmucr2    = jetSR2Info[2][3]
               allquantities.WhadronRecoil2mu    = hadrecoil
               allquantities.Wmass2mu            = wmass
               allquantities.WpT2mu              = WpT
               allquantities.mu1_pT_Wmucr2       = Wmu1pT
               allquantities.mu1_eta_Wmucr2      = Wmu1eta
               allquantities.mu1_phi_Wmucr2      = Wmu1phi
               allquantities.mu1_iso_Wmucr2      = Wmu1Iso
           if wCREle:
               allquantities.jet1_pT_Wecr2     = jetSR2Info[0][0]
               allquantities.jet1_eta_Wecr2    = jetSR2Info[0][1]
               allquantities.jet1_phi_Wecr2    = jetSR2Info[0][2]
               allquantities.jet1_csv_Wecr2    = jetSR2Info[0][3]
               allquantities.jet2_pT_Wecr2     = jetSR2Info[1][0]
               allquantities.jet2_eta_Wecr2    = jetSR2Info[1][1]
               allquantities.jet2_phi_Wecr2    = jetSR2Info[1][2]
               allquantities.jet2_csv_Wecr2    = jetSR2Info[1][3]
               allquantities.jet3_pT_Wecr2     = jetSR2Info[2][0]
               allquantities.jet3_eta_Wecr2    = jetSR2Info[2][1]
               allquantities.jet3_phi_Wecr2    = jetSR2Info[2][2]
               allquantities.jet3_csv_Wecr2    = jetSR2Info[2][3]
               allquantities.WhadronRecoil2e    = hadrecoil
               allquantities.Wmass2e            = wmass
               allquantities.WpT2e              = WpT
               allquantities.el1_pT_Wecr2       = Wele1pT
               allquantities.el1_eta_Wecr2      = Wele1eta
               allquantities.el1_phi_Wecr2      = Wele1phi
        
        ##For TopCR region
        if inSR1 and TopCR:
           allquantities.jet1_pT_TOPcr1     = jetSR1Info[0][0]
           allquantities.jet1_eta_TOPcr1    = jetSR1Info[0][1]
           allquantities.jet1_phi_TOPcr1    = jetSR1Info[0][2]
           allquantities.jet1_csv_TOPcr1    = jetSR1Info[0][3]
           allquantities.jet2_pT_TOPcr1     = jetSR1Info[1][0]
           allquantities.jet2_eta_TOPcr1    = jetSR1Info[1][1]
           allquantities.jet2_phi_TOPcr1    = jetSR1Info[1][2]
           allquantities.jet2_csv_TOPcr1    = jetSR1Info[1][3]
           allquantities.TOPRecoil1          = TOPRecoil  
           allquantities.mu1_pT_TOPcr1       = TOPmu1pT
           allquantities.el1_pT_TOPcr1       = TOPele1pT
           allquantities.mu1_eta_TOPcr1      = TOPmu1eta
           allquantities.el1_eta_TOPcr1      = TOPele1eta
           allquantities.mu1_phi_TOPcr1      = TOPmu1phi
           allquantities.el1_phi_TOPcr1      = TOPele1phi
           allquantities.mu1_iso_TOPcr1      = TOPmu1Iso
           
        elif inSR2 and TopCR:
           allquantities.jet1_pT_TOPcr2     = jetSR2Info[0][0]
           allquantities.jet1_eta_TOPcr2    = jetSR2Info[0][1]
           allquantities.jet1_phi_TOPcr2    = jetSR2Info[0][2]
           allquantities.jet1_csv_TOPcr2    = jetSR2Info[0][3]
           allquantities.jet2_pT_TOPcr2     = jetSR2Info[1][0]
           allquantities.jet2_eta_TOPcr2    = jetSR2Info[1][1]
           allquantities.jet2_phi_TOPcr2    = jetSR2Info[1][2]
           allquantities.jet2_csv_TOPcr2    = jetSR2Info[1][3]
           allquantities.jet3_pT_TOPcr2     = jetSR2Info[2][0]
           allquantities.jet3_eta_TOPcr2    = jetSR2Info[2][1]
           allquantities.jet3_phi_TOPcr2    = jetSR2Info[2][2]
           allquantities.jet3_csv_TOPcr2    = jetSR2Info[2][3]
           allquantities.TOPRecoil2          = TOPRecoil
           allquantities.mu1_pT_TOPcr2       = TOPmu1pT
           allquantities.el1_pT_TOPcr2       = TOPele1pT
           allquantities.mu1_eta_TOPcr2      = TOPmu1eta
           allquantities.el1_eta_TOPcr2      = TOPele1eta
           allquantities.mu1_phi_TOPcr2      = TOPmu1phi
           allquantities.el1_phi_TOPcr2      = TOPele1phi
           allquantities.mu1_iso_TOPcr2      = TOPmu1Iso
           

            
        #print (allquantities.regime, allquantities.met,allquantities.mass )
        allquantities.FillHisto()
        
        
    

    #print cutStatus    
    NEntries_Weight = h_t_weight.Integral()
    NEntries_total  = h_t.Integral()
    cutStatus['total'] = int(NEntries_total)
    cutStatusSR1['total'] = int(NEntries_total)
    cutStatusSR2['total'] = int(NEntries_total)
    cutStatusSR1['pfmet'] = cutStatus['pfmet']
    cutStatusSR2['pfmet'] = cutStatus['pfmet']
    print "Total events =", cutStatus['total']
    print "Preselected events=", cutStatus['preselection']
    print "Selected events =", npass
    
    # Cutflow
    cutflowTable=""
    cutflowHeader=""
    cutflowvalues=[]    
    cutflownames=['total','preselection','pfmet','isinSR','jet1','jet2/3','btaggedjet']
    for cutflowname in cutflownames:   
        cutflowvalues.append(cutStatus[cutflowname])
        cutflowTable += str(cutStatus[cutflowname])+" "
        cutflowHeader += cutflowname+" "    
    
    cutflowvaluesSR1=[]
    cutflownamesSR1=['total','preselection','pfmet','njet','jet1','jet2','btaggedjet']
    for cutflowname in cutflownamesSR1:   
        cutflowvaluesSR1.append(cutStatusSR1[cutflowname])
        
    cutflowvaluesSR2=[]
    cutflownamesSR2=['total','preselection','pfmet','njet','jet1','jet2','jet3','btaggedjet1','btaggedjet2']
    for cutflowname in cutflownamesSR2:   
        cutflowvaluesSR2.append(cutStatusSR2[cutflowname])
    
    # CR counts
    CRTable=""
    CRHeader=""
    CRvalues=[]
    for CRname in CRs:   
        CRvalues.append(CRStatus[CRname])
        CRTable += str(CRStatus[CRname])+" "
        CRHeader += CRname+" "
    
    #Cutflows for SR1 and SR2
    print "\nCutflow:"
    print cutStatus
    print
    print "SR1:"
    print cutStatusSR1
    print
    print "SR2:"
    print cutStatusSR2
    print   
    
    allquantities.WriteHisto((NEntries_total,NEntries_Weight,cutflowvalues,cutflownames,cutflowvaluesSR1,cutflownamesSR1,cutflowvaluesSR2,cutflownamesSR2,CRvalues,CRs))
    
    if NEntries > 0:
        eff=round(float(npass/float(NEntries)),5)
    else:
        eff = "NA"
    print "efficiency =", eff  
    
    os.system("mkdir -p "+outputdir+'/efficiencyfiles/')
        
    f = open(outputdir+'/efficiencyfiles/'+textfile, 'w')
    f.write(str(eff)+"\n\n#Cutflow Table:\n"+cutflowHeader[:-1]+"\n"+cutflowTable[:-1]+"\n\n#CR Table:\n"+CRHeader[:-1]+"\n"+CRTable[:-1])
    print "ROOT file written to", outfilename
    print "Log written to "+outputdir+'/efficiencyfiles/'+textfile
    f.close()
    print "Completed."



        
def CheckFilter(filterName, filterResult,filtercompare):
    ifilter_=0
    filter1 = False
    for ifilter in filterName:
        filter1 = (ifilter.find(filtercompare) != -1)  & (bool(filterResult[ifilter_]) == True)   
        if filter1: break
        ifilter_ = ifilter_ + 1
    return filter1





######################################
######################################
######################################
def MakeTable():
    print "called MakeTable"
    files= [inputfilename]
    legend=legendTemplate
    prefix="V_met_"
    effnamelist = [prefix + ihisto  for ihisto in namelist]
    inputfile={}
    histList=[]
    for ifile_ in range(len(files)):
        print ("opening file  "+files[ifile_])
        inputfile[ifile_] = TFile( files[ifile_] )
        print "fetching histograms"
        for ihisto_ in range(len(effnamelist)):
            histo = inputfile[ifile_].Get(effnamelist[ihisto_])
            histList.append(histo)
    
    for ih in range(len(histList)):
        eff = ("%0.4f" % float(histList[ih].Integral()/histList[0].Integral()))
        toprint =  legendTemplate[ih] + " & " + str(eff) + " \\\\"
        print toprint


def DeltaR(p4_1, p4_2):
    eta1 = p4_1.Eta()
    eta2 = p4_2.Eta()
    eta = eta1 - eta2
    eta_2 = eta * eta
    
    phi1 = p4_1.Phi()
    phi2 = p4_2.Phi()
    phi = Phi_mpi_pi(phi1-phi2)
    phi_2 = phi * phi

    return math.sqrt(eta_2 + phi_2)
    
def DeltaPhi(phi1,phi2):
   phi = Phi_mpi_pi(phi1-phi2)
   
   return abs(phi)
   
    
def Phi_mpi_pi(x):
    kPI = 3.14159265358979323846
    kTWOPI = 2 * kPI
    
    while (x >= kPI): x = x - kTWOPI;
    while (x < -kPI): x = x + kTWOPI;
    return x;
    
def weightbtag(reader, flav, pt, eta):
    sf_c = reader.eval_auto_bounds('central', flav, eta, pt) 
    sf_low = reader.eval_auto_bounds('down', flav, eta, pt)
    sf_up  = reader.eval_auto_bounds('up', flav, eta, pt)
    btagsf = [sf_c, sf_low, sf_up]
    return btagsf

def jetflav(flav):
    if flav == 5: 
        flavor = 0
    elif flav == 4:
        flavor = 1
    else:
        flavor = 2
    return flavor




def GenWeightProducer(sample,nGenPar, genParId, genMomParId, genParSt,genParP4):
    pt__=0;
    #print " inside gen weight "
    k2=1.0
    #################
    # WJets
    #################
    if sample=="WJETS":
        goodLepID = []
        for ig in range(nGenPar): 
            PID    = genParId[ig]
            momPID = genMomParId[ig]
            status = genParSt[ig]
            if ( (abs(PID) != 11) & (abs(PID) != 12) &  (abs(PID) != 13) & (abs(PID) != 14) &  (abs(PID) != 15) &  (abs(PID) != 16) ): continue
            if ( ( (status != 1) & (abs(PID) != 15)) | ( (status != 2) & (abs(PID) == 15)) ): continue
            if ( (abs(momPID) != 24) & (momPID != PID) ): continue
            goodLepID.append(ig)

        if len(goodLepID) == 2 :
            l4_thisLep = genParP4[goodLepID[0]]
            l4_thatLep = genParP4[goodLepID[1]]
            l4_z = l4_thisLep + l4_thatLep
            
            pt = l4_z.Pt()
            pt__ = pt

            k2 = -0.830041 + 7.93714 *TMath.Power( pt - (-877.978) ,(-0.213831) ) ;
    
    #################        
    #ZJets
    #################
    if sample == "ZJETS":
        goodLepID = []
        for ig in range(nGenPar):
            PID    = genParId[ig]
            momPID = genMomParId[ig]
            status = genParSt[ig]


            if ( (abs(PID) != 12) &  (abs(PID) != 14) &  (abs(PID) != 16) ) : continue
            if ( status != 1 ) : continue 
            if ( (momPID != 23) & (momPID != PID) ) : continue
            goodLepID.append(ig)
        
        if len(goodLepID) == 2 :
            l4_thisLep = genParP4[goodLepID[0]]
            l4_thatLep = genParP4[goodLepID[1]]
            l4_z = l4_thisLep + l4_thatLep
            pt = l4_z.Pt()
            k2 = -0.180805 + 6.04146 *TMath.Power( pt - (-759.098) ,(-0.242556) ) ;

    #################        
    #TTBar
    #################        
    if (sample=="TT"):
        goodLepID = []
        for ig in range(nGenPar):
            PID    = genParId[ig]
            momPID = genMomParId[ig]
            status = genParSt[ig]
            if ( abs(PID) == 6) :
                goodLepID.append(ig)
        if(len(goodLepID)==2):
            l4_thisLep = genParP4[goodLepID[0]]
            l4_thatLep = genParP4[goodLepID[1]]
            pt1 = TMath.Min(400.0, l4_thisLep.Pt())
            pt2 = TMath.Min(400.0, l4_thatLep.Pt())
            
            w1 = TMath.Exp(0.156 - 0.00137*pt1);
            w2 = TMath.Exp(0.156 - 0.00137*pt2);
            k2 =  1.001*TMath.Sqrt(w1*w2);
            
    if(sample=="all"):
        k2 = 1.0
        
    return k2


def MT(Pt, met, dphi):
    return ROOT.TMath.Sqrt( 2 * Pt * met * (1.0 - ROOT.TMath.Cos(dphi)) )

if __name__ == "__main__":
    ## analyze the tree and make histograms and all the 2D plots and Efficiency plots. 
    if options.analyze:
        print "now calling analyzedataset"
        AnalyzeDataSet()
    
    
    

