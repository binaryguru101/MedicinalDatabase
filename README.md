## Project Summary

- **Database Normalization**  
  - Analyzed the given medicinal database and decomposed it into multiple CSV files for improved structure and clarity.  
  - Each CSV represented a distinct entity (e.g., drugs, diseases, targets, biomarkers, pathways) to enable clear separation of concerns and easier data management.    

- **Relationship Modeling in Neo4j**  
  - Translated foreign keys from the source data into Neo4j graph relationships for more intuitive querying.  
  - Designed and implemented the following relationship types:  
    - `Drug → Target` via `[:TARGETS]`  
    - `Disease → Biomarker` via `[:ASSOCIATED_WITH]`  
    - `Target → Disease` via `[:ASSOCIATED_WITH_DISEASE]`  
    - `Target → Pathway` via `[:INVOLVED_IN_PATHWAY]`  
    - `Drug → Biomarker` via `[:HAS_BIOMARKER]`  
  
- **Knowledge Graph Construction**  
  - Imported all normalized CSV data into Neo4j, creating a fully connected medicinal knowledge graph.  
  - Verified data consistency and ensured that all relationships matched the intended schema.
     

- **LLM-Powered Cypher Query Generator**  
  - Integrated OpenAI’s LLM to automatically translate natural language questions into Cypher queries.  
  - Uses MATCH statements for precise Cypher queries, and falls back to CONTAINS-based matching when exact matches are not found.
  - Implemented fallback mechanisms and error-handling routines to recover from invalid or incomplete query outputs.  

- **Query Execution and Output Processing**  
  - Automated the execution of generated Cypher queries directly in Neo4j.  
  - Processed query results to strip unnecessary fields, retaining only the relevant, structured data.  
  - Exported the final results into an Excel spreadsheet and also printed them in a  tabular format in the terminal.  

- **Agno Framework Integration**  
  - Developed an optional “playground mode” leveraging the Agno framework for a conversational interface to the knowledge graph.  
  - Incorporated built-in memory in Agno to maintain context across multiple user queries.  
  - Uncommenting specific lines in code to switch between the direct execution pipeline and the interactive Agno-based approach.  




## Requirements

To install the Python dependencies, run:

```bash
pip install -r requirements.txt
```

##Installation & Setup

 **STEPS**
   ```bash
   git clone https://github.com/binaryguru101/MedicinalDatabase.git
   cd MedicinalDatabase
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   GROQ_API_KEY=your_groq_api_key
   OPENAI_API_KEY=your_openai_api_key
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password

  ```
  **Place your dataset CSV files in the raw_files folder.**

  **Run your Cypher commands to create nodes & relationships(Setup_Databse.cql)**
## Results

**Query:** Drugs for brain cancer and its biomarkers  

![Query Output](results/Drugs%20for%20brain%20cancer%20and%20it's%20biomarkers/Screenshot%202025-08-13%20213222.png)  
![Results Output](results/Drugs%20for%20brain%20cancer%20and%20it's%20biomarkers/Screenshot%202025-08-13%20213242.png)  
![Neo4J Visualization](results/Drugs%20for%20brain%20cancer%20and%20it's%20biomarkers/Screenshot%202025-08-13%20213307.png)
![PlayGround Visual](results/Playground/Screenshot%202025-08-13%20230944.png)
![PlayGround Memory](results/Playground/Screenshot%202025-08-13%20230821.png)



  


