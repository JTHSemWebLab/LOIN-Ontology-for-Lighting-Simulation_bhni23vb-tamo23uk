# From Information Requirements to Knowledge Graphs

This repository provides the research materials and supplementary artefacts associated with the journal manuscript:

**“From Information Requirements to Knowledge Graphs: A Semantic Approach Based on DD, DT, and LOIN”**

## Authors

- **Peter Johansson**
- **Nischal Bhattarai**
- **Rahel Kebede**
- **Annika Moscati**

Department of Construction Engineering and Lighting Science, Jönköping University.

## Repository Background

This repository originated from the Master's thesis **“Lifting Heterogeneous Data into RDF/OWL Knowledge Graph: A Semantic Approach”**, conducted by **Nischal Bhattarai** and **Mohamad Monir Taktak**, under the supervision of **Peter Johansson** and **Rahel Kebede**.

Selected materials from the original thesis were subsequently revised, extended, or reorganised for the journal study. The Git history and file-level documentation should be consulted when tracing individual files and contributions.

## Study Overview

The study investigates how standards-based information requirements for lighting fixtures can be modelled, exchanged, and validated using Data Dictionaries (DD), Data Templates (DT), Level of Information Need (LOIN), IDS, RDF, and SHACL.

The workflow includes:

1. defining lighting fixture properties in a standards-based data dictionary;
2. modelling information requirements using DD, DT, and LOIN-related ontologies;
3. lowering selected LOIN requirements into IDS;
4. validating the IFC information delivery using IDS;
5. lifting the enriched IFC model into RDF using IFCtoLBD; and
6. validating the RDF graph using intrinsic and functional SHACL constraints.

## Repository Contents

00_ABOX-TBOX-MODELING/
    ABox and TBox representation of the information model.

01_DATA-DICTIONARY/
    RDF data dictionary for lighting fixture properties.

02_IDS-XML/
    IDS files used for IFC-based validation.

03_LOIN-IDS-MAPPING-EXCEL/
    LOIN documentation and LOIN-to-IDS mappings.

04_TTL-GRAPHS/
    IFCtoLBD RDF model, LOIN graphs, and SHACL shapes.

05_MODELS/
    Lighting fixture family files and BIM/IFC case-study models.

06_SCRIPTS/
    Python scripts for datatype alignment and IDS generation.

07_DOCUMENTATION/
    Supporting documentation.
