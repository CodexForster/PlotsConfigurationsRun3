CUTS=(
	"sr_ele_wp90iso__mu_cut_TightID_POG_ee_high_pt"
	"sr_ele_wp90iso__mu_cut_TightID_POG_ee_low_pt"
	"sr_ele_wp90iso__mu_cut_TightID_POG_em_high_pt"
	"sr_ele_wp90iso__mu_cut_TightID_POG_em_low_pt"
	"sr_ele_wp90iso__mu_cut_TightID_POG_mm_high_pt"
	"sr_ele_wp90iso__mu_cut_TightID_POG_mm_low_pt"
	"sr_ele_mvaWinter22V2Iso_WP90__mu_cut_Tight_HWW_ee_high_pt"
	"sr_ele_mvaWinter22V2Iso_WP90__mu_cut_Tight_HWW_ee_low_pt"
	"sr_ele_mvaWinter22V2Iso_WP90__mu_cut_Tight_HWW_em_high_pt"
	"sr_ele_mvaWinter22V2Iso_WP90__mu_cut_Tight_HWW_em_low_pt"
	"sr_ele_mvaWinter22V2Iso_WP90__mu_cut_Tight_HWW_mm_high_pt"
	"sr_ele_mvaWinter22V2Iso_WP90__mu_cut_Tight_HWW_mm_low_pt"
	"sr_ele_mvaWinter22V2Iso_WP90__mu_cut_TightMiniIso_HWW_ee_high_pt"
	"sr_ele_mvaWinter22V2Iso_WP90__mu_cut_TightMiniIso_HWW_ee_low_pt"
	"sr_ele_mvaWinter22V2Iso_WP90__mu_cut_TightMiniIso_HWW_em_high_pt"
	"sr_ele_mvaWinter22V2Iso_WP90__mu_cut_TightMiniIso_HWW_em_low_pt"
	"sr_ele_mvaWinter22V2Iso_WP90__mu_cut_TightMiniIso_HWW_mm_high_pt"
	"sr_ele_mvaWinter22V2Iso_WP90__mu_cut_TightMiniIso_HWW_mm_low_pt"
	"sr_ele_wp90iso__mu_mvaMuID_WP_medium_ee_high_pt"
	"sr_ele_wp90iso__mu_mvaMuID_WP_medium_ee_low_pt"
	"sr_ele_wp90iso__mu_mvaMuID_WP_medium_em_high_pt"
	"sr_ele_wp90iso__mu_mvaMuID_WP_medium_em_low_pt"
	"sr_ele_wp90iso__mu_mvaMuID_WP_medium_mm_high_pt"
	"sr_ele_wp90iso__mu_mvaMuID_WP_medium_mm_low_pt"
	"sr_ele_wp90iso__mu_mvaMuID_WP_tight_ee_high_pt"
	"sr_ele_wp90iso__mu_mvaMuID_WP_tight_ee_low_pt"
	"sr_ele_wp90iso__mu_mvaMuID_WP_tight_em_high_pt"
	"sr_ele_wp90iso__mu_mvaMuID_WP_tight_em_low_pt"
	"sr_ele_wp90iso__mu_mvaMuID_WP_tight_mm_high_pt"
	"sr_ele_wp90iso__mu_mvaMuID_WP_tight_mm_low_pt"
)

PRESELS=(
	"basic_selections_ee_high_pt"
	"basic_selections_ee_low_pt"
	"basic_selections_em_high_pt"
	"basic_selections_em_low_pt"
	"basic_selections_mm_high_pt"
	"basic_selections_mm_low_pt"
	"basic_selections_ee_high_pt"
	"basic_selections_ee_low_pt"
	"basic_selections_em_high_pt"
	"basic_selections_em_low_pt"
	"basic_selections_mm_high_pt"
	"basic_selections_mm_low_pt"
	"basic_selections_ee_high_pt"
	"basic_selections_ee_low_pt"
	"basic_selections_em_high_pt"
	"basic_selections_em_low_pt"
	"basic_selections_mm_high_pt"
	"basic_selections_mm_low_pt"
	"basic_selections_ee_high_pt"
	"basic_selections_ee_low_pt"
	"basic_selections_em_high_pt"
	"basic_selections_em_low_pt"
	"basic_selections_mm_high_pt"
	"basic_selections_mm_low_pt"
	"basic_selections_ee_high_pt"
	"basic_selections_ee_low_pt"
	"basic_selections_em_high_pt"
	"basic_selections_em_low_pt"
	"basic_selections_mm_high_pt"
	"basic_selections_mm_low_pt"
)

rm eff_plots/efficiencies.csv
echo "signals ; backgrounds ; cut ; sig_eff ; bkg_eff" > eff_plots/efficiencies.csv

for ((idx=0; idx<${#CUTS[@]}; ++idx)); do

echo ${CUTS[$idx]}
echo ${PRESELS[$idx]}

cd ../scripts/
python mkEff.py --inputFile /eos/user/n/ntrevisa/mkShapesRDF_rootfiles/LeptonID_2022EE_v12/rootFile/mkShapes__LeptonID_2022EE_v12.root \
	   --signals ggH_hww \
	   --backgrounds WJets \
	   --cut ${CUTS[$idx]} \
	   --presel ${PRESELS[$idx]} \
	   --year 2022 \
	   --variable pt1 \
	   --outputDir ../2022EE_v12/eff_plots/

python mkEff.py --inputFile /eos/user/n/ntrevisa/mkShapesRDF_rootfiles/LeptonID_2022EE_v12/rootFile/mkShapes__LeptonID_2022EE_v12.root \
	   --signals WW \
	   --backgrounds WJets \
	   --cut ${CUTS[$idx]} \
	   --presel ${PRESELS[$idx]} \
	   --year 2022 \
	   --variable pt1 \
	   --outputDir ../2022EE_v12/eff_plots/

python mkEff.py --inputFile /eos/user/n/ntrevisa/mkShapesRDF_rootfiles/LeptonID_2022EE_v12/rootFile/mkShapes__LeptonID_2022EE_v12.root \
	   --signals ggH_hww \
	   --backgrounds TTToSemiLeptonic \
	   --cut ${CUTS[$idx]} \
	   --presel ${PRESELS[$idx]} \
	   --year 2022 \
	   --variable pt1 \
	   --outputDir ../2022EE_v12/eff_plots/

python mkEff.py --inputFile /eos/user/n/ntrevisa/mkShapesRDF_rootfiles/LeptonID_2022EE_v12/rootFile/mkShapes__LeptonID_2022EE_v12.root \
	   --signals WW \
	   --backgrounds TTToSemiLeptonic \
	   --cut ${CUTS[$idx]} \
	   --presel ${PRESELS[$idx]} \
	   --year 2022 \
	   --variable pt1 \
	   --outputDir ../2022EE_v12/eff_plots/
cd -

done
