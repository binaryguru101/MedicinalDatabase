import pandas as pd 
import os 


os.makedirs("output",exist_ok=True)

df = pd.read_csv("raw_data.csv")
df = df.fillna("")
df = df.map(lambda x: str(x).strip() if isinstance(x, str) else x)

valid_disease_rows = df[df["disease_name"].str.upper() != "#N/A"]
valid_disease_rows = valid_disease_rows[valid_disease_rows["disease_name"] != ""]

#NODES HERE 

df[['drug_id', 'drug_name', 'drug_smiles']].drop_duplicates().to_csv("output/drugs.csv", index=False)
df[['target_id', 'target_name', 'gene_name']].drop_duplicates().to_csv("output/targets.csv", index=False)

valid_disease_rows[['disease_name']].drop_duplicates().to_csv("output/diseases.csv", index=False)

df[['pathway_name']].drop_duplicates().to_csv("output/pathways.csv", index=False)

df[['biomarker_name']].drop_duplicates().to_csv("output/biomarkers.csv", index=False)


valid_disease_rows[['target_id', 'disease_name', 'target_disease_approval_status']]\
  .drop_duplicates()\
  .to_csv("output/target_disease.csv", index=False)


valid_disease_rows[['drug_id', 'disease_name', 'disease_specific_drug_approval_status']]\
  .drop_duplicates()\
  .to_csv("output/drug_disease.csv", index=False)

df[['drug_id', 'target_id', 'drug_mechanism_of_action_on_target']] \
  .drop_duplicates() \
  .to_csv("output/drug_target.csv", index=False)


df[['target_id', 'pathway_name']] \
  .dropna(subset=['target_id', 'pathway_name']) \
  .drop_duplicates() \
  .to_csv("output/target_pathway.csv", index=False)


df[['drug_id', 'biomarker_name']] \
  .dropna(subset=['drug_id', 'biomarker_name']) \
  .drop_duplicates() \
  .to_csv("output/drug_biomarker.csv", index=False)

df[['disease_name', 'biomarker_name']] \
  .dropna(subset=['disease_name', 'biomarker_name']) \
  .drop_duplicates() \
  .to_csv("output/disease_biomarker.csv", index=False)


print("complete") 



