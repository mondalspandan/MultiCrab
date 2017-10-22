#ifndef PileUpWeights_h_
#define PileUpWeights_h_ 
using namespace std; 
class PileUpWeights{ 
 public: 
   PileUpWeights(){};
   ~PileUpWeights(){};
   static Float_t PUWEIGHT(Int_t nvtx){
   Float_t  puweight[200]= {1.};
   puweight[0]  =  1;
   puweight[1]  =  0.00034173;
   puweight[2]  =  0.0154582;
   puweight[3]  =  0.0171357;
   puweight[4]  =  0.0309825;
   puweight[5]  =  0.0444408;
   puweight[6]  =  0.0438691;
   puweight[7]  =  0.114165;
   puweight[8]  =  0.23363;
   puweight[9]  =  0.315229;
   puweight[10]  =  0.585126;
   puweight[11]  =  0.896279;
   puweight[12]  =  1.18595;
   puweight[13]  =  1.43945;
   puweight[14]  =  1.59123;
   puweight[15]  =  1.67573;
   puweight[16]  =  1.58405;
   puweight[17]  =  1.35339;
   puweight[18]  =  1.36542;
   puweight[19]  =  1.21898;
   puweight[20]  =  1.2565;
   puweight[21]  =  1.08544;
   puweight[22]  =  0.941041;
   puweight[23]  =  0.919897;
   puweight[24]  =  0.890823;
   puweight[25]  =  0.810218;
   puweight[26]  =  0.818664;
   puweight[27]  =  0.695913;
   puweight[28]  =  0.647989;
   puweight[29]  =  0.507053;
   puweight[30]  =  0.447989;
   puweight[31]  =  0.363034;
   puweight[32]  =  0.312012;
   puweight[33]  =  0.351014;
   puweight[34]  =  0.382502;
   puweight[35]  =  0.544424;
   puweight[36]  =  0.803649;
   puweight[37]  =  2.29574;
   puweight[38]  =  4.29648;
   puweight[39]  =  1;
   puweight[40]  =  1;
   puweight[41]  =  1;
   puweight[42]  =  1;
   puweight[43]  =  1;
   puweight[44]  =  1;
   puweight[45]  =  1;
   puweight[46]  =  1;
   puweight[47]  =  1;
   puweight[48]  =  1;
   puweight[49]  =  1;
   puweight[50]  =  1;
   puweight[51]  =  1;
   puweight[52]  =  1;
   if(nvtx >= 50) puweight[nvtx] =0;
   return puweight[nvtx];
  }
};
#endif
