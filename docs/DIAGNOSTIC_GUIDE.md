# Diagnostic Guide

این سند راهنمای کوتاه diagnosticهای پنل محلی Project Gate است.

## هدف

لایه guidance فقط معنی انسانی و اقدام بعدی را اضافه می‌کند. این لایه منطق transition، schema، validator یا status را تغییر نمی‌دهد.

## گروه‌ها

- Input JSON
- Transition selection
- Local repository paths
- Pinned external files
- External lock/hash verification
- Architect source identity
- Architect schema validation
- Architect semantic validation
- CE schema validation
- CE validator
- Output bundle validation
- UI/report rendering
- Unknown

## پرسش‌های اجباری برای failure

وقتی run متوقف می‌شود، visible summary باید جواب دهد:

```text
کجا متوقف شد؟
چه چیزی قبل از آن درست پیش رفت؟
مشکل فعلی چیست؟
اقدام بعدی دقیق چیست؟
آیا خروجی مرحله بعد ساخته شد؟
```

## Guidance coverage

رجیستری `src/ev4_transition/data/operator-guidance.v1.json` باید حداقل برای diagnosticهای زیر mapping داشته باشد:

```text
PG.SERVICE.REPO_PATH_MISSING
PG.SERVICE.LOCAL_FILE_ACCESS_FAILED
PG_A2C_EXTERNAL_FILE_READ_FAILED
PG_A2C_EXTERNAL_HASH_MISMATCH
PG_A2C_ARCHITECT_SCHEMA_VALIDATION_FAILED
PG_A2C_CE_SCHEMA_VALIDATION_FAILED
PG_A2C_SOURCE_SCHEMA_ID_MISMATCH
PG_A2C_WRONG_SOURCE_STAGE
PG.UI.UNHANDLED_EXCEPTION
PG.UI.REPORT_WRITE_FAILED
```

این coverage با regression test بررسی می‌شود.

## Raw diagnostics

`result.json` و جدول raw diagnostics منبع فنی باقی می‌مانند. guidance فقط خلاصه عملیاتی فارسی بالای آن‌هاست.

Raw diagnostics نباید حذف یا silently normalized شود. در reportها raw diagnostics و raw JSON result باید در LTR code block نمایش داده شوند.

## Traceback exposure

traceback خام نباید در visible summary نمایش داده شود. اگر runtime failure رخ دهد، UI باید diagnostic کنترل‌شده مثل `PG.UI.UNHANDLED_EXCEPTION` بسازد و متن فارسی امن نشان دهد.

## Repair prompt

Repair prompt فقط برای diagnosticهای شناخته‌شده و repairable تولید می‌شود. Project Gate خودش JSON را اصلاح نمی‌کند، evidence نمی‌سازد و specialist logic را پیاده‌سازی نمی‌کند.
