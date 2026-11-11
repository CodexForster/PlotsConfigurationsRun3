import numpy as np
import pandas as pd
import uproot

root_path = "/afs/cern.ch/user/s/squinto/private/work/PlotsConfigurationRun3/HWW/VBF_DF/2024/rootFiles/HWW/VBF/2024/rootFiles__VBF_DF_2024v15_df_for_combination_1607/mkShapes__VBF_DF_2024v15_df_for_combination_1607.root"
tree_path = "trees/hww_sr_inc/"
output_path = (
    "/eos/user/s/squinto/SWAN_projects/ML/2024_df_for_combination_1607.pkl.gz"
)

label_map = {
    "ggH": "is_ggH",
    "qqH": "is_qqH",
    "top": "is_top",
    "WW": "is_WW",
    "ggWW": "is_ggWW",
}
label_columns = list(label_map.values())

# Define active systematic versions here
#active_versions = ["nom", "absolute_up", "absolute_down"]
active_versions = ['nom', 'absolute_up', 'absolute_down', 'relativebal_up', 'relativebal_down', "jer_up", "jer_down"]#, "bbec1_up", "bbec1_down", "hf_up", "hf_down", "absolute2024_up", "absolute2024_down"]

# Master mapping of suffixes (defined for all potential versions)
suffixes = {
    "absolute_up": "_absolute_up",
    "absolute_down": "_absolute_down",
    "relativebal_up": "_relativebal_up",
    "relativebal_down": "_relativebal_down",
    "jer_up": "_jer_up",
    "jer_down": "_jer_down",
    "bbec1_up": "_bbec1_up",
    "bbec1_down": "_bbec1_down",
    "hf_up": "_hf_up",
    "hf_down": "_hf_down",
    "absolute2024_up": "_absolute2024_up",
    "absolute2024_down": "_absolute2024_down",
}

# Filter active suffixes based strictly on active_versions
active_suffixes = [
    suffixes[v] for v in active_versions if v in suffixes
]  # excludes 'nom'

processes = [
    "top/Events;1",
    "top/Events;2",
    #"WW/Events;1",  
    "WW/Events;3",
    "WW/Events;4",
    "ggWW/Events;1",
    "ggWW/Events;2",
    "ggH_hww/Events;1",
    "qqH_hww/Events;1",
]

file = uproot.open(root_path)
dfs = []

for proc in processes:
    print(f"Processing: {proc}")
    tree = file[tree_path + proc]
    all_branches = tree.keys()

    # Identify base variables (exclude ANY suffix pattern known in master dict)
    all_known_suffixes = list(suffixes.values())
    base_variables = [
        v
        for v in all_branches
        if not any(v.endswith(s) for s in all_known_suffixes)
    ]

    # FIX 1: Read ONLY base variables + active systematic variations
    branches_to_read = []
    for b in all_branches:
        if b in base_variables:
            branches_to_read.append(b)
        elif any(b.endswith(s) for s in active_suffixes):
            # Only keep if the stem is one of our base variables
            if any(b == f"{base_var}{s}" for base_var in base_variables for s in active_suffixes):
                branches_to_read.append(b)

    data = tree.arrays(branches_to_read, library="np")
    df_balanced = pd.DataFrame(
        {k: data[k].reshape(-1) for k in branches_to_read}
    )

    for version in active_versions:
        block_dict = {}

        for var in base_variables:
            if version == "nom":
                block_dict[var] = df_balanced[var]
            else:
                var_variant = var + suffixes[version]
                if var_variant in df_balanced.columns:
                    block_dict[var] = df_balanced[var_variant]
                else:
                    block_dict[var] = df_balanced[var]

        df_version = pd.DataFrame(block_dict)

        # FIX 2: Dynamic variation flags for all active versions
        for v in active_versions:
            df_version[f"is_{v}"] = 1 if version == v else 0

        # Process flags
        for col in label_columns:
            df_version[col] = 0
        for key, label in label_map.items():
            if key in proc:
                df_version[label] = 1

        dfs.append(df_version)

if not dfs:
    raise RuntimeError("No data to concatenate")

df_final = pd.concat(dfs, ignore_index=True)
df_final = df_final.drop_duplicates()

df_final = df_final[
    (df_final["mth"] > 60)
    & (df_final["mth"] < 125)
    & (df_final["mtw2"] > 30)
    & (df_final["jetpt1"] > 30)
    & (df_final["jetpt2"] > 30)
    & (df_final["puppimet"] > 20)
    & (df_final["ptll"] > 30)
    & (df_final["mjj"] > 120)
]

print("\n--- Statistiche Finali ---")
print(f"Shape totale: {df_final.shape}")
print("Colonne finali:" + str(df_final.columns.tolist()))
print("Distribuzione per processo:")
for col in label_columns:
    print(f"  {col}: {df_final[df_final[col] == 1].shape[0]}")

df_final.to_pickle(output_path)
print(f"\nFile salvato con successo in: {output_path}")