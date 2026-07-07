# Prompt 4.5 Evidence Repair Log

Exact command/output log for immutable Git blob hash verification and CE discovery.

```text
$ git show ea19c22c32458068e167b267da8b819e9263cdf7:contracts/common/producer-gate-export.v1.schema.json | sha256sum
exit=0
c556bb9deeccdcafeb885a1c8b3dbd660e4e06f452b8ac3c7040d21377465fcc  -

$ git show ea19c22c32458068e167b267da8b819e9263cdf7:schemas/stage-bundle/stage-bundle.v1.schema.json | sha256sum
exit=0
fc1ec6d3f7aecbabaeb0a3455d9eb42788779d2fa1531e8c7b2cb3bde706a886  -

$ git show bf0b63c1f5d78725e7ea24371bab3360d9452a4f:docs/handoffs/PROMPT-01_HANDOFF.md | sha256sum
exit=0
a715eee7b1e0f0ecfa08c0fca43480dc3e9fc164506c493709d1a53209d63a82  -

$ git show bf0b63c1f5d78725e7ea24371bab3360d9452a4f:docs/PROJECT_GATE_PRODUCER_ADOPTION.md | sha256sum
exit=0
551d583414d3ac76277c4b15a69f187a8a4e0914b0c144d07a889609e8d8492c  -

$ git show bf0b63c1f5d78725e7ea24371bab3360d9452a4f:manifests/architect-pipeline-manifest.v1.json | sha256sum
exit=0
c045546175757a9bff884fc8c08423b52389135e3198a585eb250d1a431e08c4  -

$ git show bf0b63c1f5d78725e7ea24371bab3360d9452a4f:schemas/ev4-architect-stage-payload.v1.schema.json | sha256sum
exit=0
e14b330e98b27180446764c9fe9803bcc3e1c06de34893b4f4b192b8051e8da8  -

$ git show bf0b63c1f5d78725e7ea24371bab3360d9452a4f:contracts/project-gate/producer-gate-export.v1.schema.json | sha256sum
exit=0
c556bb9deeccdcafeb885a1c8b3dbd660e4e06f452b8ac3c7040d21377465fcc  -

$ git show bf0b63c1f5d78725e7ea24371bab3360d9452a4f:contracts/project-gate/producer-gate-export.v1.lock.json | sha256sum
exit=0
7cc33527d6d83032618ef4ab66f3bcc7fb6706e6f9521d560969621f1e089eda  -

$ git show bf0b63c1f5d78725e7ea24371bab3360d9452a4f:contracts/project-gate/stage-bundle.v1.schema.json | sha256sum
exit=0
fc1ec6d3f7aecbabaeb0a3455d9eb42788779d2fa1531e8c7b2cb3bde706a886  -

$ git show bf0b63c1f5d78725e7ea24371bab3360d9452a4f:scripts/check-architect-producer-gate-adoption.py | sha256sum
exit=0
94d49d62b8ba1c5291454b7d5317b3fedae320c85b73f8ac898e6473491bda34  -

$ git show bf0b63c1f5d78725e7ea24371bab3360d9452a4f:.github/workflows/verify-project-gate-contract.yml | sha256sum
exit=0
efab8ab7b9563b073b0d8ea7a539bee4a18262c15b00f6cf084bfef0a1c15f09  -

$ git show bf0b63c1f5d78725e7ea24371bab3360d9452a4f:.github/workflows/validate-architect-producer-gate-adoption.yml | sha256sum
exit=0
db03bbfc09c27921a3114548b518d3330f8d2480c4ee6287750a924168951df2  -

$ git show bf0b63c1f5d78725e7ea24371bab3360d9452a4f:fixtures/build-tree/valid/voice-assistant-reference.v1.json | sha256sum
exit=0
5e9412fd9de9d85a9256a22b6109e97cb93f71565dac4eb12539aedba909355e  -

$ git show bf0b63c1f5d78725e7ea24371bab3360d9452a4f:fixtures/project-gate-export/valid/blocked-run.v1.json | sha256sum
exit=0
5496b1aa9329294d6a01e4e4af1335a3c2408b60b937cd21f343470cf12d4bfe  -

$ git show bf0b63c1f5d78725e7ea24371bab3360d9452a4f:fixtures/build-tree/invalid/cases.v1.json | sha256sum
exit=0
110b1890a483afe92375421bbceb2b43c4b08ea23998f17e0ccdfc46739163fb  -

$ git show bf0b63c1f5d78725e7ea24371bab3360d9452a4f:fixtures/project-gate-export/invalid/cases.v1.json | sha256sum
exit=0
79d59a3eba5e4b4fe2e91ce244a093175ee9f5e541a8174cbe47b352dbd4e5a1  -

$ git show 189163669cca0caf5adb62c97d78dae580129f15:patch-reports/CE_PROJECT_GATE_PRODUCER_ADOPTION.md | sha256sum
exit=0
51c7a9a224e2a605df63cf5916ad93e52a3883f329ef81f958b497f72ef77be0  -

$ git show 189163669cca0caf5adb62c97d78dae580129f15:manifests/ce_pipeline_manifest.v1.json | sha256sum
exit=0
917e523c03eda3b1cc98b47266ee5364533dca08db711b9f4f5b9a9515936af6  -

$ git show 189163669cca0caf5adb62c97d78dae580129f15:schemas/ce_pipeline_manifest.v1.schema.json | sha256sum
exit=0
dae84e8b98585c9838e3a5a426e91b24bff729bac0f50b9f11dc58333497deaf  -

$ git show 189163669cca0caf5adb62c97d78dae580129f15:schemas/ce_stage_payload.v1.schema.json | sha256sum
exit=0
88871da4ac5906fa222cb4d9eb8614b8a4570f603acc5b0f13861674992b8fd8  -

$ git show 189163669cca0caf5adb62c97d78dae580129f15:contracts/project-gate/producer-gate-export.v1.schema.json | sha256sum
exit=0
c556bb9deeccdcafeb885a1c8b3dbd660e4e06f452b8ac3c7040d21377465fcc  -

$ git show 189163669cca0caf5adb62c97d78dae580129f15:contracts/project-gate/producer-gate-export.v1.lock.json | sha256sum
exit=0
1168b5b55fb07408bdad9605364201c72006adf3089168028c11bedf7ce4dc40  -

$ git show 189163669cca0caf5adb62c97d78dae580129f15:validator/project_gate_export.py | sha256sum
exit=0
3d427723d44500bf827064f98deeefde601f90d171e956bd2ef7c033d3be3a6e  -

$ git show 189163669cca0caf5adb62c97d78dae580129f15:scripts/validate-project-gate-producer-adoption.py | sha256sum
exit=0
e9782b5bbf01fa80a60bdd6018d94935f4bab074eb2a4a10f5328da0a715a749  -

$ git show 189163669cca0caf5adb62c97d78dae580129f15:.github/workflows/verify-project-gate-contract.yml | sha256sum
exit=0
45cbfb717cc4acc6915ed4f514f79d818b7ac2239d2ed5b0d1f23877d982bdf8  -

$ git show 189163669cca0caf5adb62c97d78dae580129f15:fixtures/project_gate_export/valid_blocked_ce_producer_gate_export.json | sha256sum
exit=0
d5a6b6530e342f2cc7cb1559647c1ac77b774b714b833148fa29022c3859a1a8  -

$ git show 189163669cca0caf5adb62c97d78dae580129f15:fixtures/project_gate_export/invalid_silent_fallback_true.json | sha256sum
exit=0
0895c5614a8d7ae08aa8b65ae9b9343d3947bfdeded5f1b0d38dcaafd6e91de3  -

$ git show 45459d0246f5d14486867224d26c2d2ba8a563b6:docs/handoffs/PROMPT-03_HANDOFF.md | sha256sum
exit=0
0dc210e503cd5863bb717048fdc6acab2088f7cfe90e194246dfbfac054ee8d9  -

$ git show 45459d0246f5d14486867224d26c2d2ba8a563b6:docs/BUILDER_PRODUCER_GATE_EXPORT.md | sha256sum
exit=0
c277e8145462e17187c1272fd1bfd4450a9da82850c0b0a94960e0291b2e10c9  -

$ git show 45459d0246f5d14486867224d26c2d2ba8a563b6:data/builder-pipeline-manifest.v1.json | sha256sum
exit=0
fda607c75a95ffb5c2b058a5f6a81eb91817cbacbe3df189a08f24c9e3e5f50e  -

$ git show 45459d0246f5d14486867224d26c2d2ba8a563b6:schemas/builder-stage-payload.schema.json | sha256sum
exit=0
d71c019ba54462f2a1e0997e34c1caaea7f8264add0d7e09a7ed4706a90921cf  -

$ git show 45459d0246f5d14486867224d26c2d2ba8a563b6:schemas/responsive-handoff-candidate.schema.json | sha256sum
exit=0
1d0f3c1c38608e2bd9585cba6a16a353e0466b535da9dc3b3df5405cb8423f62  -

$ git show 45459d0246f5d14486867224d26c2d2ba8a563b6:contracts/project-gate/producer-gate-export.v1.schema.json | sha256sum
exit=0
c556bb9deeccdcafeb885a1c8b3dbd660e4e06f452b8ac3c7040d21377465fcc  -

$ git show 45459d0246f5d14486867224d26c2d2ba8a563b6:contracts/project-gate/producer-gate-export.v1.lock.json | sha256sum
exit=0
327604bfc91294585355ce2720a5eeec01452117842ea55ceaaf335243722f9d  -

$ git show 45459d0246f5d14486867224d26c2d2ba8a563b6:contracts/project-gate/stage-bundle.v1.schema.json | sha256sum
exit=0
fc1ec6d3f7aecbabaeb0a3455d9eb42788779d2fa1531e8c7b2cb3bde706a886  -

$ git show 45459d0246f5d14486867224d26c2d2ba8a563b6:scripts/validate-builder-producer-adoption.mjs | sha256sum
exit=0
c59185c9e48f34d4f5a24a78f0f991c46e5dba0ae7279f5a7641b0c83742dae2  -

$ git show 45459d0246f5d14486867224d26c2d2ba8a563b6:.github/workflows/verify-project-gate-contract.yml | sha256sum
exit=0
004d075311322e6a4d7a1335a45c0ecc55b0329ad4c26063027bc23a3370ee9a  -

$ git show 45459d0246f5d14486867224d26c2d2ba8a563b6:tests/valid/builder_stage_payload_minimal.json | sha256sum
exit=0
98f81c387397a507b70eb8dc4d0a8e728c5dc5ed44630bb181e80c8e9210c6d8  -

$ git show 45459d0246f5d14486867224d26c2d2ba8a563b6:tests/invalid/builder_stage_payload_completed_claims_production_ready.json | sha256sum
exit=0
5cfa49a1b7e699e613e1ce09565a8da171a27493377e7d8662839abf75970e92  -

$ git show 28a995a603a5a383b8592d6beae7db8943f20acf:docs/handoffs/PROMPT-04_HANDOFF.md | sha256sum
exit=0
84d3807b7644b67c3600fc6f4e2031c2430ad4a23b8a15f50b146ea4ddef0799  -

$ git show 28a995a603a5a383b8592d6beae7db8943f20acf:docs/45_PROJECT_GATE_PROMPT04_RESPONSIVE_PRODUCER_ADOPTION.md | sha256sum
exit=0
036dffdd560cd1760970939d527e387fddd24ba7cf92e598164284cefd1afa12  -

$ git show 28a995a603a5a383b8592d6beae7db8943f20acf:manifests/ev4-responsive-pipeline-manifest.v1.json | sha256sum
exit=0
11d4574f55b6e192059e2f8fb272f677eb1ece2c0a656a64387981e989f45a31  -

$ git show 28a995a603a5a383b8592d6beae7db8943f20acf:schemas/ev4-responsive-stage-payload.v1.schema.json | sha256sum
exit=0
25bf78e28d38884a6db9201e698cdf340efeed98f6efe0c5b5b51b22a61c506c  -

$ git show 28a995a603a5a383b8592d6beae7db8943f20acf:schemas/ev4-responsive-viewport-source-ledger.v1.schema.json | sha256sum
exit=0
64c0a5502dd4485b0fbb9aa2803e7ff9b3a4611a414b88626540fec7c4fb971b  -

$ git show 28a995a603a5a383b8592d6beae7db8943f20acf:registries/breakpoint-profiles.v1.json | sha256sum
exit=0
543266ef038681293e2b40349c2f9a750a068f7dd325538dd87f44e122beae30  -

$ git show 28a995a603a5a383b8592d6beae7db8943f20acf:registries/elementor-responsive-capabilities.v1.json | sha256sum
exit=0
d86373277b52e84c4d2b7608e38aa0b062397a1c7323fbd767bcae402c85f315  -

$ git show 28a995a603a5a383b8592d6beae7db8943f20acf:contracts/project-gate/producer-gate-export.v1.schema.json | sha256sum
exit=0
c556bb9deeccdcafeb885a1c8b3dbd660e4e06f452b8ac3c7040d21377465fcc  -

$ git show 28a995a603a5a383b8592d6beae7db8943f20acf:contracts/project-gate/producer-gate-export.v1.lock.json | sha256sum
exit=0
2253727ecfda01dd46a1b876868b389c5be0efb0fc806441bdd6a2d77dcafaa8  -

$ git show 28a995a603a5a383b8592d6beae7db8943f20acf:contracts/project-gate/common-contract-lock.v1.schema.json | sha256sum
exit=0
7beaae340e1321d8c9f35c77e024e1bd7796c9b476cf5d9e0b7714ed903d2137  -

$ git show 28a995a603a5a383b8592d6beae7db8943f20acf:schemas/project-gate/stage-bundle.v1.schema.json | sha256sum
exit=0
0479e8866c258f9dc563ba332b5fc68f0ea1b415ae9ae261deeda16086a4b1cf  -

$ git show 28a995a603a5a383b8592d6beae7db8943f20acf:validation/project_gate/validate_responsive_producer_adoption.py | sha256sum
exit=0
0f3023bda95150b652c324e6070817648ae36a12b9b496aa2dc852c625578aad  -

$ git show 28a995a603a5a383b8592d6beae7db8943f20acf:.github/workflows/verify-vendored-common-contract.yml | sha256sum
exit=0
b0631bf2ad49efd7b4738721e6ecee77b63d2a9fd89e8a37aaaf853e105628b7  -

$ git show 28a995a603a5a383b8592d6beae7db8943f20acf:validation/fixtures/prompt04/valid/responsive_producer_gate_export.valid.json | sha256sum
exit=0
764b28a6d87851d9b96558dedbbdaf53de9a0d592e144d8b3a563c7caf5a5578  -

$ git show 28a995a603a5a383b8592d6beae7db8943f20acf:validation/fixtures/prompt04/valid/responsive_stage_payload.valid.json | sha256sum
exit=0
f6e4ca2afbff56b15b98d7df92fbb6b49f6676abb46b883b8f4a4cda4bcdb5d3  -

$ git show 28a995a603a5a383b8592d6beae7db8943f20acf:validation/fixtures/prompt04/invalid/responsive_producer_gate_export_silent_fallback.invalid.json | sha256sum
exit=0
4eda796b71a5c6e10f173210e4435d5cb4a60070f4d14a84dd8e41adf546881e  -

$ git show 28a995a603a5a383b8592d6beae7db8943f20acf:validation/fixtures/prompt04/invalid/responsive_stage_payload_cross_viewport.invalid.json | sha256sum
exit=0
c756b640d89a6977a0875bf4da89e89cf80cc0153a337a8cb841b411957bd81d  -

$ git ls-tree -r --name-only 189163669cca0caf5adb62c97d78dae580129f15 | grep -E 'stage-bundle|stage_bundle|project-gate'
exit=0
.github/workflows/verify-project-gate-contract.yml
contracts/project-gate/producer-gate-export.v1.lock.json
contracts/project-gate/producer-gate-export.v1.schema.json
fixtures/architect-stage-intake-v1-1/insufficient-evidence/project-gate-transition-insufficient.v1_1.json
fixtures/architect-stage-intake-v1-1/source-bundles/synthetic-architect-stage-bundle.v1.json
fixtures/architect-stage-intake-v1-1/valid/project-gate-transition-complete.v1_1.json
fixtures/architect-stage-intake/insufficient-evidence/missing-real-architect-stage-bundle.v1.json
scripts/validate-project-gate-producer-adoption.py

$ git show 189163669cca0caf5adb62c97d78dae580129f15:docs/handoffs/PROMPT-02_HANDOFF.md | sha256sum
exit=0
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  -
fatal: path 'docs/handoffs/PROMPT-02_HANDOFF.md' exists on disk, but not in '189163669cca0caf5adb62c97d78dae580129f15'

$ git show 189163669cca0caf5adb62c97d78dae580129f15:patch-reports/CE_PROJECT_GATE_PRODUCER_ADOPTION.md | sha256sum
exit=0
51c7a9a224e2a605df63cf5916ad93e52a3883f329ef81f958b497f72ef77be0  -

```

## CE standard handoff missing-path control

The pipeline `git show <missing-path> | sha256sum` can hash empty input after `git show` fails, so this control records path existence separately for the standard CE handoff missing-path decision. Verified artifact hashes above remain computed with the required `git show <commit_sha>:<path> | sha256sum` method.

```text
$ git cat-file -e 189163669cca0caf5adb62c97d78dae580129f15:docs/handoffs/PROMPT-02_HANDOFF.md
exit=128
fatal: path 'docs/handoffs/PROMPT-02_HANDOFF.md' exists on disk, but not in '189163669cca0caf5adb62c97d78dae580129f15'
```
