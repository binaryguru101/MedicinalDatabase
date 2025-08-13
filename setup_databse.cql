LOAD CSV WITH HEADERS FROM 'file:///drugs.csv' AS row
MERGE (d:Drug {drug_id: row.drug_id})
SET d.drug_name = row.drug_name,
    d.drug_smiles = row.drug_smiles;

LOAD CSV WITH HEADERS FROM 'file:///targets.csv' AS row
MERGE (t:Target {target_id: row.target_id})
SET t.target_name = row.target_name,
    t.gene_name = row.gene_name;

LOAD CSV WITH HEADERS FROM 'file:///pathways.csv' AS row
MERGE (:Pathway {pathway_name: row.pathway_name});

LOAD CSV WITH HEADERS FROM 'file:///biomarkers.csv' AS row
MERGE (:Biomarker {biomarker_name: row.biomarker_name});

LOAD CSV WITH HEADERS FROM 'file:///diseases.csv' AS row
MERGE (:Disease {disease_name: row.disease_name});

LOAD CSV WITH HEADERS FROM 'file:///drug_target.csv' AS row
MATCH (d:Drug {drug_id: row.drug_id})
MATCH (t:Target {target_id: row.target_id})
MERGE (d)-[r:TARGETS]->(t)
SET r.drug_mechanism_of_action_on_target = row.drug_mechanism_of_action_on_target;

LOAD CSV WITH HEADERS FROM 'file:///target_pathway.csv' AS row
MATCH (t:Target {target_id: row.target_id})
MATCH (p:Pathway {pathway_name: row.pathway_name})
MERGE (t)-[:INVOLVED_IN_PATHWAY]->(p);

LOAD CSV WITH HEADERS FROM 'file:///drug_biomarker.csv' AS row
MATCH (d:Drug {drug_id: row.drug_id})
MATCH (b:Biomarker {biomarker_name: row.biomarker_name})
MERGE (d)-[:HAS_BIOMARKER]->(b);

LOAD CSV WITH HEADERS FROM 'file:///target_disease.csv' AS row
MATCH (t:Target {target_id: row.target_id})
MATCH (ds:Disease {disease_name: row.disease_name})
MERGE (t)-[r:ASSOCIATED_WITH_DISEASE]->(ds)
SET r.approval_status = row.target_disease_approval_status;

LOAD CSV WITH HEADERS FROM 'file:///drug_disease.csv' AS row
MATCH (d:Drug {drug_id: row.drug_id})
MATCH (ds:Disease {disease_name: row.disease_name})
MERGE (d)-[r:TREATS_DISEASE]->(ds)
SET r.approval_status = row.disease_specific_drug_approval_status;

LOAD CSV WITH HEADERS FROM 'file:///disease_biomarker.csv' AS row
MATCH (d:Disease)
WHERE toLower(d.disease_name) = toLower(trim(row.disease_name))
MATCH (b:Biomarker)
WHERE toLower(b.biomarker_name) = toLower(trim(row.biomarker_name))
MERGE (d)-[:ASSOCIATED_WITH]->(b);
