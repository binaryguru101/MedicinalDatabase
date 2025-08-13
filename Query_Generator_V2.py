import re 
import os
from dotenv import load_dotenv
from agno.tools import tool 
from neo4j import GraphDatabase
from agno.agent import Agent
from agno.models.groq import Groq
import pandas as pd
from openai import OpenAI
from neo4j import GraphDatabase
from agno.agent import Agent
from agno.models.groq import Groq
from agno.playground import Playground
from agno.memory.v2.memory import Memory
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.models.openai import OpenAIChat
from agno.storage.sqlite import SqliteStorage

load_dotenv()  

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_AUTH = (os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))

groq_client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=OPENAI_API_KEY
)

neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)



import re

def generate_cypher(question: str) -> str:
    """Convert natural language to Cypher query using Groq, with fallback handling and preprocessing."""
    
    clean_question = question.strip().rstrip("?").capitalize()
    
    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages = [
                {
                    "role": "system",
"content": """
# Cypher Query Assistant for Neo4j Biomedical Knowledge Graph

You convert natural language questions into valid Cypher queries. Follow these rules strictly:

## Output Format
- Return ONLY a Cypher query (no comments, explanations, or additional text)
- If the question is unclear or unsupported, return: // unable to generate query

## Schema
*Nodes:*
- Drug (drug_id, drug_name, drug_smiles)
- Target (target_id, target_name, gene_name)
- Disease (disease_name)
- Pathway (pathway_name)
- Biomarker (biomarker_name)

*Relationships:*
- (d:Drug)-[:TREATS_DISEASE {approval_status}]->(ds:Disease)
- (d:Drug)-[:TARGETS {drug_mechanism_of_action_on_target}]->(t:Target)
- (t:Target)-[:ASSOCIATED_WITH_DISEASE {approval_status}]->(ds:Disease)
- (t:Target)-[:INVOLVED_IN_PATHWAY]->(p:Pathway)
- (d:Drug)-[:HAS_BIOMARKER]->(b:Biomarker)

## Mandatory Rules

### 1. Case Sensitivity
*ALWAYS use case-insensitive matching for ALL name-based lookups:*
cypher
WHERE toLower(d.drug_name) = toLower("user_input")
WHERE toLower(t.gene_name) = toLower("user_input")
WHERE toLower(ds.disease_name) = toLower("user_input")
WHERE toLower(p.pathway_name) = toLower("user_input")
WHERE toLower(b.biomarker_name) = toLower("user_input")


### 2. Mechanism of Action Queries
When question mentions "mechanism", "inhibitor", "activator", or similar terms:
cypher
WHERE toLower(r.drug_mechanism_of_action_on_target) CONTAINS toLower("mechanism_term")


### 3. Common Query Patterns
- "drugs for X" or "treatments for X" → Find drugs that treat disease X
- "genes for X" → Find targets associated with disease X
- "pathways for X" → Find pathways involving targets associated with disease X

### 4. Always Use
- DISTINCT when multiple paths may exist
- WHERE clauses for filtering (never use inline property matching in node patterns)
- Exact field names: d.drug_name, d.drug_smiles, t.gene_name, etc.

## Dynamic Field Selection

- Always return only the most relevant fields based on the question.
- Example rules:
  - Always include `d.drug_name`.
  - Always include `ds.disease_name`.  
  - If the question mentions "mechanism" or "inhibitor", return only `d.drug_name`, `r.drug_mechanism_of_action_on_target`
  - If the question asks for "SMILES", return `d.drug_name`, `d.drug_smiles`
  - If the question asks what a drug treats, return `d.drug_name`, `ds.disease_name`
  - If the question asks what drugs treat a disease, return only `d.drug_name`
  - If the question involves gene/target/pathway, return only those specific fields
- Do not include extra columns. Minimize output fields.

## Mandatory fields

## Examples

*Q: Which drugs treat Acute pain?*
cypher
MATCH (d:Drug)-[:TREATS_DISEASE]->(ds:Disease)
WHERE toLower(ds.disease_name) = toLower("Acute pain")
RETURN DISTINCT d.drug_name


*Q: What are the drugs for Tuberculosis?*
cypher
MATCH (d:Drug)-[:TREATS_DISEASE]->(ds:Disease)
WHERE toLower(ds.disease_name) = toLower("Tuberculosis")
RETURN DISTINCT d.drug_name


*Q: Give me drug smiles that work on inhibitor mechanism of TP53*
cypher
MATCH (d:Drug)-[r:TARGETS]->(t:Target)
WHERE toLower(t.gene_name) = toLower("TP53")
AND toLower(r.drug_mechanism_of_action_on_target) CONTAINS toLower("inhibitor")
RETURN DISTINCT d.drug_smiles


*Q: Find genes associated with cancer*
cypher
MATCH (t:Target)-[:ASSOCIATED_WITH_DISEASE]->(ds:Disease)
WHERE toLower(ds.disease_name) CONTAINS toLower("cancer")
RETURN DISTINCT t.gene_name



""" },
                {"role": "user", "content": clean_question}
            ],
            temperature=0
        )

        cypher = response.choices[0].message.content.strip()

        if cypher.lower().startswith("// unable to generate query"):
            print(f"[WARN] LLM could not generate a Cypher query for: '{clean_question}'")
            return "// unable to generate query"

        # Clean up: remove markdown/code fences
        cypher = re.sub(r'```[a-z]*\n?', '', cypher, flags=re.IGNORECASE)
        cypher = re.sub(r'^query:?\s*', '', cypher, flags=re.IGNORECASE)

        return cypher.strip()

    except Exception as e:
        print(f"[ERROR] Cypher generation failed: {e}")
        return "// unable to generate query"

def fuzzy_disease_fallback(disease_keyword: str) -> str:
    return f"""
    MATCH (d:Drug)-[:TREATS_DISEASE]->(ds:Disease)
    WHERE toLower(ds.disease_name) CONTAINS "{disease_keyword.lower()}"
    RETURN DISTINCT d.drug_name, ds.disease_name
    """

@tool(name="query_neo4j", show_result=True, stop_after_tool_call=False)
def query_neo4j(question: str) -> str:
    """Query the Neo4j biomedical dataset using a natural language question and export the result to Excel."""

    cypher = generate_cypher(question)
    print(f"[Cypher Generated] {cypher}")

    
    if (
        cypher.strip().startswith("// unable to generate query")
        or 'disease_name: "' in cypher
        or "treatments for" in question.lower()
        or "drugs for" in question.lower()
    ):
        print("[Fallback Triggered]")

        
        match = re.search(r'disease_name:\s*"(.+?)"', cypher)
        if match:
            disease = match.group(1)
        else:
            # Try extracting from the question
            disease = question.replace("treatments for", "").replace("drugs for", "").strip("? ").strip()

        cypher = f"""
    MATCH (d:Drug)-[:TREATS_DISEASE]->(ds:Disease)
    WHERE toLower(ds.disease_name) CONTAINS "{disease.lower()}"
    OPTIONAL MATCH (d)-[r:TARGETS]->(t:Target)
    OPTIONAL MATCH (t)-[:INVOLVED_IN_PATHWAY]->(p:Pathway)
    OPTIONAL MATCH (d)-[:HAS_BIOMARKER]->(b:Biomarker)
    OPTIONAL MATCH (t)-[:ASSOCIATED_WITH_DISEASE]->(ds2:Disease)
    RETURN DISTINCT
        d.drug_name AS drug_name,
        d.drug_smiles AS drug_smiles,
        r.drug_mechanism_of_action_on_target AS drug_mechanism,
        t.target_name AS target_name,
        t.gene_name AS gene_name,
        p.pathway_name AS pathway_name,
        ds.disease_name AS disease_name,
        b.biomarker_name AS biomarker_name
    """
        print(f"[New Cypher] {cypher}")

    try:
        with neo4j_driver.session() as session:
            results = session.run(cypher)
            data = [dict(record) for record in results]

        if not data:
            return f" No data found in Neo4j for:\n\"{question}\"\n\n[Cypher Used] {cypher}"

        df = pd.DataFrame(data)
        df.columns = [col.replace("_", " ").capitalize() for col in df.columns]

        file_path = "results.xlsx"
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Query Results", index=False)
            pd.DataFrame([[f"Results for: {question}"]]).to_excel(writer, sheet_name="Metadata", header=False, index=False)

        return f" Query successful for: \"{question}\"\n\nTop results:\n{df.head(5).to_string(index=False)}\n\n Full results saved to: {file_path}"

    except Exception as e:
        print(f"[ERROR] Query failed: {e}")
        return f" An error occurred while querying Neo4j for:\n\"{question}\"\n\nError: {str(e)}"



model = Groq(api_key=OPENAI_API_KEY, id="llama-3.1-8b-instant")
model.debug = True  

web_agent = Agent(
   name="web_agent",
   model=model,
   tools=[query_neo4j],
)
web_agent.print_response("Give me drugs that target the metabolic pathways", stream=True)

'''
    comment the line above and uncoment the lines below till 255 to run this in agno virtual playground
    supports memory and pipelining
'''
# play=Playground(agents=[web_agent])
# app=play.get_app()
# if __name__ == '__main__':
#   play.serve("Query_Generator:app", reload=True)



#give me the smiles of drug that works on inhibitor mechanism of TP53