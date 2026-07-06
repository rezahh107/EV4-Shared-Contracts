# Visual Theme Contract

این سند قرارداد theme token برای پنل محلی Project Gate است.

## Token owner

Semantic tokenها در این فایل تعریف می‌شوند:

```text
src/ev4_transition/presentation/theme_tokens.py
```

UI نباید رنگ‌های status یا surface را به‌صورت پراکنده و ناسازگار hard-code کند.

## Required token groups

- `surface.base`
- `surface.raised`
- `surface.overlay`
- `text.primary`
- `text.secondary`
- `border.subtle`
- `border.default`
- `border.strong`
- `accent.primary`
- `accent.hover`
- `focus.ring`
- `code.bg`
- `shadow.raised`
- `font.fa_ui`
- `font.code`

## Required status tokens

برای هر status زیر باید token مستقل وجود داشته باشد:

- `accepted`
- `repair_needed`
- `insufficient_evidence`
- `invalid`

هر status token باید شامل این فیلدها باشد:

- `tone`
- `foreground`
- `background`
- `icon`
- `label`

Status نباید فقط با رنگ منتقل شود؛ icon + label + semantic tone لازم است.

## Dark mode

Dark mode نباید pure black / pure white inversion باشد. surfaceها باید layered باشند و code background مستقل داشته باشد.

## Focus and code

- focus ring token اجباری است.
- code background token اجباری است.
- technical content باید با font code نمایش داده شود.

## Test carrier

`assert_theme_contract()` و tests مربوط به `theme_tokens.py` حامل regression برای این قرارداد هستند.
