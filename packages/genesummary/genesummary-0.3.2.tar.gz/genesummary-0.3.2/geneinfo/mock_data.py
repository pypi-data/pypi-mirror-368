"""
Mock data for testing geneinfo package when external APIs are not available.
"""

MOCK_GENE_DATA = {
    "TP53": {
        "basic_info": {
            "id": "ENSG00000141510",
            "display_name": "TP53",
            "external_name": "TP53", 
            "description": "tumor protein p53",
            "seq_region_name": "17",
            "start": 7661779,
            "end": 7687550,
            "strand": -1,
            "biotype": "protein_coding"
        },
        "transcripts": [
            {
                "id": "ENST00000269305",
                "display_name": "TP53-201",
                "biotype": "protein_coding",
                "start": 7661779,
                "end": 7687550,
                "length": 2579,
                "protein_id": "ENSP00000269305"
            },
            {
                "id": "ENST00000455263",
                "display_name": "TP53-202",
                "biotype": "protein_coding",
                "start": 7668402,
                "end": 7687550,
                "length": 1839,
                "protein_id": "ENSP00000398846"
            }
        ],
        "protein_domains": [
            {
                "type": "DOMAIN",
                "description": "P53 DNA-binding domain",
                "start": 102,
                "end": 292,
                "evidence": ["ECO:0000255"]
            },
            {
                "type": "DOMAIN", 
                "description": "P53 tetramerization domain",
                "start": 323,
                "end": 356,
                "evidence": ["ECO:0000255"]
            }
        ],
        "gene_ontology": [
            {
                "go_id": "GO:0003677",
                "go_name": "DNA binding",
                "evidence_code": "IDA",
                "aspect": "molecular_function",
                "qualifier": []
            },
            {
                "go_id": "GO:0006915",
                "go_name": "apoptotic process",
                "evidence_code": "TAS",
                "aspect": "biological_process", 
                "qualifier": []
            },
            {
                "go_id": "GO:0005634",
                "go_name": "nucleus",
                "evidence_code": "IDA",
                "aspect": "cellular_component",
                "qualifier": []
            }
        ],
        "pathways": [
            {
                "pathway_id": "R-HSA-69278",
                "name": "Cell Cycle Checkpoints",
                "species": "Homo sapiens",
                "url": "https://reactome.org/content/detail/R-HSA-69278"
            },
            {
                "pathway_id": "R-HSA-5357801", 
                "name": "Programmed Cell Death",
                "species": "Homo sapiens",
                "url": "https://reactome.org/content/detail/R-HSA-5357801"
            }
        ],
        "orthologs": [
            {
                "id": "ENSMUSG00000059552",
                "species": "mus_musculus",
                "protein_id": "ENSMUSP00000058024",
                "type": "ortholog_one2one",
                "dn_ds": 0.1234,
                "identity": 85.2
            }
        ],
        "paralogs": []
    },
    "BRCA1": {
        "basic_info": {
            "id": "ENSG00000012048",
            "display_name": "BRCA1",
            "external_name": "BRCA1",
            "description": "BRCA1, DNA repair associated",
            "seq_region_name": "17",
            "start": 43044295,
            "end": 43125483,
            "strand": -1,
            "biotype": "protein_coding"
        },
        "transcripts": [
            {
                "id": "ENST00000357654",
                "display_name": "BRCA1-201",
                "biotype": "protein_coding", 
                "start": 43044295,
                "end": 43125483,
                "length": 7269,
                "protein_id": "ENSP00000350283"
            }
        ],
        "protein_domains": [
            {
                "type": "DOMAIN",
                "description": "RING-type E3 ubiquitin transferase domain",
                "start": 1,
                "end": 109,
                "evidence": ["ECO:0000255"]
            },
            {
                "type": "DOMAIN",
                "description": "BRCT domain",
                "start": 1650,
                "end": 1736,
                "evidence": ["ECO:0000255"]
            }
        ],
        "gene_ontology": [
            {
                "go_id": "GO:0003677",
                "go_name": "DNA binding",
                "evidence_code": "IEA", 
                "aspect": "molecular_function",
                "qualifier": []
            },
            {
                "go_id": "GO:0006281",
                "go_name": "DNA repair",
                "evidence_code": "TAS",
                "aspect": "biological_process",
                "qualifier": []
            }
        ],
        "pathways": [
            {
                "pathway_id": "R-HSA-5696394",
                "name": "DNA Double-Strand Break Repair",
                "species": "Homo sapiens", 
                "url": "https://reactome.org/content/detail/R-HSA-5696394"
            }
        ],
        "orthologs": [
            {
                "id": "ENSMUSG00000017146",
                "species": "mus_musculus",
                "protein_id": "ENSMUSP00000017290",
                "type": "ortholog_one2one",
                "dn_ds": 0.0876,
                "identity": 88.1
            }
        ],
        "paralogs": []
    },
    "ENSG00000129514": {
        "basic_info": {
            "id": "ENSG00000129514",
            "display_name": "FOXA1",
            "external_name": "FOXA1",
            "description": "forkhead box A1",
            "seq_region_name": "14",
            "start": 37806061,
            "end": 37815987,
            "strand": 1,
            "biotype": "protein_coding"
        },
        "transcripts": [
            {
                "id": "ENST00000250448",
                "display_name": "FOXA1-201",
                "biotype": "protein_coding",
                "start": 37806061,
                "end": 37815987,
                "length": 1467,
                "protein_id": "ENSP00000250448"
            }
        ],
        "protein_domains": [
            {
                "type": "DOMAIN",
                "description": "Forkhead domain",
                "start": 146,
                "end": 233,
                "evidence": ["ECO:0000255"]
            }
        ],
        "gene_ontology": [
            {
                "go_id": "GO:0003677",
                "go_name": "DNA binding",
                "evidence_code": "IDA",
                "aspect": "molecular_function",
                "qualifier": []
            },
            {
                "go_id": "GO:0006355",
                "go_name": "regulation of transcription, DNA-templated",
                "evidence_code": "TAS",
                "aspect": "biological_process",
                "qualifier": []
            }
        ],
        "pathways": [
            {
                "pathway_id": "R-HSA-212436",
                "name": "Generic Transcription Pathway",
                "species": "Homo sapiens",
                "url": "https://reactome.org/content/detail/R-HSA-212436"
            }
        ],
        "orthologs": [
            {
                "id": "ENSMUSG00000035451",
                "species": "mus_musculus", 
                "protein_id": "ENSMUSP00000033142",
                "type": "ortholog_one2one",
                "dn_ds": 0.0654,
                "identity": 92.3
            }
        ],
        "paralogs": [
            {
                "id": "ENSG00000125798",
                "species": "homo_sapiens",
                "protein_id": "ENSP00000245495",
                "type": "within_species_paralog", 
                "dn_ds": None,
                "identity": 45.2
            }
        ]
    }
}