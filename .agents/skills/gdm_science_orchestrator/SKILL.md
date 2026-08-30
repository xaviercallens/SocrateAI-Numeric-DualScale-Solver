---
name: gdm-science-orchestrator
description: >-
  Orchestrates Google DeepMind science skills (AlphaFold, AlphaGenome, Foldseek, PDB, ChEMBL, PubChem,
  PubMed, ArXiv, BioRxiv, Reactome, STRING, OpenTargets, Ensembl, dbSNP, ClinVar) for interdisciplinary
  scientific discovery, biomolecular modeling, literature synthesis, and physical chemistry.
  Activate when combining deep learning structural models with literature or database retrieval.
---

# Google DeepMind Science Skills Orchestrator

Integrates the official Google DeepMind [science-skills](https://github.com/google-deepmind/science-skills) collection into unified scientific research pipelines.

## 1. Available Domain Toolchains

| Domain | DeepMind Science Skills | Primary Use Case |
|---|---|---|
| **Structural Biology** | `alphafold_database_fetch_and_analyze`, `pdb_database`, `foldseek_structural_search`, `pymol` | Fetch 3D coordinates, analyze pLDDT confidence, compute structural similarity, render complexes. |
| **Genomics & Variants** | `alphagenome_single_variant_analysis`, `clinvar_database`, `dbsnp_database`, `gnomad_database`, `ensembl_database` | Variant effect prediction, pathogenicity classification, population frequencies, transcript mapping. |
| **Cheminformatics & Drug Discovery** | `chembl_database`, `pubchem_database`, `opentargets_database`, `reactome_database` | Bioactivity data, target-disease associations, pathway analysis, molecular properties. |
| **Scientific Literature** | `literature_search_arxiv`, `literature_search_biorxiv`, `literature_search_europepmc`, `literature_search_openalex`, `pubmed_database` | Multi-source literature retrieval, citation graphing, preprint extraction. |

## 2. Multi-Step Research Workflows

### Target to Structure to Literature Pipeline
1. **Target Identification**: Query `opentargets_database` or `uniprot_database` for gene/protein IDs.
2. **Structure Fetch & Analysis**: Use `alphafold_database_fetch_and_analyze` or `pdb_database` for 3D atomic coordinates.
3. **Homology & Binding Sites**: Run `foldseek_structural_search` to discover structural homologues.
4. **Literature Evidence**: Query `literature_search_arxiv` and `pubmed_database` to cross-reference experimental papers.

## 3. Epistemic Grounding

- Always distinguish between **experimentally resolved data** (PDB, X-ray crystallography, cryo-EM) and **AI predictions** (AlphaFold pLDDT, AlphaGenome variant predictions).
- Record UniProt accessions, PDB IDs, and DOIs for all cited biological entities.
