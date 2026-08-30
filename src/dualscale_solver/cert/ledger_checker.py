"""
Mathesis Stream 0 Ledger Soundness & Verification Engine.

Implements machine-checked validation of `ledger.jsonl` and `LEDGER.md`
conforming to `SocrateAI-Scientific-Mathesis` Tier Calculus:
  Sound(L) := forall a, b. b in L(a).supports ==> tier(L(a)) <= tier(L(b))
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Set
import enum


class Tier(enum.Enum):
    """Citation strength per Mathesis SPEC.md §2.1."""
    X = 0  # Exploratory: floats, sampling, plots, LLM output
    C = 1  # Conjecture: physical narrative, unverified reduction
    L = 2  # Literature: peer-reviewed quoted theorem statement
    B = 3  # Checkable: exact rational arithmetic + failing negative control
    A = 4  # Kernel: Lean 4 compiled, zero sorry, foundational axioms only

    @property
    def rank(self) -> int:
        return self.value

    def __le__(self, other: "Tier") -> bool:
        return self.rank <= other.rank

    def __lt__(self, other: "Tier") -> bool:
        return self.rank < other.rank


def load_ledger(ledger_path: Path) -> Dict[str, Dict[str, Any]]:
    """Load and parse JSONL claims ledger."""
    claims = {}
    with open(ledger_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            claim = json.loads(line)
            cid = claim["id"]
            if cid in claims:
                raise ValueError(f"Duplicate claim ID {cid} at line {line_num}")
            
            # Check ID matches tier
            tier_letter = claim["tier"]
            if f"-{tier_letter}-" not in cid:
                raise ValueError(f"Claim ID {cid} mismatch with tier {tier_letter}")
                
            claims[cid] = claim
    return claims


def verify_ledger_soundness(claims: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Verify transitive tier monotonicity across all claim support relations:
    No claim may exceed the tier of anything reachable through its supports.
    """
    violations = []
    
    def get_tier(cid: str) -> Tier:
        if cid not in claims:
            raise KeyError(f"Missing support claim ID '{cid}' in ledger")
        return Tier[claims[cid]["tier"]]

    for cid, claim in claims.items():
        claim_tier = Tier[claim["tier"]]
        supports = claim.get("supports", [])
        
        # Traverse transitive dependency tree
        visited: Set[str] = set()
        queue = list(supports)
        
        while queue:
            curr = queue.pop(0)
            if curr in visited:
                continue
            visited.add(curr)
            
            supp_tier = get_tier(curr)
            # Monotonicity rule: claim_tier <= supp_tier
            if claim_tier > supp_tier:
                violations.append({
                    "claim_id": cid,
                    "claim_tier": claim_tier.name,
                    "supported_by": curr,
                    "supported_tier": supp_tier.name,
                    "error": f"Tier monotonicity violated: {cid} ({claim_tier.name}) depends on lower-tier {curr} ({supp_tier.name})",
                })
            
            # Add transitive dependencies
            for next_supp in claims[curr].get("supports", []):
                if next_supp not in visited:
                    queue.append(next_supp)

    return {
        "status": "PASSED" if not violations else "FAILED",
        "total_claims": len(claims),
        "violations": violations,
        "is_sound": len(violations) == 0,
    }


def audit_ledger_files(repo_root: Path) -> Dict[str, Any]:
    """Audit ledger.jsonl and check consistency with LEDGER.md."""
    ledger_jsonl = repo_root / "ledger.jsonl"
    ledger_md = repo_root / "LEDGER.md"

    if not ledger_jsonl.exists():
        raise FileNotFoundError(f"Missing {ledger_jsonl}")
    if not ledger_md.exists():
        raise FileNotFoundError(f"Missing {ledger_md}")

    claims = load_ledger(ledger_jsonl)
    soundness_res = verify_ledger_soundness(claims)

    if not soundness_res["is_sound"]:
        raise AssertionError(f"Ledger soundness verification failed: {soundness_res['violations']}")

    # Check that all IDs in jsonl appear in LEDGER.md
    md_text = ledger_md.read_text(encoding="utf-8")
    for cid in claims:
        if cid not in md_text:
            raise AssertionError(f"Claim {cid} present in ledger.jsonl but missing from LEDGER.md")

    return {
        "status": "PASSED",
        "total_claims_audited": len(claims),
        "soundness": soundness_res,
    }
