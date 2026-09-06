#!/usr/bin/env python3
"""
scripts/download_references.py

LeanFlow Enterprise — Scientific Literature Downloader
======================================================
Downloads canonical scientific reference papers (PDFs) for UC1-UC16.
Creates stubs for papers behind paywalls or lacking direct PDF access.
"""

import os
import sys
import json
import requests
from pathlib import Path

# Setup paths
REPO_ROOT = Path(__file__).resolve().parent.parent
REFERENCES_DIR = REPO_ROOT / "data" / "references"
REFERENCES_DIR.mkdir(parents=True, exist_ok=True)

# DOI/Reference mapping for UC1-UC16
# We'll use unpaywall or direct arxiv links for open access PDFs.
REFERENCE_DB = {
    "UC1": {"title": "High-Re Turbulent Cascade", "doi": "10.1017/jfm.2015.421", "arxiv": None, "stub": True},
    "UC2": {"title": "Zero-Alloc ETD-RK4", "doi": "10.1016/j.jcp.2005.02.006", "arxiv": None, "stub": True},
    "UC3": {"title": "Dual-Scale UV Regularity", "doi": "10.1103/PhysRevFluids.4.084607", "arxiv": "1905.10300", "stub": False},
    "UC4": {"title": "IDA DAE Incompressibility", "doi": "10.1137/0909062", "arxiv": None, "stub": True},
    "UC5": {"title": "PolarQuant Telemetry", "doi": "10.1109/LSP.2018.2882583", "arxiv": None, "stub": True},
    "UC6": {"title": "PyO3 Zero-Copy Buffer Safety", "doi": "10.1145/3313808.3313822", "arxiv": None, "stub": True},
    "UC7": {"title": "PDEBench Takamoto et al 2022", "doi": "10.48550/arXiv.2210.07182", "arxiv": "2210.07182", "stub": False},
    "UC8": {"title": "Ghia Ghia and Shin 1982", "doi": "10.1016/0021-9991(82)90058-4", "arxiv": None, "stub": True},
    "UC9": {"title": "Dedalus Burns et al 2020", "doi": "10.1103/PhysRevResearch.2.023068", "arxiv": "1905.10388", "stub": False},
    "UC10": {"title": "Athena++ Stone et al 2020", "doi": "10.3847/1538-4365/ab929b", "arxiv": "2005.06651", "stub": False},
    "UC11": {"title": "JHTDB Li et al 2008", "doi": "10.1080/14685240802376389", "arxiv": "0806.4617", "stub": False},
    "UC12": {"title": "PyClaw Ketcheson et al 2012", "doi": "10.1137/11082539X", "arxiv": "1104.5298", "stub": False},
    "UC13": {"title": "OpenFOAM Weller et al 1998", "doi": "10.1063/1.168744", "arxiv": None, "stub": True},
    "UC14": {"title": "AMReX-Hydro Bell et al 1989", "doi": "10.1016/0021-9991(89)90151-4", "arxiv": None, "stub": True},
    "UC15": {"title": "Vortex Merger Meunier et al 2002", "doi": "10.1017/S002211200100732X", "arxiv": None, "stub": True},
    "UC16": {"title": "MHD Duct Müller and Bühler 2001", "doi": "10.1016/S0167-6105(01)00155-4", "arxiv": None, "stub": True},
}

def download_arxiv_pdf(arxiv_id: str, out_path: Path) -> bool:
    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    print(f"Downloading {url} ...")
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        with open(out_path, "wb") as f:
            f.write(resp.content)
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to download {url}: {e}")
        return False

def create_stub(uc_id: str, info: dict, out_path: Path):
    print(f"Creating literature stub for {uc_id} ...")
    content = f"""# Reference Literature Stub: {uc_id}
Title: {info['title']}
DOI: {info['doi']}

Note: The full PDF is not freely available (paywalled or lacks direct arXiv link).
This stub serves as a persistent reference for LeanFlowScratchDB.
"""
    with open(out_path, "w") as f:
        f.write(content)

def main():
    print("LeanFlow Enterprise — Scientific Literature Downloader")
    print("=" * 60)
    
    for uc_id, info in REFERENCE_DB.items():
        base_name = f"{uc_id}_{info['title'].replace(' ', '_').replace('(', '').replace(')', '').replace('&', 'and')}"
        
        if info.get("arxiv") and not info.get("stub"):
            pdf_path = REFERENCES_DIR / f"{base_name}.pdf"
            if not pdf_path.exists():
                success = download_arxiv_pdf(info["arxiv"], pdf_path)
                if not success:
                    # Fallback to stub
                    stub_path = REFERENCES_DIR / f"{base_name}.txt"
                    create_stub(uc_id, info, stub_path)
            else:
                print(f"Skipping {uc_id}, already exists: {pdf_path.name}")
        else:
            stub_path = REFERENCES_DIR / f"{base_name}.txt"
            if not stub_path.exists():
                create_stub(uc_id, info, stub_path)
            else:
                print(f"Skipping {uc_id}, already exists: {stub_path.name}")

    print("\nAll references processed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
