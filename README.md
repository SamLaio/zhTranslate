# zhTranslate（s2tw-converter）

將簡體中文轉為臺灣正體中文的工具。支援直接轉換文字、單一文字檔與整個資料夾，也提供 Python API，供其他工具共用同一套詞彙與引號規則。

以 OpenCC `s2tw` 為基礎，再套用共用自訂詞庫。它處理純文字，不修改 Calibre DB，也不負責 EPUB 結構；EPUB 書籍請透過 epub223 的 `--convert-chinese s2tw` 使用。

目前版本：**0.1.9**。版本異動見 [CHANGELOG](CHANGELOG.md)。

## 安裝與快速開始

需要 Python 3.10 以上。在專案根目錄執行：

```powershell
python -m pip install -e .
s2tw-convert text '实时信息和“后面”'
```

從標準輸入讀取：

```powershell
Get-Content .\input.txt -Raw | s2tw-convert text
```

## 轉換單一檔案

```powershell
s2tw-convert file .\input.txt -o .\output.txt
```

**實際輸出為 `output_zyTw.txt`**。`-o` 是基礎路徑，程式會在副檔名前加入 `_zyTw`；原始 `input.txt` 保留。預設不覆蓋已存在的輸出，確定需要時加 `--overwrite`。

## 轉換資料夾

```powershell
s2tw-convert dir .\input-dir -o .\output-dir
s2tw-convert dir .\input-dir -o .\output-dir --extensions .txt,.md
```

預設處理 `.txt`、`.md`，保留子資料夾結構。例如 `input-dir\novel\book.txt` 對應 `output-dir\novel\book_zyTw.txt`。略過已帶 `_zyTw` 的檔案；輸出資料夾位於輸入內時也會排除，避免重複轉換。

想在來源資料夾旁產生轉換檔：

```powershell
s2tw-convert dir .\input-dir --in-place
```

`--in-place` 仍產生 `_zyTw` 新檔，不代表直接改寫原檔。`--overwrite` 控制是否覆蓋既有轉換輸出。

## 引號、自訂詞與編碼

預設將 `“”‘’` 改為 `「」『』`；要保留原引號，加 `--no-quote-convert`。

```powershell
s2tw-convert text '实时“信息”' --no-quote-convert
s2tw-convert text "实时" --replacements .\words.tsv
```

`--replacements` 可重複指定，也適用於 `file`、`dir`。TSV 每行為 `原詞<TAB>正體詞`，忽略空行及 `#` 註解。額外詞檔供當次轉換使用；共用詞庫維護方式見 [轉換規則與整合](docs/conversion.md)。

讀檔依序嘗試 UTF-8 BOM、UTF-8、UTF-16、CP950、Big5、GB18030。自動辨識仍可能有歧義，應檢查輸出是否亂碼。

## 限制與檢查

本工具不理解整份文件的語意。人名、古典用字與歧義詞需按出版原文核對；已確認正體文字不應只為統一流程而重轉。直接轉換 HTML／XML 會連路徑、識別字或程式內容一起處理，不能代替 EPUB 安全轉換。

CLI 會印出文字或實際輸出路徑；錯誤時檢查結束碼及 stderr。子指令後加 `--help` 可查看選項。

## 開發與授權

原始碼入口為 `python -m s2tw_converter.cli`。未安裝時先設定 `$env:PYTHONPATH="D:\github\zhTranslate\src"` 並安裝 `opencc-python-reimplemented`。

測試：`python -m pytest -q`。授權 GPL-3.0-or-later，見 [LICENSE](LICENSE)。

## 第三方來源與致謝

### 轉換引擎與字典

| 專案／作者 | 使用範圍 | 上游授權 |
| --- | --- | --- |
| [opencc-python-reimplemented／Yichen](https://github.com/yichen0831/opencc-python) | 實際呼叫的 Python OpenCC 實作 | Apache-2.0 |
| [OpenCC／BYVoid 與貢獻者](https://github.com/BYVoid/OpenCC) | `s2tw` 設定、簡繁字詞與臺灣字形字典；亦供明確簡體偵測使用 | Apache-2.0 |

本專案使用上述字典，不將其視為本專案原創詞庫；本專案 GPL-3.0-or-later 不取代其原授權。

### 自訂詞與設計來源

- [metaFinder](https://github.com/SamLaio/metaFinder) 與 [epub223](https://github.com/SamLaio/epub223)：匯入早期自訂替換詞，並將後續可共用修正集中於本專案。
- 本機歷史詞表 `kiwqtshoh.txt`：既有文件記錄曾保守匯入部分非重複詞條；目前未保存可核實的原作者、公開網址及原始授權，不能將它標成已確認的自製或自由授權來源。此來源資訊缺口仍待補證。
- [ezPub](https://github.com/SamLaio/ezPub)：文字編碼 fallback 與 CLI 設計參考，沒有匯入其簡轉正字典。

詞庫位置、套用順序與 API 見 [轉換規則](docs/conversion.md)。新增外部詞表時須同時保存作者、來源網址與授權；不能只記本機檔名。
