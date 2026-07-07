from __future__ import annotations
import re
from pathlib import Path
from typing import Any
from ev4_transition.canonical_json import load_json_file
from ev4_transition.runners.git_blobs import git_blob_sha256_from_runner

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
STAGES = ["architect", "ce", "builder", "responsive"]
REPOSITORIES = {
 "architect":"rezahh107/EV4-Architect-Repo",
 "ce":"rezahh107/EV4-Constructability-Engineer-Repo",
 "builder":"rezahh107/EV4-Builder-Assistant-Repo",
 "responsive":"rezahh107/EV4-Responsive-Architect",
}
ALLOWED_ROLES = {"handoff","adoption_doc","pipeline_manifest","stage_payload_schema","producer_gate_export_schema","producer_gate_export_lock","stage_bundle_schema","validator","ci_workflow","fixture","ce_stage_bundle_schema_reference"}

class RegistryError(Exception):
    def __init__(self, diagnostics: list[dict[str, Any]]):
        self.diagnostics=diagnostics
        super().__init__("producer registry invalid")

def validate_adoption_registry(path: str | Path = "contracts/producer-adoption/ev4-producer-adoption-set.v1.json") -> dict[str, Any]:
    reg=load_json_file(path)
    diags: list[dict[str, Any]]=[]
    if reg.get("schema_id")!="ev4-producer-adoption-set.v1": _d(diags,"$.schema_id","unexpected registry schema id")
    prompt0=reg.get("prompt_0") if isinstance(reg.get("prompt_0"),dict) else {}
    if prompt0.get("producer_gate_export_schema_sha256")!="c556bb9deeccdcafeb885a1c8b3dbd660e4e06f452b8ac3c7040d21377465fcc": _d(diags,"$.prompt_0.producer_gate_export_schema_sha256","Prompt 0 Producer Gate Export hash mismatch")
    if prompt0.get("stage_bundle_schema_sha256")!="fc1ec6d3f7aecbabaeb0a3455d9eb42788779d2fa1531e8c7b2cb3bde706a886": _d(diags,"$.prompt_0.stage_bundle_schema_sha256","Prompt 0 Stage Bundle hash mismatch")
    producers=reg.get("producers")
    if not isinstance(producers,list):
        _d(diags,"$.producers","producers must be an array")
    else:
        stages=[]
        for i,p in enumerate(producers):
            stage=p.get("stage") if isinstance(p,dict) else None; stages.append(stage)
            if stage not in STAGES: _d(diags,f"$.producers[{i}].stage","unexpected producer stage")
            elif p.get("repository")!=REPOSITORIES[stage]: _d(diags,f"$.producers[{i}].repository","wrong producer repository")
            pr_head=p.get("pr_head_sha"); runtime=p.get("runtime_pin",{}).get("merged_commit_sha") if isinstance(p.get("runtime_pin"),dict) else None
            for path,val in [(f"$.producers[{i}].pr_head_sha",pr_head),(f"$.producers[{i}].runtime_pin.merged_commit_sha",runtime)]:
                if not isinstance(val,str) or not SHA_RE.fullmatch(val): _d(diags,path,"commit must be lowercase 40-character SHA")
                if val in {"main","master"} or (isinstance(val,str) and val.startswith("refs/")): _d(diags,path,"moving refs are forbidden")
            if runtime == pr_head: _d(diags,f"$.producers[{i}].runtime_pin.merged_commit_sha","PR head cannot be used as runtime pin","PG-P05-PR-HEAD-AS-RUNTIME-PIN")
            roles=[]
            for j,a in enumerate(p.get("artifacts",[]) if isinstance(p.get("artifacts"),list) else []):
                role=a.get("role"); roles.append(role)
                if role not in ALLOWED_ROLES: _d(diags,f"$.producers[{i}].artifacts[{j}].role","unexpected artifact role")
                if a.get("verification_status")=="verified" and a.get("canonical_status")=="insufficient_evidence": _d(diags,f"$.producers[{i}].artifacts[{j}]","artifact cannot be verified when canonical record is insufficient_evidence")
            if roles != sorted(roles): _d(diags,f"$.producers[{i}].artifacts","artifact roles must be deterministically ordered")
            if not any(a.get("role")=="producer_gate_export_schema" for a in p.get("artifacts",[]) if isinstance(a,dict)): _d(diags,f"$.producers[{i}].artifacts","missing required Producer Gate Export schema record")
        if stages != STAGES: _d(diags,"$.producers","producer ordering must be architect, ce, builder, responsive and stages must be unique")
    return {"schema_version":"producer-adoption-validation-result.v1","status":"invalid" if diags else "valid","diagnostics":sorted(diags,key=lambda x:(x["path"],x["code"]))}

def git_blob_sha256(repo: str|Path, commit_sha: str, path: str) -> dict[str, Any]:
    if not SHA_RE.fullmatch(commit_sha):
        return {"status":"invalid","diagnostic":{"code":"PG-P05-MOVING-REF-FORBIDDEN","severity":"error","path":"$.commit_sha","message":"Only immutable lowercase commit SHAs are accepted.","repair_owner":"Project Gate"}}
    return git_blob_sha256_from_runner(repo, commit_sha, path)

def _d(diags,path,msg,code="PG-P05-PRODUCER-REGISTRY-INVALID"):
    diags.append({"code":code,"severity":"error","path":path,"message":msg,"details":{},"repair_owner":"Project Gate"})
