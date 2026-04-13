# Install Guide Design

**Date:** 2026-04-13  
**Topic:** Non-technical end-user getting-started guide (Google Drive download + install + first launch)

---

## Goal

Replace the current minimal `INSTALLATION_INSTRUCTIONS.txt` with a clear, friendly guide that any non-technical user can follow. The guide covers downloading the ZIP from Google Drive, extracting it, installing the app, handling OS security warnings, and a quick first-launch walkthrough.

---

## Delivery

The guide lives as static pre-written files inside the repository. The packaging script copies the right platform folder into the delivery ZIP at package time — no generation at runtime.

```
docs/guides/
  macos/
    Getting_Started.txt
    Getting_Started.pdf
    Getting_Started.html
  windows/
    Getting_Started.txt
    Getting_Started.pdf
    Getting_Started.html
```

All three formats carry identical content. PDF is generated once with ReportLab (already a project dependency). HTML is self-contained with inline CSS.

---

## Guide Content Structure

Each guide is platform-specific (no combined Windows+Mac doc).

### What's in this folder
Short list of files the user received: the app, `license.json`, and this guide. One sentence on what `license.json` is ("your personal license — keep it next to the app").

### Step 1 — Download & extract
- Open the Google Drive link you received.
- Click the file name, then click the download icon (↓) in the top-right corner.
- macOS: double-click the downloaded ZIP to extract it.
- Windows: right-click the ZIP → Extract All → Extract.

### Step 2 — Place your files
- macOS: drag `PDF Batch Merger.app` to your Applications folder. Place `license.json` in the same Applications folder next to the app.
- Windows: move `PDF Batch Merger.exe` to any folder you like. Place `license.json` in the same folder as the `.exe`.

### Step 3 — Open the app
- macOS: right-click the app → Open.
  - **⚠️ Inline callout:** "You may see a message saying Apple cannot verify the developer. This is normal for software not sold through the App Store. Right-click the app, click Open, then click Open again in the dialog."
- Windows: double-click `PDF Batch Merger.exe`.
  - **⚠️ Inline callout:** "You may see a 'Windows protected your PC' message. This is normal for new software. Click More info, then click Run anyway."

### Step 4 — First launch
- A green checkmark at the top means your license is active and you're ready to go.
- Use the three Browse buttons to select: your input CSV/Excel file, the folder containing your PDFs, and the folder where merged files should be saved.
- Click Run Merge to start.

### Need help?
One line: "Contact [support placeholder] for license or technical issues."

---

## Changes to `create_client_package.py`

In `create_delivery_package()`:
- Remove the inline block that writes `INSTALLATION_INSTRUCTIONS.txt`.
- Add a block that copies all three files from `docs/guides/<platform>/` into the delivery directory.
- Keep the existing `User_Guide.md` copy (covers app usage, not installation).

---

## What Does Not Change

- The CI/CD workflow (`build-client-package.yml`) — no changes needed.
- `tools/license_generator.py` — no changes needed.
- `docs/README_USER.md` — still copied as `User_Guide.md`; it covers usage, not installation.
