# s2tw-converter Agent Rules

本檔是 `s2tw-converter` 的 agent / Codex 專案慣例檔。修改程式、文件、測試或發版前，先依照這裡的規則檢查。

## 專案定位

- 本專案是獨立的簡體中文轉臺灣正體中文工具。
- 本專案只處理文字、單一檔案與一般資料夾批次。
- 本專案不修改 Calibre DB、不直接處理 EPUB ZIP/package、不取代 `D:\project\epub223` 的 EPUB 安全轉換流程。
- EPUB 內 XHTML、OPF、NCX、XML 的安全轉換仍交由 `D:\project\epub223`，避免誤改 `href`、`src`、`id`、CSS、URL 或 script/style。
- 本專案授權為 GPL-3.0-or-later；修改授權相關資訊時需同步 `LICENSE`、`README.md` 與 `pyproject.toml`。

## 參考來源

- `D:\project\metaFinder`
  - 參考 `OpenCC("s2tw")`。
  - 參考自訂替換在 OpenCC 轉換前後各套用一次的做法。
  - 參考以 pytest 驗證簡轉正與自訂詞。
  - 既有 `custom_replacements.tsv` 已匯入本專案主字典。
- `D:\project\epub223`
  - 參考西式彎引號轉臺灣直角引號。
  - 參考將可泛用規則沉澱成測試與 change log 的做法。
  - 注意：只參考文字轉換思路，不搬移 EPUB package 修復規則。
  - 既有 `custom_replacements.tsv` 已匯入本專案主字典。
- `D:\github\ezPub`
  - 參考中文文字檔常見編碼 fallback。
  - 參考 CLI 文件與測試素材分離的維護方式。
  - 目前沒有發現可匯入的簡轉正自訂字典。

## 核心功能

- 使用 `opencc-python-reimplemented` 的 `OpenCC("s2tw")`。
- 透過 `custom_replacements.tsv` 套用專案自訂詞覆寫。
- 主字典集中收納 `metaFinder`、`epub223`、書庫整理流程與未來 `ezPub` 可能需要共用的簡轉正詞彙。
- 自訂替換必須在 OpenCC 轉換前與轉換後各套用一次。
- 預設將西式彎引號 `“”‘’` 轉成臺灣直角引號 `「」『』`。
- CLI 必須支援：
  - 直接轉換文字。
  - 轉換單一檔案。
  - 轉換資料夾並保留相對路徑。

## 文件語言

- 所有人類可讀文件、README、CHANGELOG、測試說明與 log 一律使用正體中文。
- CLI help 可使用英文參數名稱，但說明文字優先使用正體中文。

## 可泛用規則沉澱

當 Calibre 書庫整理、EPUB 轉換或 metadata 查找流程中發現新的簡轉正詞彙偏差時：

1. 若是泛用詞彙修正，優先加入本專案 `src/s2tw_converter/custom_replacements.tsv`。
2. 補最小可行 regression test。
3. 更新 `README.md` 或相關使用說明。
4. 更新 `CHANGELOG.md`，使用正體中文。
5. 執行 `python -m pytest -q`。

只有明確是單本書特有、需要人工內容判斷、或不安全批次套用時，才不要寫入本專案。

## 驗證方式

- 修改 Python 實作後，執行：

```powershell
python -m pytest -q
```

- 修改 CLI 行為後，也要至少手動跑一次：

```powershell
python -m s2tw_converter.cli text "实时信息和“后面”"
```

## 文件一致性

- `README.md` 要和實際 CLI 行為一致。
- 行為變動時，先更新 README 與 CHANGELOG，再視情況提交。
- 不要把本工具寫成 EPUB 專用工具；EPUB 結構安全仍屬於 `epub223`。

## Git Ignore 規則

以下內容不得提交：

- `__pycache__/`
- `*.py[cod]`
- `.pytest_cache/`
- `.mypy_cache/`
- `.ruff_cache/`
- `.venv/`
- `venv/`
- `dist/`
- `build/`
- `*.egg-info/`
- `*.log`

## 已知重點

- 本工具是共用文字轉換層，應保持小而穩定。
- `metaFinder` 與 `epub223` 未來應優先引用本工具的文字轉換能力，不再各自維護分散字典。
- 不要在本工具中加入 Calibre、metadata 查找、EPUBCheck 或 EPUB package 修復相依。
- 若未來要處理 EPUB，應由 `epub223` 呼叫本工具的文字轉換能力，而不是讓本工具理解 EPUB。
