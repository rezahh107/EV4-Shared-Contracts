# PROMPT-08 Handoff — Local Operator Panel User Guide

```yaml
prompt: PROMPT-08
scope: documentation_only
branch: project-gate-prompt-08-operator-user-guide
base_branch: main
base_sha: 4598f51fd8599e4ca77d4760431d646af4d7b93f
status: ready_for_review
```

## هدف

افزودن مستندات فارسی کاربردی برای پنل محلی `EV4 Project Gate` بر اساس UI و service implementation موجود، بدون تغییر در transition semantics، schemaها، validatorها، adapterها یا capability truth.

این scope اکنون دو سطح دارد:

1. مرجع جامع و جزءبه‌جزء برای تمام componentهای UI؛
2. شروع سریع کوتاه برای استفاده شخصی و روزمره، تصمیم‌گیری بر اساس هدف، status و artifact.

## Commitها

| Commit | شرح |
|---|---|
| `7dd4755c6e01faebe1fa2d8d98d2eab9d75eec65` | افزودن راهنمای جامع پنل محلی |
| `1f1b935ad2395801a8a01334d7c4d8997a6bbf0f` | لینک دادن راهنمای جامع از `docs/OPERATOR_GUIDE.md` |
| `584defa6921fb8ee156c5a72771cc08e5301f5b4` | افزودن راهنما به فهرست اسناد مرتبط پنل |
| `1e001673a91bc28397648ce326b6fd338dd3c99f` | افزودن شروع سریع شخصی و task-oriented |
| `0de96388841fa85e96a62a20424e50413f35b698` | لینک دادن شروع سریع از Operator Guide |
| `c3e5723907d3589517decaf32b87dcba346ed65b` | افزودن شروع سریع به اسناد مرتبط UI |
| `c53888361903d3a63c0af37f299bf61762d6160b` | اصلاح command نصب fallback در سند UI |

## فایل‌های تغییرکرده

- `docs/LOCAL_OPERATOR_PANEL_USER_GUIDE.fa.md` — توضیح 61 جزء رابط، جریان استفاده، statusها، Diagnostics، Capabilities، outputها، خطاهای رایج و troubleshooting.
- `docs/LOCAL_OPERATOR_PANEL_QUICK_START.fa.md` — شروع سریع پنج‌دقیقه‌ای، جدول انتخاب transition، جدول اقدام بعد از status، قواعد artifact و خطاهای سریع.
- `docs/OPERATOR_GUIDE.md` — لینک مستقیم به شروع سریع و راهنمای جامع.
- `docs/UI_OPERATOR_PANEL.md` — افزودن شروع سریع و راهنمای جامع به اسناد مرتبط.
- `docs/handoffs/PROMPT-08_HANDOFF.md` — این handoff.

## شواهد و منابع بررسی‌شده

- `src/ev4_transition/ui/app.py`
- `src/ev4_transition/ui/adapters.py`
- `src/ev4_transition/ui/components.py`
- `src/ev4_transition/ui/preflight_components.py`
- `src/ev4_transition/ui/state.py`
- `src/ev4_transition/service/preflight_core.py`
- `src/ev4_transition/data/capability-status.v1.json`
- `docs/OPERATOR_GUIDE.md`
- `docs/UI_OPERATOR_PANEL.md`
- `docs/UI_SERVICE_CONTRACT.md`
- `docs/PG_A2C_OPERATOR_WORKFLOW.md`
- `docs/PG_C2B_OPERATOR_WORKFLOW.md`
- تصویر UI ارائه‌شده توسط مالک پروژه در گفتگو

## تست‌ها و بررسی‌ها

### انجام‌شده

- تطبیق متن راهنمای جامع با componentهای قابل مشاهده در `src/ev4_transition/ui/app.py`.
- تطبیق path requirementها و Preflight با service code و operator docs.
- افزودن مسیر کوتاه با یک action اصلی در هر step و جدول تصمیم بر اساس هدف کاربر.
- ثبت صریح `verified_against_commit` و `last_reviewed` در شروع سریع.
- حفظ تفکیک `result.json` از downstream artifact.
- معرفی workflowهای رسمی A2C و C2B برای تولید artifact مستقل و receipt جداگانه.
- حفظ fail-closed semantics برای `insufficient_evidence`.
- حفظ boundary: مستندات capability، evidence یا readiness claim جدیدی ایجاد نمی‌کنند.
- بازبینی commandهای اجرای UI و fallback نصب پس از ویرایش.

### اجرا نشده

هیچ test suite یا GitHub Actions اجرا نشد، چون این تغییر documentation-only است و کد اجرایی، schema، workflow یا dependency را تغییر نمی‌دهد.

```yaml
tests_run: []
tests_not_run:
  - pytest
  - UI runtime smoke
  - GitHub Actions
reason: documentation-only change
```

## Behavioral Rule Coverage

هیچ behavioral rule به status بالاتری ارتقا داده نشد.

```yaml
coverage_advanced: []
coverage_unchanged: true
new_validator: false
new_fixture: false
new_ci_enforcement: false
new_downstream_contract: false
```

## Diagnostics و CLI/CI

```yaml
new_diagnostics: []
cli_changes: none
ci_changes: none
schema_changes: none
transition_semantics_changes: none
```

## تصمیم‌های طراحی

1. راهنمای جامع به‌عنوان UI Reference حفظ شد و بزرگ‌تر نشد.
2. شروع سریع در فایل مستقل اضافه شد تا کاربر شخصی برای کار روزمره مجبور به مرور راهنمای 780 خطی نباشد.
3. شروع سریع از هدف کاربر آغاز می‌شود و سپس transition، JSON، path و خروجی مورد انتظار را مشخص می‌کند.
4. procedureها کوتاه، شماره‌دار و action-oriented نوشته شدند.
5. technical identifierها، pathها، statusها و codeها به‌صورت LTR و copyable نگه داشته شدند.
6. `result.json`، `report.md` و `report.html` صریحاً report artifact هستند، نه downstream semantic input.
7. برای A2C و C2B فقط workflowهای رسمی repository به‌عنوان مسیر تولید `ce-input.json` و `builder-input.json` معرفی شدند؛ extraction یا بازسازی دستی ممنوع باقی ماند.
8. limitationهای فعلی با زبان fail-closed توضیح داده شدند و هیچ مسیر موفقیت یا evidence فرضی اضافه نشد.

## Web sources

منابع زیر در 2026-07-18 برای شکل‌دهی ساختار ساده و task-oriented بررسی شدند:

- Google Developer Documentation Style Guide — Procedures: `https://developers.google.com/style/procedures`
  - مبنای استفاده از مراحل شماره‌دار، کوتاه، action-first و انتخاب کوتاه‌ترین روش اصلی.
- Microsoft Style Guide — Writing step-by-step instructions: `https://learn.microsoft.com/en-us/style-guide/procedures-instructions/writing-step-by-step-instructions`
  - مبنای scan-friendly headings، یک action در هر step و بیان محل انجام کار قبل از action.
- Diátaxis — How-to guides: `https://diataxis.fr/how-to-guides/`
  - مبنای جداکردن مسیر goal-oriented از مرجع جزءبه‌جزء UI.

این منابع برای ادعای انطباق رسمی استفاده نشده‌اند؛ فقط best-practice guidance برای راهنمای شخصی بوده‌اند.

## گپ‌ها و `insufficient_evidence`

- browser accessibility certification همچنان `insufficient_evidence` است.
- real non-synthetic handoff evidence برای transitionهای ثبت‌شده همچنان خارج از محدوده این تغییر و `insufficient_evidence` است.
- این تغییر documentation-only است و هیچ evidence gap را نمی‌بندد.
- اجرای واقعی procedureهای راهنما روی سیستم مالک در این تغییر انجام نشده است.

## اقدام بعدی مجاز

1. review محتوای فارسی، commandها و لینک‌ها در pull request.
2. اجرای markdown/link check موجود repository توسط CI یا reviewer، در صورت وجود.
3. merge فقط با تصمیم صریح مالک پروژه.
