#!/usr/bin/env python
from ROOT import TFile, TTree, TH1F, TH1D, TH1, TCanvas, TChain,TGraphAsymmErrors, TMath, TH2D, TLorentzVector, AddressOf, gROOT
import ROOT as ROOT
import os
import sys, optparse
from array import array
import math
import numpy as numpy_

ROOT.gROOT.LoadMacro("Loader.h+")

#to find which sample is being used
#def WhichSample(filename):
#    samplename = 'all'
#    if filename.find('WJets')>-1:
#        samplename = 'WJETS'
#    elif filename.find('ZJets')>-1:
#        samplename = 'ZJETS'
#    elif filename.find('TT')>-1:
#        samplename  = 'TT'
#    else:
#        samplename = 'all'
#    return samplename   
    
    
## When not running on farmout
#inputfilename= 'FileList.txt' uncomment it for providing list of file
outfilename= 'SkimmedTree.root'
PUPPI = True
CA15  = False

## When running on farmout
#inputfilename = os.environ['INPUT']                                                                                                                                                 
#outfilename   = os.environ['OUTPUT']                                                                                                                                                


skimmedTree = TChain("tree/treeMaker")
##======use this for providing list of file======##
#infile = open(inputfilename)
#for ifile in infile: 
#    skimmedTree.Add(ifile.rstrip())
#    samplename = WhichSample(inputfilename)
##======use this for providing list of file======##
skimmedTree.Add(sys.argv[1])
#samplename = WhichSample(sys.argv[1])

    
def AnalyzeDataSet():
    NEntries = skimmedTree.GetEntries()
    
    h_total = TH1F('h_total','h_total',2,0,2)
    h_total_mcweight = TH1F('h_total_mcweight','h_total_mcweight',2,0,2)
    
    outfile = TFile(outfilename,'RECREATE')
    
    outTree = TTree( 'outTree', 'tree branches' )
    st_runId            = numpy_.zeros(1, dtype=int)
    st_lumiSection      = array( 'L', [ 0 ] )
    st_eventId          = array( 'L', [ 0 ] )
    st_pfMetCorrPt      = array( 'f', [ 0. ] )
    st_pfMetCorrPhi     = array( 'f', [ 0. ] )
    st_isData           = array( 'b', [ 0 ] )
    
    maxn = 10
    
    st_THINnJet            = array( 'L', [ 0 ] ) #ROOT.std.vector('int')()
    st_THINjetP4           = ROOT.std.vector('TLorentzVector')()
    st_THINjetCISVV2       = ROOT.std.vector('float')()
    st_THINjetHadronFlavor = ROOT.std.vector('int')()
    st_THINjetNHadEF       = ROOT.std.vector('float')()
    st_THINjetCHadEF       = ROOT.std.vector('float')()
    
    
    st_nEle                = array( 'L', [ 0 ] ) #ROOT.std.vector('int')()
    st_eleP4               = ROOT.std.vector('TLorentzVector')()
    st_eleIsPassLoose      = ROOT.std.vector('bool')()
    st_eleIsPassMedium     = ROOT.std.vector('bool')()
    st_eleIsPassTight      = ROOT.std.vector('bool')()
    
    st_nMu= array( 'L', [ 0 ] ) #ROOT.std.vector('int')()
    st_muP4                = ROOT.std.vector('TLorentzVector')()
    st_isLooseMuon         = ROOT.std.vector('bool')()
    st_isMediumMuon        = ROOT.std.vector('bool')()
    st_isTightMuon         = ROOT.std.vector('bool')()
    st_muChHadIso          = ROOT.std.vector('float')()
    st_muNeHadIso          = ROOT.std.vector('float')()
    st_muGamIso            = ROOT.std.vector('float')()
    st_muPUPt              = ROOT.std.vector('float')()
    st_muCharge            = ROOT.std.vector('int')()
    
    
    st_HPSTau_n= array( 'L', [ 0 ] ) #ROOT.std.vector('int')()
    st_HPSTau_4Momentum= ROOT.std.vector('TLorentzVector')()
    
    mcweight = array( 'f', [ 0 ] )
    st_pu_nTrueInt= array( 'f', [ 0 ] ) #ROOT.std.vector('std::vector<float>')()
    
    st_nGenPar = array( 'L', [ 0 ] ) 
    st_genParId = ROOT.std.vector('int')()
    st_genMomParId = ROOT.std.vector('int')()
    st_genParSt = ROOT.std.vector('int')()
    st_genParP4 = ROOT.std.vector('TLorentzVector')()
    
    WenuRecoil = array( 'f', [ 0. ] )
    Wenumass = array( 'f', [ 0. ] )
    
    WmunuRecoil = array( 'f', [ 0. ] )
    Wmunumass = array( 'f', [ 0. ] )
    
    ZeeRecoil = array( 'f', [ 0. ] )
    ZeeMass = array( 'f', [ 0. ] )
    
    ZmumuRecoil = array( 'f', [ 0. ] )
    ZmumuMass = array( 'f', [ 0. ] )
    
    TOPRecoil = array( 'f', [ 0. ] )
           
    outTree.Branch( 'st_runId', st_runId , 'st_runId/L')
    outTree.Branch( 'st_lumiSection', st_lumiSection , 'st_lumiSection/L')
    outTree.Branch( 'st_eventId',  st_eventId, 'st_eventId/L')
    outTree.Branch( 'st_pfMetCorrPt', st_pfMetCorrPt , 'st_pfMetCorrPt/F')
    outTree.Branch( 'st_pfMetCorrPhi', st_pfMetCorrPhi , 'st_pfMetCorrPhi/F')
    outTree.Branch( 'st_isData', st_isData , 'st_isData/O')
    
    outTree.Branch( 'st_THINnJet',st_THINnJet, 'st_THINnJet/L' ) 
    outTree.Branch( 'st_THINjetP4',st_THINjetP4 ) 
    outTree.Branch( 'st_THINjetCISVV2',st_THINjetCISVV2 ) 
    outTree.Branch( 'st_THINjetHadronFlavor',st_THINjetHadronFlavor ) 
    outTree.Branch( 'st_THINjetNHadEF',st_THINjetNHadEF )
    outTree.Branch( 'st_THINjetCHadEF',st_THINjetCHadEF )
    
    outTree.Branch( 'st_nEle',st_nEle , 'st_nEle/L') 
    outTree.Branch( 'st_eleP4',st_eleP4 )
    outTree.Branch( 'st_eleIsPassLoose', st_eleIsPassLoose)#, 'st_eleIsPassLoose/O' )
    outTree.Branch( 'st_eleIsPassMedium', st_eleIsPassMedium)#, 'st_eleIsPassMedium/O' )
    outTree.Branch( 'st_eleIsPassTight', st_eleIsPassTight)#, 'st_eleIsPassTight/O' )
                   
    outTree.Branch( 'st_nMu',st_nMu , 'st_nMu/L') 
    outTree.Branch( 'st_muP4',st_muP4 ) 
    outTree.Branch( 'st_isLooseMuon', st_isLooseMuon)#, 'st_isLooseMuon/O' )
    outTree.Branch( 'st_isMediumMuon', st_isMediumMuon)#, 'st_isMediumMuon/O' )
    outTree.Branch( 'st_isTightMuon', st_isTightMuon)#, 'st_isTightMuon/O' )
    outTree.Branch( 'st_muChHadIso', st_muChHadIso)#, 'st_muChHadIso/F')
    outTree.Branch( 'st_muNeHadIso', st_muNeHadIso)#, 'st_muNeHadIso/F')
    outTree.Branch( 'st_muGamIso', st_muGamIso)#, 'st_muGamIso/F')
    outTree.Branch( 'st_muPUPt', st_muPUPt)#, 'st_muPUPt/F')
    
    outTree.Branch( 'st_HPSTau_n', st_HPSTau_n, 'st_HPSTau_n/L') 
    outTree.Branch( 'st_HPSTau_4Momentum', st_HPSTau_4Momentum) 
    
    outTree.Branch( 'st_pu_nTrueInt', st_pu_nTrueInt, 'st_pu_nTrueInt/L') 
    outTree.Branch( 'mcweight', mcweight, 'mcweight/F')
    outTree.Branch( 'st_nGenPar',st_nGenPar,'st_nGenPar/L' )  #nGenPar/I
    outTree.Branch( 'st_genParId',st_genParId )  #vector<int>
    outTree.Branch( 'st_genMomParId',st_genMomParId ) 
    outTree.Branch( 'st_genParSt',st_genParSt ) 
    outTree.Branch( 'st_genParP4', st_genParP4) 
    
    outTree.Branch( 'WenuRecoil', WenuRecoil, 'WenuRecoil/F')
    outTree.Branch( 'Wenumass', Wenumass, 'Wenumass/F')
    
    outTree.Branch( 'WmunuRecoil', WmunuRecoil, 'WmunuRecoil/F')
    outTree.Branch( 'Wmunumass', Wmunumass, 'Wmunumass/F')
    
    outTree.Branch( 'ZeeRecoil', ZeeRecoil, 'ZeeRecoil/F')
    outTree.Branch( 'ZeeMass', ZeeMass, 'ZeeMass/F')
    
    outTree.Branch( 'ZmumuRecoil', ZmumuRecoil, 'ZmumuRecoil/F')
    outTree.Branch( 'ZmumuMass', ZmumuMass, 'ZmumuMass/F')
    
    outTree.Branch( 'TOPRecoil', TOPRecoil, 'TOPRecoil/F')

    
    for ievent in range(NEntries):
        skimmedTree.GetEntry(ievent)
        ## Get all relevant branches
        run                        = skimmedTree.__getattr__('runId')
        lumi                       = skimmedTree.__getattr__('lumiSection')
        event                      = skimmedTree.__getattr__('eventId')
        print "Run:"+str(run)+"; Lumi:"+str(lumi)+"; Event:"+str(event)
        trigName                   = skimmedTree.__getattr__('hlt_trigName')
        trigResult                 = skimmedTree.__getattr__('hlt_trigResult')
        filterName                 = skimmedTree.__getattr__('hlt_filterName')
        filterResult               = skimmedTree.__getattr__('hlt_filterResult')
        
        
        pfMet                      = skimmedTree.__getattr__('pfMetCorrPt')
        pfMetPhi                   = skimmedTree.__getattr__('pfMetCorrPhi')
        
        
        nTHINJets                  = skimmedTree.__getattr__('THINnJet')
        thinjetP4                  = skimmedTree.__getattr__('THINjetP4')
        thinJetCSV                 = skimmedTree.__getattr__('THINjetCISVV2')
        passThinJetLooseID         = skimmedTree.__getattr__('THINjetPassIDLoose')
        THINjetHadronFlavor        = skimmedTree.__getattr__('THINjetHadronFlavor')
        thinjetNhadEF              = skimmedTree.__getattr__('THINjetNHadEF')
        thinjetChadEF              = skimmedTree.__getattr__('THINjetCHadEF')
        
        
        nEle                       = skimmedTree.__getattr__('nEle')
        eleP4                      = skimmedTree.__getattr__('eleP4')
        eleIsPassLoose             = skimmedTree.__getattr__('eleIsPassLoose')
        eleIsPassMedium            = skimmedTree.__getattr__('eleIsPassMedium')
        eleIsPassTight             = skimmedTree.__getattr__('eleIsPassTight')
        eleCharge                  = skimmedTree.__getattr__('eleCharge')
        
        nMu                        = skimmedTree.__getattr__('nMu')
        muP4                       = skimmedTree.__getattr__('muP4')
        isLooseMuon                = skimmedTree.__getattr__('isLooseMuon')
        isMediumMuon               = skimmedTree.__getattr__('isMediumMuon')
        isTightMuon                = skimmedTree.__getattr__('isTightMuon')
        muChHadIso                 = skimmedTree.__getattr__('muChHadIso')
        muNeHadIso                 = skimmedTree.__getattr__('muNeHadIso')
        muGamIso                   = skimmedTree.__getattr__('muGamIso')
        muPUPt                     = skimmedTree.__getattr__('muPUPt')
        muCharge                   = skimmedTree.__getattr__('muCharge')
        
        nTau                       = skimmedTree.__getattr__('HPSTau_n')
        tauP4                      = skimmedTree.__getattr__('HPSTau_4Momentum')
        isDecayModeFinding         = skimmedTree.__getattr__('disc_decayModeFinding')
        passLooseTauIso            = skimmedTree.__getattr__('disc_byLooseIsolationMVA3oldDMwLT')
        isData                     = skimmedTree.__getattr__('isData')
        mcWeight                   = skimmedTree.__getattr__('mcWeight')
        pu_nTrueInt                = int(skimmedTree.__getattr__('pu_nTrueInt'))
        
        nGenPar                    = skimmedTree.__getattr__('nGenPar')
        genParId                   = skimmedTree.__getattr__('genParId')
        genMomParId                = skimmedTree.__getattr__('genMomParId')
        genParSt                   = skimmedTree.__getattr__('genParSt')
        genParP4                   = skimmedTree.__getattr__('genParP4')
                     
        
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # MC Weights ----------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        mcweight[0] = 0.0 
        if isData==1:   mcweight[0] =  1.0
        if not isData :
            if mcWeight<0:  mcweight[0] = -1.0
            if mcWeight>0:  mcweight[0] =  1.0
        

        h_total.Fill(1.);
        h_total_mcweight.Fill(1.,mcweight[0]);
        
        
        
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        ## Trigger selection
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        itrig_=0; trig1 = False; trig2 = False; trig3 = False; trig4 = False; trig5 = False; trig6 = False; trig7 = False; trig8 = False; trig9 = False; trig10 = False; trig11 = False; trig12 = False;
        trig1 = CheckFilter(trigName, trigResult, 'HLT_PFMET170_') # added from  monojet
        trig2 = CheckFilter(trigName, trigResult, 'HLT_PFMET170_NoiseCleaned')
        trig3 = CheckFilter(trigName, trigResult, 'HLT_PFMET170_JetIdCleaned_v')
        trig4 = CheckFilter(trigName, trigResult, 'HLT_PFMET170_HBHECleaned_v')
        trig5 = CheckFilter(trigName, trigResult, 'HLT_PFMETNoMu90_PFMHTNoMu90_IDTight_v')
        trig6 = CheckFilter(trigName, trigResult, 'HLT_PFMETNoMu100_PFMHTNoMu100_IDTight_v') #added from  tt+DM all hadronic analysis
        trig7 = CheckFilter(trigName, trigResult, 'HLT_PFMETNoMu110_PFMHTNoMu110_IDTight_v')
        trig8 = CheckFilter(trigName, trigResult, 'HLT_PFMETNoMu120_PFMHTNoMu120_IDTight_v')
        trig9 = CheckFilter(trigName, trigResult, 'HLT_PFMET110_PFMHT110_')
        trig10 = CheckFilter(trigName, trigResult, 'HLT_IsoMu24_v') #added from tt+DM all hadronic analysis
        trig11 = CheckFilter(trigName, trigResult, 'HLT_IsoTkMu24_v') #added from tt+DM all hadronic analysis
        trig12 = CheckFilter(trigName, trigResult, 'HLT_Ele27_WPTight_Gsf') #added from Siew Yan slides
        
        if not isData:
            trigstatus  = False # triggers are not required for MC
        if isData:
            trigstatus =  trig1 | trig2 | trig3 | trig4 | trig5 | trig6 | trig7 | trig8 | trig9 | trig10 | trig11 | trig12  #to include data with above triggers
        if not isData:
           if trigstatus == True : continue
            
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        ## Filter selection
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        filterstatus = False
        filter1 = False; filter2 = False;filter3 = False;filter4 = False; filter5 = False; filter6 = False
        ifilter_=0
        filter1 = CheckFilter(filterName, filterResult, 'Flag_HBHENoiseFilter')
        filter2 = CheckFilter(filterName, filterResult, 'Flag_globalTightHalo2016Filter')
        filter3 = CheckFilter(filterName, filterResult, 'Flag_eeBadScFilter')
        filter4 = CheckFilter(filterName, filterResult, 'Flag_goodVertices')
        filter5 = CheckFilter(filterName, filterResult, 'Flag_EcalDeadCellTriggerPrimitiveFilter')
        
        filter6 = True #Flag_HBHENoiseIsoFilter
        
        if not isData:
            filterstatus = True
        if isData:
            filterstatus =  filter1 & filter2 & filter3 & filter4 & filter5 & filter6
        if filterstatus == False: continue 
        
        
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        ## PFMET Selection
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        
#        if samplename=="all":
        pfmetstatus = ( pfMet > 200.0 )
#           if pfmetstatus == False : continue
         
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
                
        thinjetpassindex=[]
        for ithinjet in range(nTHINJets):
            j1 = thinjetP4[ithinjet]
            #if (j1.Pt() > 30.0)&(abs(j1.Eta())<2.4)&(bool(passThinJetLooseID[ithinjet])==True)&(bool(passThinJetPUID[ithinjet]) == True):
            if (j1.Pt() > 30.0)&(abs(j1.Eta())<2.4)&(bool(passThinJetLooseID[ithinjet])==True):
                thinjetpassindex.append(ithinjet)
        if len(thinjetpassindex) < 1 : continue
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        ## Electron Veto
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        myEles=[]
        for iele in range(nEle):
            if (eleP4[iele].Pt() > 10. ) & (abs(eleP4[iele].Eta()) <2.5) & (bool(eleIsPassLoose[iele]) == True) :
                myEles.append(iele)
        
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        ## Muon Veto
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        myMuos = []
        for imu in range(nMu):
            if (muP4[imu].Pt()>10.) & (abs(muP4[imu].Eta()) < 2.4) & (bool(isLooseMuon[imu]) == True):
                relPFIso = (muChHadIso[imu]+ max(0., muNeHadIso[imu] + muGamIso[imu] - 0.5*muPUPt[imu]))/muP4[imu].Pt();
                if relPFIso<0.4 :
                    myMuos.append(imu)
                    
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        ## Tau Veto
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------
        myTaus=[]
        for itau in range(nTau):
            if (tauP4[itau].Pt()>18.) & (abs(tauP4[itau].Eta())<2.5) & (bool(isDecayModeFinding[itau]) == True) & (bool(passLooseTauIso[itau]) == True):
                myTaus.append(itau)
        
        
        

        
        st_runId[0]             = long(run)
        st_lumiSection[0]       = lumi
        st_eventId[0]           = event
#        print '-----------'+str(st_runId)+", "+str(st_lumiSection)+", "+str(st_eventId)
        
        st_pfMetCorrPt[0]       = pfMet
        st_pfMetCorrPhi[0]      = pfMetPhi
        st_isData[0]            = isData

        
        st_THINjetP4.clear()
        st_THINjetCISVV2.clear()
        st_THINjetHadronFlavor.clear()
        st_THINjetNHadEF.clear()
        st_THINjetCHadEF.clear()
        
        st_eleP4.clear()
        st_muP4.clear()
        st_muChHadIso.clear()
        st_muGamIso.clear()
        st_muNeHadIso.clear()
        st_HPSTau_4Momentum.clear()
        
        st_genParId.clear()
        st_genMomParId.clear()
        st_genParSt.clear()
        st_genParP4.clear()

        st_THINnJet[0] = len(thinjetpassindex)
        for ithinjet in range(len(thinjetpassindex)):
            st_THINjetP4.push_back(thinjetP4[ithinjet])
            st_THINjetCISVV2.push_back(thinJetCSV[ithinjet])
            st_THINjetHadronFlavor.push_back(THINjetHadronFlavor[ithinjet])
            st_THINjetNHadEF.push_back(thinjetNhadEF[ithinjet])
            st_THINjetCHadEF.push_back(thinjetChadEF[ithinjet])
            
        st_nEle[0] = len(myEles)
        for iele in range(len(myEles)):
            st_eleP4.push_back(eleP4[iele])
            st_eleIsPassLoose.push_back(bool(eleIsPassLoose[iele]))
            st_eleIsPassMedium.push_back(bool(eleIsPassMedium[iele]))
            st_eleIsPassTight.push_back(bool(eleIsPassTight[iele]))
            
        st_nMu[0] = len(myMuos)
        for imu in range(len(myMuos)):
            st_muP4.push_back(muP4[imu])
            st_isLooseMuon.push_back(bool(isLooseMuon[imu]))
            st_isTightMuon.push_back(bool(isTightMuon[imu]))
            st_isMediumMuon.push_back(bool(isMediumMuon[imu]))
            st_muChHadIso.push_back(muChHadIso[imu])
            st_muNeHadIso.push_back(muNeHadIso[imu])
            st_muGamIso.push_back(muGamIso[imu])
            st_muPUPt.push_back(muPUPt[imu])
            
        st_HPSTau_n[0] = len(myTaus)
        for itau in range(len(myTaus)):
            st_HPSTau_4Momentum.push_back(tauP4[itau])
            
        

        st_pu_nTrueInt[0] = pu_nTrueInt
        st_nGenPar[0] =  nGenPar
        for igp in range(nGenPar): 
            st_genParId.push_back(genParId[igp])
            st_genMomParId.push_back(genMomParId[igp])
            st_genParSt.push_back(genParSt[igp])
            st_genParP4.push_back(genParP4[igp])

                
        
        ## Fill variables for the CRs. 
        WenuRecoil[0] = -1.0
        Wenumass[0] = -1.0
        
        WmunuRecoil[0] = -1.0
        Wmunumass[0] = -1.0
        
        ZeeMass[0] = -1.0
        ZeeRecoil[0] = -1.0
        
        ZmumuMass[0] = -1.0
        ZmumuRecoil[0] = -1.0
        
        TOPRecoil[0] = -1.0
        
        ## for dielectron 
        if len(myEles) ==2:
            ele1 = myEles[0]
            ele2 = myEles[1]
            p4_ele1 = eleP4[ele1]
            p4_ele2 = eleP4[ele2]
            
            ee_mass = ( p4_ele1 + p4_ele2 ).M()
            
            #if not  ( (ee_mass > 70.0 ) & (ee_mass < 110.0) ): continue
            if not ( eleCharge[ele1] * eleCharge[ele2] > 0 ) :            
                zeeRecoilPx = -( pfMet*math.cos(pfMetPhi) - p4_ele1.Px() - p4_ele2.Px())
                zeeRecoilPy = -( pfMet*math.sin(pfMetPhi) - p4_ele1.Py() - p4_ele2.Py())
                ZeeRecoil[0] =  math.sqrt(zeeRecoilPx * zeeRecoilPx  +  zeeRecoilPy*zeeRecoilPy)
                ZeeMass[0] = ee_mass
                
        ## hardrecoil cut for ZJETS sample
#            if samplename == "ZJETS":
#               ZeeRecoilstatus =(ZeeRecoil > 200)
#               print(samplename,ZeeRecoilstatus)
#               if ZeeRecoilstatus == False : continue
           
        
        ## for dimu
        if len(myMuos) ==2:
            mu1 = myMuos[0]
            mu2 = myMuos[1]
            p4_mu1 = muP4[mu1]
            p4_mu2 = muP4[mu2]
            
            mumu_mass = ( p4_mu1 + p4_mu2 ).M()
            
            #if not  ( (mumu_mass > 70.0 ) & (mumu_mass < 110.0) ): continue
            if not ( muCharge[mu1] * muCharge[mu2] > 0 ) :
                zmumuRecoilPx = -( pfMet*math.cos(pfMetPhi)  - p4_mu1.Px() - p4_mu2.Px())
                zmumuRecoilPy = -( pfMet*math.sin(pfMetPhi)  - p4_mu1.Py() - p4_mu2.Py())
                ZmumuRecoil[0] =  math.sqrt(zmumuRecoilPx * zmumuRecoilPx  +  zmumuRecoilPy*zmumuRecoilPy)
                ZmumuMass[0] = mumu_mass
                
        ## hardrecoil cut for ZJETS sample
#        if samplename == "ZJETS":
        if len(myEles) ==2:
            ZRecoilstatus =(ZeeRecoil[0] > 200)                
        elif len(myMuos) ==2:
            ZRecoilstatus =(ZmumuRecoil[0] > 200)
        else:
            ZRecoilstatus=False
#         print(samplename,ZRecoilstatus)
#         if ZRecoilstatus == False : continue
        
        ## for Single electron  
        if len(myEles) == 1:
           ele1 = myEles[0]
           p4_ele1 = eleP4[ele1]
           
           e_mass = MT(p4_ele1.Pt(),pfMet, DeltaPhi(p4_ele1.Phi(),pfMetPhi)) #transverse mass defined as sqrt{2pT*MET*(1-cos(dphi)}
           
           #if not  ( (e_mass > 50.0 ) & (e_mass < 160.0) ): continue
           
           WenuRecoilPx = -( pfMet*math.cos(pfMetPhi) - p4_ele1.Px())
           WenuRecoilPy = -( pfMet*math.sin(pfMetPhi) - p4_ele1.Py())
           WenuRecoil[0] =  math.sqrt(WenuRecoilPx * WenuRecoilPx  +  WenuRecoilPy*WenuRecoilPy)
           Wenumass[0] = e_mass
           
        ## hardrecoil cut for WJETS sample   
#        if samplename == "WJETS":
#           WenuRecoilstatus =(WenuRecoil > 200)
#           print(samplename,WenuRecoilstatus) 
#           if WenuRecoilstatus == False : continue
         
        ## for Single muon  
        if len(myMuos) == 1:
           mu1 = myMuos[0]
           p4_mu1 = muP4[mu1]
           
           mu_mass = MT(p4_mu1.Pt(),pfMet, DeltaPhi(p4_mu1.Phi(),pfMetPhi)) #transverse mass defined as sqrt{2pT*MET*(1-cos(dphi)} 
           
           #if not  ( (mu_mass > 50.0 ) & (mu_mass < 160.0) ): continue
           
           WmunuRecoilPx = -( pfMet*math.cos(pfMetPhi) - p4_mu1.Px())
           WmunuRecoilPy = -( pfMet*math.sin(pfMetPhi) - p4_mu1.Py())
           WmunuRecoil[0] =  math.sqrt(WmunuRecoilPx * WmunuRecoilPx  +  WmunuRecoilPy*WmunuRecoilPy)
           Wmunumass[0] = mu_mass
           
        ## hardrecoil cut for WJETS sample
#        if samplename == "WJETS":
        if len(myEles) == 1:
            WRecoilstatus =(WenuRecoil[0] > 200)
        elif len(myMuos) == 1:
            WRecoilstatus =(WmunuRecoil[0] > 200)
        else:
            WRecoilstatus=False
#            print(samplename,WRecoilstatus) 
#            if WRecoilstatus == False : continue
         
         
        ## for Single electron && Single Muon
        if len(myEles) == 1 and len(myMuos) == 1:
           ele1 = myEles[0]
           p4_ele1 = eleP4[ele1]
           mu1 = myMuos[0]
           p4_mu1 = muP4[mu1]
           
           #e_mass = MT(p4_ele1.Pt(),pfMet, DeltaPhi(p4_ele1.Phi(),pfMetPhi)) #transverse mass defined as sqrt{2pT*MET*(1-cos(dphi)}
           #mu_mass = MT(p4_mu1.Pt(),pfMet, DeltaPhi(p4_mu1.Phi(),pfMetPhi))
           #if not  ( (e_mass > 50.0 ) & (e_mass < 160.0) ): continue
           
           TOPenumunuRecoilPx = -( pfMet*math.cos(pfMetPhi) - p4_mu1.Px() -p4_ele1.Px())
           TOPenumunuRecoilPy = -( pfMet*math.sin(pfMetPhi) - p4_mu1.Py() -p4_ele1.Py())
           TOPRecoil[0] =  math.sqrt(TOPenumunuRecoilPx * TOPenumunuRecoilPx  +  TOPenumunuRecoilPy*TOPenumunuRecoilPy)
           
         
#        if samplename == "TT": #hardrecoil cut for TTbar sample
        TOPRecoilstatus =(TOPRecoil[0] > 200)
#            if TOPRecoilstatus == False : continue
        
        if pfmetstatus==False and ZRecoilstatus==False and WRecoilstatus==False and TOPRecoilstatus==False:
            continue
         
        outTree.Fill()

    h_total_mcweight.Write()
    h_total.Write()
    outfile.Write()


def CheckFilter(filterName, filterResult,filtercompare):
    ifilter_=0
    filter1 = False
    for ifilter in filterName:
        filter1 = (ifilter.find(filtercompare) != -1)  & (bool(filterResult[ifilter_]) == True)   
        if filter1: break
        ifilter_ = ifilter_ + 1
    return filter1

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
    
def Phi_mpi_pi(x):
    kPI = 3.14159265358979323846
    kTWOPI = 2 * kPI
    
    while (x >= kPI): x = x - kTWOPI;
    while (x < -kPI): x = x + kTWOPI;
    return x;
    
def DeltaPhi(phi1,phi2):
   phi = Phi_mpi_pi(phi1-phi2)
   
   return phi
        
def CheckFilter(filterName, filterResult,filtercompare):
    ifilter_=0
    filter1 = False
    for ifilter in filterName:
        filter1 = (ifilter.find(filtercompare) != -1)  & (bool(filterResult[ifilter_]) == True)   
        if filter1: break
        ifilter_ = ifilter_ + 1
    return filter1


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
            #print "inside WJ loop pdgid", PID
            #print ("if status =",      (abs(PID) != 11),( abs(PID) != 12),(  abs(PID) != 13 ),(  abs(PID) != 14),(  abs(PID) != 15),(  abs(PID) != 16))
            #print "and of if status ", ( (abs(PID) != 11) & (abs(PID) != 12) &  (abs(PID) != 13) & (abs(PID) != 14) &  (abs(PID) != 15) &  (abs(PID) != 16) )
            
            if ( (abs(PID) != 11) & (abs(PID) != 12) &  (abs(PID) != 13) & (abs(PID) != 14) &  (abs(PID) != 15) &  (abs(PID) != 16) ): continue
            #print "lepton found"
            if ( ( (status != 1) & (abs(PID) != 15)) | ( (status != 2) & (abs(PID) == 15)) ): continue
            #print "tau found"
            if ( (abs(momPID) != 24) & (momPID != PID) ): continue
            #print "W found"
            #print "aftrer WJ if statement"
            goodLepID.append(ig)
        #print "length = ",len(goodLepID)
        if len(goodLepID) == 2 :
            l4_thisLep = genParP4[goodLepID[0]]
            l4_thatLep = genParP4[goodLepID[1]]
            l4_z = l4_thisLep + l4_thatLep
            
            pt = l4_z.Pt()
            pt__ = pt
            print " pt inside "
            k2 = -0.830041 + 7.93714 *TMath.Power( pt - (-877.978) ,(-0.213831) ) ;
    
    #################        
    #ZJets
    #################
    if sample == "ZJETS":
        print " inside zjets "
        goodLepID = []
        for ig in range(nGenPar):
         #   print " inside loop "
            PID    = genParId[ig]
            momPID = genMomParId[ig]
            status = genParSt[ig]
          #  print " after vars "

            if ( (abs(PID) != 12) &  (abs(PID) != 14) &  (abs(PID) != 16) ) : continue
            if ( status != 1 ) : continue 
            if ( (momPID != 23) & (momPID != PID) ) : continue
            goodLepID.append(ig)
        
        if len(goodLepID) == 2 :
            l4_thisLep = genParP4[goodLepID[0]]
            l4_thatLep = genParP4[goodLepID[1]]
            l4_z = l4_thisLep + l4_thatLep
            pt = l4_z.Pt()
            print " pt inside "
            k2 = -0.180805 + 6.04146 *TMath.Power( pt - (-759.098) ,(-0.242556) ) ;

    #################        
    #TTBar
    #################        
    if (sample=="TT"):
        print " inside ttbar "
        goodLepID = []
        for ig in range(nGenPar):
            print "inside TT loop "
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
    AnalyzeDataSet()
