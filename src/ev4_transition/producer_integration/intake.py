from __future__ import annotations
import copy
from pathlib import Path
from typing import Any
from ev4_transition.canonical_json import canonical_dumps, load_json_file
from ev4_transition.producer_gate_export import ProducerGateExportValidator
from .registry import validate_adoption_registry

TRANSITIONS={"ce-intake":"architect-to-ce","builder-intake":"ce-to-builder","responsive-intake":"builder-to-responsive","final-evidence-gate":"final-evidence-gate"}

def load_transition_targets(path: str|Path="contracts/transition-targets/ev4-transition-targets.v1.json") -> dict[str,str]:
    data=load_json_file(path); return {x["handoff_target"]:x["transition_id"] for x in data.get("targets",[])}

def intake_producer_export(artifact: Any, *, transition_name: str|None=None, registry_path: str|Path="contracts/producer-adoption/ev4-producer-adoption-set.v1.json", targets_path: str|Path="contracts/transition-targets/ev4-transition-targets.v1.json", repository_root: str|Path=".") -> dict[str, Any]:
    original=canonical_dumps(artifact) if isinstance(artifact,(dict,list)) else None
    diags=[]; status="accepted"
    if not isinstance(artifact,dict):
        return _result("invalid", None, None, [{"code":"PG_EXPORT_SCHEMA_INVALID","severity":"error","path":"$","message":"Producer Gate Export input must be a JSON object.","details":{},"repair_owner":"Producer"}])
    item=copy.deepcopy(artifact)
    acq=item.get("acquisition_mode") if isinstance(item.get("acquisition_mode"),dict) else None
    if acq is None or "mode" not in acq:
        diags.append(_diag("PG-P05-ACQUISITION-MODE-MISSING","error","$.acquisition_mode","Explicit acquisition mode is required.","Producer"))
    elif acq.get("mode")!="producer_emitted_gate_artifact":
        diags.append(_diag("PG-P05-ACQUISITION-MODE-MISMATCH","error","$.acquisition_mode.mode","Selected mode must match producer_emitted_gate_artifact.","Producer"))
    if isinstance(acq,dict) and acq.get("silent_fallback_allowed") is not False:
        diags.append(_diag("PG-P05-SILENT-FALLBACK-FORBIDDEN","error","$.acquisition_mode.silent_fallback_allowed","Silent fallback is forbidden.","Project Gate"))
    if isinstance(acq,dict) and acq.get("evidence_sources") not in (None,["producer_emitted_gate_artifact"]):
        diags.append(_diag("PG-P05-EVIDENCE-MIXING-FORBIDDEN","error","$.acquisition_mode.evidence_sources","Evidence mixing is forbidden.","Project Gate"))
    common=ProducerGateExportValidator(repository_root).validate(item)
    for d in common.get("diagnostics",[]): diags.append({**d,"repair_owner":d.get("repair_owner","Producer")})
    reg_result=validate_adoption_registry(registry_path)
    if reg_result["status"]!="valid": diags.extend(reg_result["diagnostics"])
    reg=load_json_file(registry_path)
    prod=item.get("producer") if isinstance(item.get("producer"),dict) else {}
    match=None
    for p in reg.get("producers",[]):
        if p.get("stage")==prod.get("stage"): match=p
    if not match:
        diags.append(_diag("PG-P05-PRODUCER-REGISTRY-INVALID","error","$.producer.stage","Producer stage is not adopted.","Project Gate"))
    else:
        if prod.get("repository")!=match.get("repository"): diags.append(_diag("PG-P05-PRODUCER-REGISTRY-INVALID","error","$.producer.repository","Producer repository does not match adoption registry.","Producer"))
        if prod.get("commit_sha")!=match.get("runtime_pin",{}).get("merged_commit_sha"): diags.append(_diag("PG-P05-PRODUCER-REGISTRY-INVALID","error","$.producer.commit_sha","Producer commit must match merged runtime pin.","Producer"))
    target=(item.get("handoff") or {}).get("target") if isinstance(item.get("handoff"),dict) else None
    targets=load_transition_targets(targets_path)
    resolved=targets.get(target)
    if resolved is None:
        diags.append(_diag("PG-P05-HANDOFF-TARGET-INVALID","error","$.handoff.target","Unknown handoff target.","Producer"))
    if transition_name and resolved and transition_name != resolved:
        diags.append(_diag("PG-P05-HANDOFF-TARGET-INVALID","error","$.handoff.target","Handoff target does not match selected transition.","Producer", expected_transition=transition_name, actual_transition=resolved))
    if original is not None and canonical_dumps(artifact)!=original:
        diags.append(_diag("PG-P05-PRODUCER-ARTIFACT-MUTATED","error","$","Producer artifact was mutated during intake.","Project Gate"))
    if any(d["severity"]=="error" for d in diags): status="invalid"
    elif any(d["severity"]=="insufficient_evidence" for d in diags): status="insufficient_evidence"
    return _result(status, prod, resolved, sorted(diags,key=lambda x:(x["path"],x["code"])))

def transition_producer_export(transition_name: str, artifact: Any, **kwargs: Any) -> dict[str, Any]:
    result=intake_producer_export(artifact, transition_name=transition_name, **kwargs)
    result["transition_id"]=transition_name
    if result["status"]=="accepted":
        result["producer_validation"]={"status":"passed","official_validator_status":"not_run","note":"Project Gate shared intake accepted the producer-emitted envelope; official owner tool execution requires immutable local producer checkout in CI."}
        result["downstream_artifact"]={"status":"not_fabricated"}
    return result

def _result(status, producer, transition, diagnostics):
    return {"schema_version":"producer-emitted-transition-result.v1","status":status,"acquisition_mode":"producer_emitted_gate_artifact","producer":producer or {},"resolved_transition":transition,"common_validation":"passed" if status=="accepted" else "failed","diagnostics":diagnostics}

def _diag(code,severity,path,message,owner,**details):
    return {"code":code,"severity":severity,"path":path,"message":message,"details":details,"repair_owner":owner}
