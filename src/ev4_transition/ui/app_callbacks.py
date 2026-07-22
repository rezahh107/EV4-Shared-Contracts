from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, Callable

from ev4_transition.service import execute_authoritative_gate_transaction, prepare_authoritative_gate_transaction

from .adapters import build_capability_rows, build_gate_request, ui_output_from_response
from .app_support import (
    ExecutedUiOperation,
    PreparedUiOperation,
    operator_run_outputs,
    repository_field_affects_request,
    run_authoritative_preflight,
    stale_preflight_html,
    workflow_state_html,
)
from .preflight_components import preflight_diagnostic_rows, preflight_result_html
from .source_preflight import classify_source_file
from .state import (
    begin_workflow,
    block_workflow,
    complete_workflow,
    invalidate_workflow,
    mark_running,
    operation_is_current,
    record_preview,
    transition_choices,
)


@dataclass(frozen=True)
class OperatorCallbacks:
    classify_source: Callable[..., Any]
    classify_project_gate: Callable[..., Any]
    preview: Callable[..., Any]
    begin: Callable[..., Any]
    prepare: Callable[..., Any]
    execute: Callable[..., Any]
    finalize: Callable[..., Any]
    invalidate: Callable[..., Any]


def build_operator_callbacks(gr: Any) -> OperatorCallbacks:
    def _classify_source(source, project_gate, current_state):
        payload = classify_source_file(source, project_gate)
        message = escape(str(payload.get("message_fa", "")))
        schema = escape(str(payload.get("source_schema") or "unknown"))
        html = f'<section class="ev4-status-content ev4-classification" lang="fa" dir="rtl"><p>{message}</p><p><b>schema:</b> <bdi dir="ltr">{schema}</bdi></p></section>'
        selected_transition = payload.get("selected_transition") or transition_choices()[0]
        selected_mode = payload.get("selected_acquisition_mode") or "pinned_owner_file_computation"
        updated = invalidate_workflow(current_state, relevant=True, detail_fa="فایل source تغییر کرد؛ نتیجه قبلی stale شد.")
        return (
            html,
            gr.update(value=selected_transition),
            gr.update(value=selected_mode),
            updated,
            workflow_state_html(updated),
            stale_preflight_html(),
            None,
            None,
            None,
            gr.update(interactive=False),
            gr.update(interactive=not current_state.active),
        )

    def _classify_project_gate(source, project_gate, selected_transition, selected_mode, current_state):
        payload = classify_source_file(source, project_gate)
        message = escape(str(payload.get("message_fa", "")))
        schema = escape(str(payload.get("source_schema") or "unknown"))
        html = f'<section class="ev4-status-content ev4-classification" lang="fa" dir="rtl"><p>{message}</p><p><b>schema:</b> <bdi dir="ltr">{schema}</bdi></p></section>'
        relevant = repository_field_affects_request(selected_transition, selected_mode, "project_gate_repo_path")
        updated = invalidate_workflow(current_state, relevant=relevant)
        if not relevant:
            return html, updated, workflow_state_html(updated), gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip()
        return (
            html,
            updated,
            workflow_state_html(updated),
            stale_preflight_html(),
            None,
            None,
            None,
            gr.update(interactive=False),
            gr.update(interactive=not current_state.active),
        )

    def _preview(selected_transition, selected_mode, pasted, uploaded, project_gate, architect, ce, builder, responsive, kernel, output, current_state):
        result, _token = run_authoritative_preflight(
            selected_transition, selected_mode, pasted, uploaded, project_gate, architect, ce, builder, responsive, kernel, output
        )
        updated = record_preview(current_state, result.status)
        return preflight_result_html(result), preflight_diagnostic_rows(result), updated, workflow_state_html(updated)

    def _begin(current_state):
        updated = begin_workflow(current_state)
        return updated, workflow_state_html(updated), gr.update(interactive=False), gr.update(interactive=False), None, None

    def _prepare(selected_transition, selected_mode, pasted, uploaded, project_gate, architect, ce, builder, responsive, kernel, output, current_state):
        request = build_gate_request(
            selected_transition,
            pasted_json=pasted,
            uploaded_file=uploaded,
            project_gate_repo_path=project_gate,
            architect_repo_path=architect,
            ce_repo_path=ce,
            builder_repo_path=builder,
            responsive_repo_path=responsive,
            kernel_repo_path=kernel,
            acquisition_mode=selected_mode,
            output_dir=output,
        )
        transaction = prepare_authoritative_gate_transaction(request)
        prepared = PreparedUiOperation(
            operation_id=current_state.operation_id,
            input_revision=current_state.operation_revision if current_state.operation_revision is not None else current_state.input_revision,
            acquisition_mode=selected_mode,
            transaction=transaction,
        )
        if not transaction.authorization_ready:
            status = transaction.preflight.status
            detail = (
                "Preflight با warnings پایان یافت؛ طبق قرارداد فعلی warnings مجوز dispatch نمی‌دهد."
                if status == "warnings"
                else "Preflight مسدود است؛ اولین diagnostic خطادار را اصلاح کنید."
            )
            updated = block_workflow(
                current_state,
                prepared.operation_id,
                prepared.input_revision,
                detail_fa=detail,
            )
        else:
            updated = current_state
        return (
            prepared,
            updated,
            workflow_state_html(updated),
            preflight_result_html(transaction.preflight),
            preflight_diagnostic_rows(transaction.preflight),
        )

    def _execute(prepared, current_state):
        if not isinstance(prepared, PreparedUiOperation):
            failed_state = complete_workflow(
                current_state,
                current_state.operation_id,
                current_state.operation_revision if current_state.operation_revision is not None else current_state.input_revision,
                failed=True,
            )
            return ExecutedUiOperation(current_state.operation_id, current_state.input_revision, "unknown", failed=True, error_type="MissingPreparedOperation"), failed_state, workflow_state_html(failed_state)
        if not prepared.transaction.authorization_ready:
            return ExecutedUiOperation(prepared.operation_id, prepared.input_revision, prepared.acquisition_mode, blocked=True), current_state, workflow_state_html(current_state)
        if current_state.status != "checking":
            stale_state = invalidate_workflow(
                current_state,
                relevant=True,
                detail_fa="این prepared operation قبلاً شروع شده یا دیگر فعال نیست؛ dispatch تکراری انجام نشد.",
            )
            return ExecutedUiOperation(prepared.operation_id, prepared.input_revision, prepared.acquisition_mode, stale=True), stale_state, workflow_state_html(stale_state)
        running_state = mark_running(current_state, prepared.operation_id, prepared.input_revision)
        if running_state.status == "stale":
            return ExecutedUiOperation(prepared.operation_id, prepared.input_revision, prepared.acquisition_mode, stale=True), running_state, workflow_state_html(running_state)
        try:
            transaction = execute_authoritative_gate_transaction(prepared.transaction)
            if transaction.response is None:
                blocked_state = block_workflow(
                    running_state,
                    prepared.operation_id,
                    prepared.input_revision,
                    detail_fa="Fingerprint معتبر صادر نشد؛ dispatch انجام نشد.",
                )
                return ExecutedUiOperation(prepared.operation_id, prepared.input_revision, prepared.acquisition_mode, blocked=True), blocked_state, workflow_state_html(blocked_state)
            output = ui_output_from_response(transaction.response, prepared.acquisition_mode)
            return ExecutedUiOperation(prepared.operation_id, prepared.input_revision, prepared.acquisition_mode, output=output), running_state, workflow_state_html(running_state)
        except Exception as exc:  # Defensive UI boundary.
            failed_state = complete_workflow(
                running_state,
                prepared.operation_id,
                prepared.input_revision,
                failed=True,
            )
            return ExecutedUiOperation(
                prepared.operation_id,
                prepared.input_revision,
                prepared.acquisition_mode,
                failed=True,
                error_type=type(exc).__name__,
            ), failed_state, workflow_state_html(failed_state)

    def _finalize(executed, current_state):
        run_update = gr.update(interactive=True)
        preview_update = gr.update(interactive=True)
        if not isinstance(executed, ExecutedUiOperation):
            return (
                gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.update(interactive=False), None,
                current_state, workflow_state_html(current_state), run_update, preview_update,
            )
        if executed.stale or not operation_is_current(current_state, executed.operation_id, executed.input_revision):
            stale_state = invalidate_workflow(
                current_state,
                relevant=True,
                detail_fa="نتیجه عملیات قدیمی نادیده گرفته شد؛ ورودی فعلی را دوباره اجرا کنید.",
            )
            return (
                gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.update(interactive=False), None,
                stale_state, workflow_state_html(stale_state), run_update, preview_update,
            )
        if executed.blocked:
            return (
                workflow_state_html(current_state), gr.skip(), gr.skip(), "", [], gr.update(interactive=False), None,
                current_state, workflow_state_html(current_state), run_update, preview_update,
            )
        if executed.failed or executed.output is None:
            failed_state = complete_workflow(
                current_state,
                executed.operation_id,
                executed.input_revision,
                failed=True,
            )
            summary = workflow_state_html(failed_state)
            if executed.error_type:
                summary = summary.replace("</section>", f'<p><bdi dir="ltr">error_type={escape(executed.error_type)}</bdi></p></section>')
            return (
                summary, [], build_capability_rows(), "", [], gr.update(interactive=False), None,
                failed_state, workflow_state_html(failed_state), run_update, preview_update,
            )
        completed_state = complete_workflow(
            current_state,
            executed.operation_id,
            executed.input_revision,
        )
        attempt = executed.output.result.get("attempt_directory")
        open_enabled = bool(attempt and Path(str(attempt)).is_dir())
        return (
            *operator_run_outputs(executed.output),
            gr.update(interactive=open_enabled),
            attempt,
            completed_state,
            workflow_state_html(completed_state),
            run_update,
            preview_update,
        )

    def _invalidate(current_state, selected_transition, selected_mode, field_name):
        repository_fields = {
            "project_gate_repo_path",
            "architect_repo_path",
            "ce_repo_path",
            "builder_repo_path",
            "responsive_repo_path",
            "kernel_repo_path",
        }
        relevant = True
        if field_name in repository_fields:
            relevant = repository_field_affects_request(selected_transition, selected_mode, field_name)
        updated = invalidate_workflow(current_state, relevant=relevant)
        if not relevant:
            return current_state, gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip()
        return (
            updated,
            workflow_state_html(updated),
            stale_preflight_html(),
            None,
            None,
            None,
            gr.update(interactive=False),
        )

    return OperatorCallbacks(
        classify_source=_classify_source,
        classify_project_gate=_classify_project_gate,
        preview=_preview,
        begin=_begin,
        prepare=_prepare,
        execute=_execute,
        finalize=_finalize,
        invalidate=_invalidate,
    )
