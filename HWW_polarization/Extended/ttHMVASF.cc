
#include <vector>
#include "TLorentzVector.h"
#include "correction.h"
#include "ROOT/RVec.hxx"
#include "TH2D.h"
#include "TFile.h"
#include <map>
#include <sstream>
#include <fstream>

using namespace ROOT;
using namespace ROOT::VecOps;

typedef std::map<std::string, std::map<std::string, std::string>> map_dict;


class ttHMVASF{
public:

  RVecF lepton_pt,  lepton_eta;
  RVecI lepton_pdgId;

  TH2D* h_SF_ele_;
  TH2D* h_SF_ele_stat_;
  TH2D* h_SF_ele_syst_;
  TH2D* h_SF_mu_;
  TH2D* h_SF_mu_stat_;
  TH2D* h_SF_mu_syst_;

  int nLeptons_;

  map_dict SF_files_map_;
  const char* muOrEle_;
  const char* year_;

  std::tuple<double, double, double> GetSF(int flavor, double eta, double pt){
    
    double eta_temp = eta;
    double pt_temp  = pt;
    
    double SF, SF_stat, SF_syst;
    
    // Case electron
    if (flavor == 11){
      
      double eta_max = 2.49;
      double eta_min = -2.5;
      double pt_max  = 499.;
      double pt_min  = 15.;
      
      if(eta_temp < eta_min) {eta_temp = eta_min;}
      if(eta_temp > eta_max) {eta_temp = eta_max;}
      if(pt_temp < pt_min)   {pt_temp  = pt_min;}
      if(pt_temp > pt_max)   {pt_temp  = pt_max;}
      
      SF      = h_SF_ele_      -> GetBinContent(h_SF_ele_     -> FindBin(eta_temp, pt_temp));
      SF_stat = h_SF_ele_stat_ -> GetBinContent(h_SF_ele_stat_-> FindBin(eta_temp, pt_temp));
      SF_syst = h_SF_ele_syst_ -> GetBinContent(h_SF_ele_syst_-> FindBin(eta_temp, pt_temp));
    }
    // Case muon
    else if (flavor == 13){
      
      double eta_max = 2.39;
      double eta_min = -2.4;
      double pt_max = 119.9; // 199.;
      double pt_min = 10.1;
      
      if(eta_temp < eta_min) {eta_temp = eta_min;}
      if(eta_temp > eta_max) {eta_temp = eta_max;}
      if(pt_temp < pt_min)   {pt_temp  = pt_min;}
      if(pt_temp > pt_max)   {pt_temp  = pt_max;}
      
      SF      = h_SF_mu_      -> GetBinContent(h_SF_mu_    -> FindBin(eta_temp, pt_temp));
      SF_stat = h_SF_mu_stat_ -> GetBinError(h_SF_mu_stat_ -> FindBin(eta_temp, pt_temp)); //Note -- uncertainty histograms store uncertainty as error per bin
      SF_syst = h_SF_mu_syst_ -> GetBinError(h_SF_mu_syst_ -> FindBin(eta_temp, pt_temp));
    }
    
    else {
      std::cout << "Invalid call to ttHMVASF::GetSF" << std::endl;
    }
    
    std::tuple<double, double, double> result = {SF, SF_stat, SF_syst};
    
    return result;
    
  }  

  ttHMVASF() {
    map_dict SF_files_map;
    // Electron
    SF_files_map["electron"]["2016HIPM"] = {
      "/afs/cern.ch/work/s/sblancof/private/Run2Analysis/AlmaLinux9_mkShapes/mkShapesRDF/examples/extended/data/electron_ttHMVA_UL_SF/2016HIPM/egammaEffi.txt"
    };
    SF_files_map["electron"]["2016noHIPM"] = {
      "/afs/cern.ch/work/s/sblancof/private/Run2Analysis/AlmaLinux9_mkShapes/mkShapesRDF/examples/extended/data/electron_ttHMVA_UL_SF/2016HIPM/egammaEffi.txt"
    };
    SF_files_map["electron"]["2017"] = {
      "/afs/cern.ch/work/s/sblancof/private/Run2Analysis/AlmaLinux9_mkShapes/mkShapesRDF/examples/extended/data/electron_ttHMVA_UL_SF/2017/egammaEffi.txt"
    };
    SF_files_map["electron"]["2018"] = {
      "/afs/cern.ch/work/s/sblancof/private/Run2Analysis/AlmaLinux9_mkShapes/mkShapesRDF/examples/extended/data/electron_ttHMVA_UL_SF/2018/egammaEffi.txt"
    };
    
    // Muon
    SF_files_map["muon"]["2016HIPM"] = {
      "/afs/cern.ch/work/s/sblancof/private/Run2Analysis/AlmaLinux9_mkShapes/mkShapesRDF/examples/extended/data/muon_ttHMVA_SF/2016HIPM/NUM_TightHWW_ISO_tthmva_DEN_TightHWW_ISO_eta_pt.root"
    };
    SF_files_map["muon"]["2016noHIPM"] = {
      "/afs/cern.ch/work/s/sblancof/private/Run2Analysis/AlmaLinux9_mkShapes/mkShapesRDF/examples/extended/data/muon_ttHMVA_SF/2016noHIPM/NUM_TightHWW_ISO_tthmva_DEN_TightHWW_ISO_eta_pt.root"
    };
    SF_files_map["muon"]["2017"] = {
      "/afs/cern.ch/work/s/sblancof/private/Run2Analysis/AlmaLinux9_mkShapes/mkShapesRDF/examples/extended/data/muon_ttHMVA_SF/2017/NUM_TightHWW_ISO_tthmva_DEN_TightHWW_ISO_eta_pt.root"
    };
    SF_files_map["muon"]["2018"] = {
      "/afs/cern.ch/work/s/sblancof/private/Run2Analysis/AlmaLinux9_mkShapes/mkShapesRDF/examples/extended/data/muon_ttHMVA_SF/2018/NUM_TightHWW_ISO_tthmva_DEN_TightHWW_ISO_eta_pt.root"
    };
    SF_files_map_ = SF_files_map;


    SF_files_map_ = SF_files_map;    
  }

  RVecD operator()(const char* year, const int nLeptons, const char* muOrEle, std::string requested_SF, RVecF lepton_pt, RVecF lepton_eta, RVecI lepton_pdgId){

    muOrEle_ = muOrEle;
    year_ = year;
    nLeptons_ = lepton_pt.size();
    
    int ele_nbins_eta = 10;
    int ele_nbins_pt  = 7;
    
    float ele_eta_bins[] {-2.5, -2., -1.566, -1.442,  -0.8, 0., 0.8, 1.442, 1.566, 2.0, 2.5};
    float ele_pt_bins[] {10., 15., 20., 35., 50., 90., 150., 500.};
    
    if (strncmp(muOrEle_,"ele",3) || strncmp(muOrEle_,"all",3)){
      
      h_SF_ele_      = new TH2D("h_SF_ele",      "h_SF_ele",      ele_nbins_eta, ele_eta_bins, ele_nbins_pt, ele_pt_bins);
      h_SF_ele_stat_ = new TH2D("h_SF_ele_stat", "h_SF_ele_stat", ele_nbins_eta, ele_eta_bins, ele_nbins_pt, ele_pt_bins);
      h_SF_ele_syst_ = new TH2D("h_SF_ele_syst", "h_SF_ele_syst", ele_nbins_eta, ele_eta_bins, ele_nbins_pt, ele_pt_bins);
      h_SF_ele_->SetDirectory(0);
      h_SF_ele_stat_->SetDirectory(0);
      h_SF_ele_syst_->SetDirectory(0);
      
      // Filling TH2D objects by reading txt input files
      //cout << "SF files map = " << SF_files_map_["electron"][year_] << endl;
      
      // Prepare grid to read the txt file: 70 lines and 14 columns  
      double lines[70][14];
      
      // Parsing the .txt file
      std::string line;
      std::istringstream strm;
      double num;
      std::ifstream ifs(SF_files_map_["electron"][year_]);
      int i = 0;
      int j = 0;
      while(getline(ifs, line)){
	j = 0;
	std::istringstream strm(line);
	while(strm >> num){
	  lines[i][j] = num;
	  j++;
	}
	i++;
      }
      ifs.close();
      for(int iBinX = 1; iBinX <= h_SF_ele_->GetNbinsX(); iBinX++){
	for(int iBinY = 1; iBinY <= h_SF_ele_->GetNbinsY(); iBinY++){
	  
	  double eta = h_SF_ele_ -> GetXaxis() -> GetBinCenter(iBinX);
	  double pt  = h_SF_ele_ -> GetYaxis() -> GetBinCenter(iBinY);
	  
	  // txt columns structure:
	  // 0:  eta Low  
	  // 1:  eta High  
	  // 2:  pt Low  
	  // 3:  pt High 
	  // 4:  effData 
	  // 5:  statErrData 
	  // 6:  systErrData 
	  // 7:  effMC 
	  // 8:  statErrMC 
	  // 9:  systErrMC 
	  // 10: effDataAltBkg 
	  // 11: effDataAltSig 
	  // 12: effMCAltMC 
	  // 13: effMCTagSel
	  
	  // Looking for correct eta, pt bin
	  for(unsigned i = 0; i < 70; i++){
	    
	    if(eta >= lines[i][0] && eta <= lines[i][1] && pt >= lines[i][2] && pt <= lines[i][3]){
	      // efficiencies
	      double data = lines[i][4];
	      double mc   = lines[i][7];
	      double sf   = 1;
	      if (mc != 0) sf = data/mc;
	      
	      // statistical uncertainty on efficiencies
	      double sigma_data = lines[i][5];
	      double sigma_mc   = lines[i][8];
	      double sigma_sf   = 0.0;
	      if (mc != 0) sigma_sf = TMath::Sqrt( TMath::Power(sigma_data/mc, 2) + TMath::Power(data*sigma_mc/(mc*mc), 2));
	      
	      // systematic uncertainty on efficiencies
	      double syst_data = lines[i][6];
	      double syst_mc   = lines[i][9];
	      double syst_sf   = 0.0;
	      if (mc != 0) syst_sf = TMath::Sqrt( TMath::Power(syst_data/mc, 2) + TMath::Power(data*syst_mc/(mc*mc), 2));
	      
	      h_SF_ele_      -> SetBinContent(iBinX, iBinY, sf);
	      h_SF_ele_stat_ -> SetBinContent(iBinX, iBinY, sigma_sf);
	      h_SF_ele_syst_ -> SetBinContent(iBinX, iBinY, syst_sf);
	      
	      break;
	    }
	  }
	}
      }
      //cout << "Done with loading electrons scale factors" << endl;
    }
    
    //////////////////////////
    // Load muon SFs in memory (if needed)
    //////////////////////////
    
    if (strncmp(muOrEle_,"mu",2) || strncmp(muOrEle_,"all",3)){
      
      //cout << "Muons rootfile: " << SF_files_map_["muon"][year_] << endl;
      TFile* rootfile = new TFile(SF_files_map_["muon"][year_].c_str());
      //cout << "Loaded!" << endl;
      
      // Nominal SF histogram - temp are needed to properly handle BinContent and BinError (maybe) 
      h_SF_mu_      = (TH2D*)rootfile->Get("NUM_TightHWW_ISO_tthmva_DEN_TightHWW_ISO_eta_pt")->Clone();
      h_SF_mu_stat_ = (TH2D*)rootfile->Get("NUM_TightHWW_ISO_tthmva_DEN_TightHWW_ISO_eta_pt_stat")->Clone();
      h_SF_mu_syst_ = (TH2D*)rootfile->Get("NUM_TightHWW_ISO_tthmva_DEN_TightHWW_ISO_eta_pt_syst")->Clone();
      h_SF_mu_->SetDirectory(0);
      h_SF_mu_stat_->SetDirectory(0);
      h_SF_mu_syst_->SetDirectory(0);
      
      rootfile->Close();
      //cout << "Done with loading muons scale factors" << endl;
    }
  
    std::vector<double> SF_vect {};
    std::vector<double> SF_err_vect_el {};
    std::vector<double> SF_err_vect_mu {};
    std::vector<double> SF_up_el {};
    std::vector<double> SF_up_mu {};
    std::vector<double> SF_do_el {};
    std::vector<double> SF_do_mu {};
    
    // Loop over leptons
    for (int i = 0; i < nLeptons_; i++){
      
      // Get electron SF and uncertainty
      if(TMath::Abs(lepton_pdgId[i]) == 11 && (strncmp(muOrEle_,"ele",3) || strncmp(muOrEle_,"all",3))){
	
	std::tuple<double, double, double> res = GetSF(11, lepton_eta[i], lepton_pt[i]);
	
	SF_vect.push_back(std::get<0>(res));
	SF_err_vect_el.push_back(TMath::Sqrt(TMath::Power(std::get<1>(res), 2) + TMath::Power(std::get<2>(res), 2)));
	SF_err_vect_mu.push_back(0.0);
      }
      
      // Get muon SF and uncertainty
      else if(TMath::Abs(lepton_pdgId[i]) == 13 && (strncmp(muOrEle_,"mu",2) || strncmp(muOrEle_,"all",3))){
	
	std::tuple<double, double, double> res = GetSF(13, lepton_eta[i], lepton_pt[i]);
	
	SF_vect.push_back(std::get<0>(res));
	SF_err_vect_el.push_back(0.0);
	SF_err_vect_mu.push_back(TMath::Sqrt(TMath::Power(std::get<1>(res), 2) + TMath::Power(std::get<2>(res), 2)));
      }
    }
    
    double SF     = 1.;
    double SF_err = 1.;
    
    // Calculate product of SFs for all leptons in the event --> central value of SF to be returned
    for (auto x : SF_vect) 
      SF *= x;
    
    // Now for the variations, these also have to account for the recoSF --> why? I guess not in our case
    for(int i = 0; i < nLeptons_; i++){
      
      double SFref = SF_vect[i] == 0. ? 1.0 : SF_vect[i]; // Not sure how to handle uncertainty on 0 SF ... for now act as if SF is 1 in this case
      SF_up_el.push_back( (SFref + SF_err_vect_el[i]) / SFref );
      SF_up_mu.push_back( (SFref + SF_err_vect_mu[i]) / SFref );
      SF_do_el.push_back( (SFref - SF_err_vect_el[i]) / SFref );
      SF_do_mu.push_back( (SFref - SF_err_vect_mu[i]) / SFref );
    }
    
    // Now build the up and down variation SFs
    double SF_up_out_el   = 1.;
    double SF_up_out_mu   = 1.;
    double SF_down_out_el = 1.;
    double SF_down_out_mu = 1.;
    
    // Up/down variations are already divided by the central SF value
    for(int i = 0; i < nLeptons_; i++){
      SF_up_out_el   *= SF_up_el[i];
      SF_up_out_mu   *= SF_up_mu[i];
      SF_down_out_el *= SF_do_el[i];
      SF_down_out_mu *= SF_do_mu[i];
    }

    // [nominal, eleUp, eleDown, muUp, muDown]
    RVecD results = {SF, SF_up_out_el, SF_up_out_mu, SF_down_out_el, SF_down_out_mu};
    h_SF_ele_->Delete();
    h_SF_ele_stat_->Delete();
    h_SF_ele_syst_->Delete();
    h_SF_mu_->Delete();
    h_SF_mu_stat_->Delete();
    h_SF_mu_syst_->Delete();
    return results;    
  }
};


