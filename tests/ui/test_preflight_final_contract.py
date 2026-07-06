from __future__ import annotations

from ev4_transition.service.preflight import PreflightCheck, PreflightResult
from ev4_transition.ui.preflight_components import preflight_result_html


def test_final_preflight_rendering_states_it_is_not_full_gate_authority():
    result = PreflightResult(
        status="warnings",
        transition_choice="validate_bundle",
        summary_fa="⚠️ Preflight هشدار دارد.",
        checks=[
            PreflightCheck(
                id="transition.validate_bundle.validation_only",
                label_fa="نوع اجرای انتخاب‌شده",
                status="warning",
                message_fa="این انتخاب فقط اعتبارسنجی می‌کند و خروجی CE/Builder/Responsive نمی‌سازد.",
                technical_detail="transition_choice=validate_bundle",
                classification="validation_only_no_transition_output",
            )
        ],
    )

    rendered = preflight_result_html(result)

    assert '<section lang="fa" dir="rtl"' in rendered
    assert "Preflight اجرای کامل Project Gate نیست" in rendered
    assert "hash/schema/validator checks" in rendered
    assert '<bdi dir="ltr"><code>validate_bundle</code></bdi>' in rendered
    assert '<bdi dir="ltr"><code>validation_only_no_transition_output</code></bdi>' in rendered
