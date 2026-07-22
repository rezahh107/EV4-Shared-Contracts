from __future__ import annotations

import importlib


def test_app_public_compatibility_surface() -> None:
    import ev4_transition.ui.app as app

    assert callable(app.build_demo)
    assert isinstance(app.HEADER_WARNING_FA, str)
    assert isinstance(app.HEADER_HELPER_FA, str)
    assert isinstance(app.PREFLIGHT_HELPER_FA, str)
    assert callable(app.operator_header_html)
    assert callable(app.operator_gradio_theme)
    assert callable(app.operator_panel_css)
    assert callable(app.operator_run_outputs)
    assert callable(app.workflow_state_html)
    assert callable(app.run_authoritative_preflight)
    assert callable(app.invalidate_preflight_state)
    assert callable(app.browse_directory)
    assert callable(app.open_directory)
    assert callable(app.open_output_folder)
    assert callable(app.repository_field_affects_request)


def test_build_demo_constructs_without_launch() -> None:
    from ev4_transition.ui.app import build_demo

    demo = build_demo()
    assert demo is not None


def test_primary_unified_action_is_constructed_without_persistent_authorization_state() -> None:
    from ev4_transition.ui.app import build_demo

    demo = build_demo()
    config = demo.get_config_file()
    components = config["components"]
    dependencies = config["dependencies"]

    buttons = {
        component.get("props", {}).get("value"): component
        for component in components
        if component.get("type") == "button"
    }
    primary = buttons["بررسی و اجرای Authoritative Project Gate"]
    preview = buttons["فقط نمایش Authoritative Preflight"]
    assert primary["props"]["interactive"] is True
    assert preview["props"]["interactive"] is True

    primary_clicks = [
        dependency
        for dependency in dependencies
        if (primary["id"], "click") in dependency.get("targets", [])
    ]
    assert len(primary_clicks) == 1
    begin = primary_clicks[0]
    assert begin.get("trigger_mode") == "once"
    prepare = [item for item in dependencies if item.get("trigger_after") == begin["id"]]
    assert len(prepare) == 1
    execute = [item for item in dependencies if item.get("trigger_after") == prepare[0]["id"]]
    assert len(execute) == 1
    finalize = [item for item in dependencies if item.get("trigger_after") == execute[0]["id"]]
    assert len(finalize) == 1

    function_names = {getattr(block.fn, "__name__", "") for block in demo.fns.values()}
    assert {"_begin", "_prepare", "_execute", "_finalize"} <= function_names
    assert "_run" not in function_names


def test_internal_ui_modules_do_not_import_public_facade() -> None:
    support = importlib.import_module("ev4_transition.ui.app_support")
    callbacks = importlib.import_module("ev4_transition.ui.app_callbacks")

    assert support.__name__.endswith("app_support")
    assert callbacks.__name__.endswith("app_callbacks")
    assert "ev4_transition.ui.app" not in {
        value.__name__
        for value in (support, callbacks)
    }
