import ROOT
import sys,os

input_file_name = "eff_plots/efficiencies.root"

colors = [ROOT.kGreen+1,ROOT.kRed+1,ROOT.kBlue,ROOT.kOrange,ROOT.kMagenta,ROOT.kAzure+10]

sys.argv.append('-b')
ROOT.gROOT.SetBatch()

def plot_canvas(input_file_name,
                sig,
                bkg,
                ele_ids,
                muon_ids,
                final_state,
                pt_range,
                output_name,
                focus):
    """plots a canvas with the requested cuts and processes"""

    input_file = ROOT.TFile(input_file_name)

    first_graph = 0

    # Create canvas
    c1 = ROOT.TCanvas("c1","c1",800,800)
    c1.cd()

    # Trick to allow legend to get all the graphs --> put them into a list
    graphs = []

    # Draw a frame with correct axis ranges. Otherwise, TGraphs will choose their own axis ranges.
    frame = c1.DrawFrame(0.0,0.0,1.0,1.0)
    frame.GetXaxis().SetTitle("1 - bkg efficiency");
    frame.GetYaxis().SetTitle("Sig efficiency");
    c1.Update()
    
    for ele_id in ele_ids:
        for muon_id in muon_ids:
            
            graph_name = f"{sig}_{bkg}_sr_ele_{ele_id}__mu_{muon_id}_{final_state}_{pt_range}"
            print(f"Graph name: {graph_name}")

            if first_graph == 0:
                print("Preparing first graph")
                graph = input_file.Get(graph_name)
                if isinstance(graph, ROOT.TGraph): 
                    graphs.append(input_file.Get(graph_name))
                    graphs[-1].SetMarkerStyle(20)
                    graphs[-1].SetMarkerColor(colors[first_graph])
                    graphs[-1].GetXaxis().SetRangeUser(0.0,1.0)
                    graphs[-1].GetYaxis().SetRangeUser(0.0,1.0)
                    graphs[-1].GetXaxis().SetTitle("1 - bkg efficiency")
                    graphs[-1].GetYaxis().SetTitle("Sig efficiency")
                    if focus == 'mm': graphs[-1].SetName(muon_id)
                    if focus == 'ee': graphs[-1].SetName(ele_id)
                    if focus == 'em': graphs[-1].SetName(ele_id + "_" + muon_id)
                    graphs[-1].Draw("P")
                    graphs[-1].GetXaxis().SetRangeUser(0.0,1.0)
                    graphs[-1].GetYaxis().SetRangeUser(0.0,1.0)
                    print("First graph plotted!")
                    print(f"Values = ({graphs[-1].GetPointX(0)},{graphs[-1].GetPointY(0)})")
                    first_graph += 1
            else:
                print(f"Preparing graph number {first_graph+1}")
                graph = input_file.Get(graph_name)
                if isinstance(graph, ROOT.TGraph): 
                    graphs.append(input_file.Get(graph_name))
                    graphs[-1].SetMarkerStyle(20)
                    graphs[-1].SetMarkerColor(colors[first_graph])
                    if focus == 'mm': graphs[-1].SetName(muon_id)
                    if focus == 'ee': graphs[-1].SetName(ele_id)
                    if focus == 'em': graphs[-1].SetName(ele_id + "_" + muon_id)
                    graphs[-1].Draw("P,same")
                    print(f"Graph {first_graph+1} plotted!")
                    print(f"Values = ({graphs[-1].GetPointX(0)},{graphs[-1].GetPointY(0)})")
                    first_graph += 1

    # Legend                
    leg = ROOT.TLegend(0.12,0.12,0.82,0.42)
    leg.SetLineColor(0)
    if focus == 'mm':   leg.SetHeader("Muon ID:")
    elif focus == 'ee':  leg.SetHeader("Electron ID:")
    elif focus == 'em': leg.SetHeader("Electron and Muon ID:")
    else:
        raise ValueError("Please spcify what I should put my focus on")
    for g in graphs:
        leg.AddEntry(g,g.GetName(),"p")
    
    print(f"Graphs = {graphs}")
    leg.Draw("same")
    print(f"Total legend rows = {leg.GetNRows()}")

    frame.SetTitle(output_name)
    c1.Update()
    
    c1.Print(f"eff_plots/{output_name}.png")
    input_file.Close()
    

# Calling the function to produce plots 
ele_ids  = ["wp90iso","mvaWinter22V2Iso_WP90"]
muon_ids = ["cut_TightID_POG","cut_Tight_HWW","cut_TightMiniIso_HWW","mvaMuID_WP_medium","mvaMuID_WP_tight"] 

signals     = ["WW","ggH_hww"]
backgrounds = ["TTToSemiLeptonic","WJets"]

final_states = ["ee","em","mm"]
pt_ranges    = ["high_pt","low_pt"]


# Loop over IDs without tthmva
for signal in signals:
    for background in backgrounds:
        for final_state in final_states:
            for pt_range in pt_ranges:

                tthmva = ""
                low_pt = ""
                if "tthmva" in muon_ids[0]:
                    tthmva = "_tthmva"
                if pt_range == "low_pt":
                    low_pt = "_low_pt"

                background = background.replace(",","_")
                    
                output_name = f"{final_state}_{signal}_vs_{background}{low_pt}{tthmva}"
                    
                plot_canvas(input_file_name,signal,background,ele_ids,muon_ids,final_state,pt_range,output_name,final_state)

# Loop over IDs with tthmva
ele_ids  = ["wp90iso","mvaWinter22V2Iso_WP90"]
muon_ids = ["cut_TightID_POG_tthmva_80","cut_Tight_HWW_tthmva_80","cut_TightMiniIso_HWW_tthmva_80","mvaMuID_WP_medium_tthmva_80","mvaMuID_WP_tight_tthmva_80"] 

for signal in signals:
    for background in backgrounds:
        for final_state in final_states:
            for pt_range in pt_ranges:

                tthmva = ""
                low_pt = ""
                if "tthmva" in muon_ids[0]:
                    tthmva = "_tthmva"
                if pt_range == "low_pt":
                    low_pt = "_low_pt"

                background = background.replace(",","_")

                output_name = f"{final_state}_{signal}_vs_{background}{low_pt}{tthmva}"
                    
                plot_canvas(input_file_name,signal,background,ele_ids,muon_ids,final_state,pt_range,output_name,final_state)
