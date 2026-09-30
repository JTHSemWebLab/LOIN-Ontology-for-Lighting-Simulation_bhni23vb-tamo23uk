# From Information Requirements to Knowledge Graphs

This repository contains research materials for modelling and validating information requirements for lighting fixtures using Data Dictionaries (DD), Data Templates (DT), Level of Information Need (LOIN), Information Delivery Specification (IDS), RDF, and SHACL.

The repository originated from the Master's thesis **“Lifting Heterogeneous Data into RDF/OWL Knowledge Graph: A Semantic Approach”**, conducted by Nischal Bhattarai and Mohamad Monir Taktak at Jönköping University.

Selected materials were subsequently revised, extended, or reorganised to support the journal manuscript **“From Information Requirements to Knowledge Graphs: A Semantic Approach Based on DD, DT, and LOIN.”**

## Workflow

The case study investigates information requirements for lighting fixtures used in an office-space lighting simulation.

The workflow includes:

1. defining lighting fixture properties in a standards-based data dictionary;
2. modelling information requirements using DD, DT, and LOIN-related ontologies;
3. lowering selected LOIN requirements into IDS;
4. validating the IFC-based information delivery using IDS;
5. lifting the enriched IFC model into RDF using IFCtoLBD;
6. validating the RDF graph using intrinsic and functional SHACL constraints; and
7. storing and querying the resulting graph in GraphDB.

IDS and SHACL serve complementary purposes. IDS validates selected information requirements within an IFC-based exchange, while SHACL validates semantic constraints over the RDF graph.

## Repository Contents

00_ABOX-TBOX-MODELING/
    ABox and TBox representation of the lighting fixture information model.

01_DATA-DICTIONARY/
    RDF data dictionary for lighting fixture properties.

02_IDS-XML/
    IDS files used for IFC-based validation.

03_LOIN-IDS-MAPPING-EXCEL/
    Human-readable LOIN documentation and LOIN-to-IDS mappings.

04_TTL-GRAPHS/
    IFCtoLBD RDF model, LOIN graphs, and intrinsic and functional SHACL shapes.

05_MODELS/
    Lighting fixture family files and BIM/IFC models used in the case study.

06_SCRIPTS/
    Python scripts used for datatype alignment and IDS generation.

07_DOCUMENTATION/
    Supporting documentation that may be redistributed legally.
