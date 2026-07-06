from __future__ import annotations

from ev4_transition.presentation.rtl import bdi_ltr, escape_html, isolate_ltr_text, ltr_code_block, rtl_text


def test_escape_html_escapes_markup_and_quotes():
    assert escape_html('<script data-x="1">') == "&lt;script data-x=&quot;1&quot;&gt;"


def test_bdi_ltr_isolates_technical_identifier_as_code():
    rendered = bdi_ltr("PG_A2C_EXTERNAL_HASH_MISMATCH")

    assert rendered == '<bdi dir="ltr"><code>PG_A2C_EXTERNAL_HASH_MISMATCH</code></bdi>'


def test_rtl_text_wraps_persian_text_with_rtl_attributes():
    rendered = rtl_text("مسیر local repository")

    assert rendered.startswith('<span lang="fa" dir="rtl">')
    assert "مسیر" in rendered


def test_ltr_code_block_keeps_raw_json_ltr():
    rendered = ltr_code_block('{"status":"accepted"}')

    assert rendered.startswith('<pre dir="ltr"><code>')
    assert "&quot;status&quot;" in rendered
    assert rendered.endswith("</code></pre>")


def test_plain_ltr_isolation_uses_unicode_isolates_for_table_cells():
    rendered = isolate_ltr_text("schemas/example.json")

    assert rendered.startswith("\u2066")
    assert rendered.endswith("\u2069")
