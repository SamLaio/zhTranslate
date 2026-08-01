# s2tw-converter

`s2tw-converter` 是目前專案內獨立的簡體中文轉臺灣正體中文工具。

它參考了：

- `D:\project\metaFinder`：`OpenCC("s2tw")`、自訂詞在 OpenCC 前後各套用一次。
- `D:\project\epub223`：西式彎引號轉臺灣直角引號、避免把 EPUB 專用安全規則混入一般文字工具。
- `D:\github\ezPub`：檔案讀取時支援常見中文編碼 fallback，並保持 CLI 工具可獨立使用。
- `D:\Downloads\kiwqtshoh.txt`：OpenCC 後修正候選，已保守匯入目前不存在且非 identity 的詞條。

## 功能

- 使用 `opencc-python-reimplemented` 的 `OpenCC("s2tw")`。
- 內建 `custom_replacements.tsv`，可修正 OpenCC 後仍常見的詞彙偏差。
- 內建字典已匯入 `D:\project\epub223`、`D:\project\metaFinder` 與 `D:\Downloads\kiwqtshoh.txt` 的可泛用詞彙。
- OpenCC 的 `STCharacters.txt`、`STPhrases.txt` 不直接匯入，避免重複與衝突。
- 自訂替換會在 OpenCC 轉換前、轉換後各套用一次。
- 預設將 `“”‘’` 轉成 `「」『』`。
- 可轉換單段文字、單一檔案、整個資料夾。
- 輸出檔名會自動在副檔名前加上 `_zyTw`，例如 `book.txt` 會輸出成 `book_zyTw.txt`。
- 讀檔支援 `utf-8-sig`、`utf-8`、`utf-16`、`gb18030`、`big5` fallback。

## 安裝

在本資料夾執行：

```powershell
pip install -e .
```

若只要直接以原始碼執行：

```powershell
$env:PYTHONPATH="D:\github\zhTranslate\src"
python -m s2tw_converter.cli text '实时信息和“后面”'
```

## 使用方式

轉換文字：

```powershell
s2tw-convert text '实时信息和“后面”'
```

從 stdin 讀取：

```powershell
Get-Content .\input.txt -Raw | s2tw-convert text
```

轉換單一檔案：

```powershell
s2tw-convert file .\input.txt -o .\output.txt
```

實際輸出為 `.\output_zyTw.txt`。

覆蓋輸出檔：

```powershell
s2tw-convert file .\input.txt -o .\output.txt --overwrite
```

轉換資料夾，保留相對路徑：

```powershell
s2tw-convert dir .\input-dir -o .\output-dir
```

資料夾內每個轉換檔都會加上 `_zyTw`，例如 `.\input-dir\novel\book.txt` 會輸出到 `.\output-dir\novel\book_zyTw.txt`。若輸出資料夾位於輸入資料夾內，轉換時會略過該輸出資料夾；批次轉換也會略過檔名已經以 `_zyTw` 結尾的檔案，避免重複處理已產生的輸出檔。

在原資料夾內輸出 `_zyTw` 檔案：

```powershell
s2tw-convert dir .\input-dir --in-place --overwrite
```

指定副檔名：

```powershell
s2tw-convert dir .\input-dir -o .\output-dir --extensions .txt,.md
```

使用額外自訂替換檔：

```powershell
s2tw-convert text "实时" --replacements .\my_replacements.tsv
```

自訂替換檔格式：

```text
原詞<TAB>正體詞
```

空行與 `#` 開頭註解會被忽略。

## 字典來源

目前主字典位於：

```text
D:\github\zhTranslate\src\s2tw_converter\custom_replacements.tsv
```

已整理匯入的來源：

- `D:\project\epub223\epub3itizer\custom_replacements.tsv`
- `D:\project\metaFinder\src\metafinder\custom_replacements.tsv`

這兩份來源字典目前內容一致，共 302 筆；`zhTranslate` 會移除已知過度泛化詞條，例如無上下文的 `出 -> 齣`，避免「出版」被誤轉成「齣版」。

`D:\github\ezPub` 目前沒有發現可匯入的簡轉正自訂字典；它只作為中文文字檔編碼 fallback 與 CLI 設計參考。

## 與書庫整理流程整合

建議把 `zhTranslate` 放在共用文字轉換層：

- `metaFinder`：metadata 候選輸出前使用 `zhTranslate` 做正體化與自訂詞修正。
- `epub223`：保留 `--convert-chinese s2tw` 選用行為，但內部文字轉換可改為呼叫 `zhTranslate`，EPUB 結構安全仍由 `epub223` 負責。
- `ezPub`：預設不自動轉換 TXT 內容；未來若新增明確的簡轉正參數，再呼叫 `zhTranslate`。
- `CalibreAbout` 書庫整理流程：人工寫入 metadata、comments、tags、OPF metadata 前，若資料為簡體，優先使用 `zhTranslate`；新詞彙修正沉澱回本專案。

## 注意事項

- 本工具是純文字層工具，不會修改 Calibre DB。
- 本工具不直接處理 EPUB ZIP/package 結構。
- EPUB 內 XHTML、OPF、NCX 等檔案若要安全轉換，仍應由 `D:\project\epub223` 處理，因為 EPUB 需要避開 `href`、`src`、`id`、CSS、URL、script/style 等欄位。
- 如果將本工具直接套到 HTML/XML 檔，會做全文字串轉換，可能改到路徑或識別字；這類用途要先確認安全性。

## 測試

```powershell
python -m pytest -q
```

## 授權

本專案使用 GPL-3.0-or-later 授權，詳見 `LICENSE`。

## 維護原則

- 新增泛用詞彙修正時，先補 `custom_replacements.tsv`。
- 不再把簡轉正自訂詞分散維護在 `metaFinder` 或 `epub223`；需要共用的詞彙先進本專案，再由其他工具引用。
- 每次改轉換邏輯，要補或更新測試。
- 行為改變時要更新 `README.md` 與 `CHANGELOG.md`。
- 人類可讀文件與 log 一律使用正體中文。
