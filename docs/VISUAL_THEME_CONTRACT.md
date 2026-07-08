# Visual Theme Contract

این سند قرارداد theme token برای پنل محلی Project Gate است.

## Token owner

Semantic tokenها در این فایل تعریف می‌شوند:

```text
src/ev4_transition/presentation/theme_tokens.py
```

UI نباید رنگ‌های status، surface، input، control indicator، button، disabled یا modal را به‌صورت پراکنده و ناسازگار hard-code کند. مقدارهای hex در `theme_tokens.py` متمرکز می‌مانند و CSS/componentها باید از custom propertyهای `--ev4-*` یا Gradio theme variables مشتق‌شده از همان tokenها استفاده کنند.

## Required token groups

- `surface.base`
- `surface.raised`
- `surface.overlay`
- `surface.dialog`
- `text.primary`
- `text.secondary`
- `text.muted`
- `text.disabled`
- `border.subtle`
- `border.default`
- `border.strong`
- `accent.primary`
- `accent.hover`
- `accent.active`
- `focus.ring`
- `selection.bg`
- `success`
- `success.bg`
- `warning`
- `warning.bg`
- `danger`
- `danger.bg`
- `info`
- `info.bg`
- `input.bg`
- `input.border`
- `input.text`
- `control.indicator.bg`
- `control.indicator.border`
- `control.indicator.checked.bg`
- `control.indicator.checked.dot`
- `control.indicator.hover.bg`
- `control.indicator.focus.ring`
- `button.primary.bg`
- `button.primary.text`
- `button.secondary.bg`
- `button.secondary.text`
- `disabled.bg`
- `disabled.text`
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

## Theme resolution

Theme resolution باید predictable باشد:

1. انتخاب صریح کاربر/Gradio theme class اگر وجود داشته باشد.
2. `data-theme="light|dark"` اگر توسط shell یا host اضافه شده باشد.
3. `prefers-color-scheme` فقط fallback است، نه تنها driver.
4. default امن: Light theme.

`css_custom_properties()` باید برای حالت‌های زیر token مناسب صادر کند:

- default light
- system dark fallback با `@media (prefers-color-scheme: dark)`
- explicit light selectors مثل `:root[data-theme="light"]` و `body.light`
- explicit dark selectors مثل `:root[data-theme="dark"]` و `body.dark`

## Gradio integration

Gradio مالک بسیاری از componentها و Settings modal است. بنابراین:

- `src/ev4_transition/ui/app.py` باید یک Gradio theme بسازد و variableهای اصلی Gradio را به EV4 tokenها map کند.
- custom CSS فقط برای شکاف‌هایی استفاده شود که Gradio theme variables پوشش کافی ندارند.
- selectorهای global/brittle فقط در محدوده `.gradio-container` مجازند و باید برای readability-critical componentها باشند: modal، upload، accordion، radio، disabled و footer.

## Control indicators

Radio indicatorها نباید فقط به browser default یا `accent-color` وابسته باشند. قرارداد فعلی برای radio از semantic custom propertyهای زیر استفاده می‌کند:

```text
--ev4-control-indicator-bg
--ev4-control-indicator-border
--ev4-control-indicator-checked-bg
--ev4-control-indicator-checked-dot
--ev4-control-indicator-hover-bg
--ev4-control-indicator-focus-ring
```

رفتار لازم:

- unselected state باید در Light و Dark مرز قابل تشخیص داشته باشد.
- selected state باید با checked background و dot مستقل واضح باشد.
- focus-visible باید از ring مستقل و قابل اندازه‌گیری استفاده کند.
- hover state باید subtle اما قابل تشخیص باشد.

## Dark mode

Dark mode نباید pure black / pure white inversion باشد. surfaceها باید layered باشند و code background مستقل داشته باشد.

Dark Mode header نباید white/light island بسازد. `.ev4-header` در explicit Dark و fallback System Dark باید از dark raised/overlay surface و foreground tokenهای همان theme استفاده کند؛ نه از card سفید Light Mode.

اصل منتقل‌شده از `rezahh107/EV4-Workbook-Jinja` فقط shell-level theme coherence، layered dark surfaces، focus visibility، visible control indicators و Persian line-height است. Project Gate نباید palette یا identity آموزشی Workbook را کپی کند.

## Light mode

Light mode باید token-backed باشد و component boundaryهای مهم مثل input border، focus ring، radio indicator و primary button text/background باید contrast قابل اندازه‌گیری داشته باشند.

## Focus, disabled, modal and code

- focus ring token اجباری است.
- focus indicator باید در light و dark قابل مشاهده باشد.
- disabled state نباید صرفاً با opacity ناخوانا شود؛ `disabled.bg` و `disabled.text` باید readable باشند.
- Settings modal و dialog باید از `surface.dialog`, `text.primary`, `text.secondary`, `border.default` استفاده کنند.
- code background token اجباری است.
- technical content باید با font code و LTR isolation نمایش داده شود.

## Contrast carrier

Contrast-critical token pairها باید تست شوند:

- primary/secondary/muted text روی surfaceها
- primary/secondary button text روی button background
- input border و focus ring
- radio border روی radio background
- radio checked dot روی checked background
- radio focus ring روی relevant surface
- disabled text/background
- status foreground/background

حداقل‌ها:

- متن عادی: `4.5:1`
- متن بزرگ: `3:1`
- component/focus boundary: `3:1`

## Test carrier

`assert_theme_contract()` و tests مربوط به `theme_tokens.py` حامل regression برای shape قرارداد هستند.

`tests/theme_acceptance/test_theme_contrast.py` حامل regression برای contrast-critical token pairهاست.

`tests/ui/test_operator_panel_css.py` حامل regression برای CSS-level radio indicator styling و dark-header anti-regression selectorهاست.

Browser visual QA همچنان manual evidence لازم دارد و با token tests جایگزین نمی‌شود.
