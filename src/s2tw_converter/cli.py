from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .converter import DEFAULT_EXTENSIONS, Converter, convert_directory, convert_file

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


def _replacement_paths(values: list[str] | None) -> tuple[Path, ...]:
    return tuple(Path(value) for value in values or ())


def _extensions(value: str | None) -> tuple[str, ...]:
    if not value:
        return DEFAULT_EXTENSIONS
    return tuple(part.strip() for part in value.split(",") if part.strip())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="s2tw-convert", description="簡體中文轉臺灣正體中文工具")
    sub = parser.add_subparsers(dest="command", required=True)

    text = sub.add_parser("text", help="轉換命令列文字；未提供文字時讀取 stdin")
    text.add_argument("text", nargs="*", help="要轉換的文字")
    text.add_argument("--replacements", action="append", help="額外自訂替換 TSV，可重複指定")
    text.add_argument("--no-quote-convert", action="store_true", help="不要把西式彎引號轉成直角引號")

    file_cmd = sub.add_parser("file", help="轉換單一檔案")
    file_cmd.add_argument("input", help="輸入檔")
    file_cmd.add_argument("-o", "--output", required=True, help="輸出檔基礎路徑，實際檔名會加 _zyTw")
    file_cmd.add_argument("--overwrite", action="store_true", help="允許覆蓋輸出檔")
    file_cmd.add_argument("--replacements", action="append", help="額外自訂替換 TSV，可重複指定")
    file_cmd.add_argument("--no-quote-convert", action="store_true", help="不要把西式彎引號轉成直角引號")

    dir_cmd = sub.add_parser("dir", help="轉換資料夾")
    dir_cmd.add_argument("input", help="輸入資料夾")
    dir_cmd.add_argument("-o", "--output", help="輸出資料夾；非 --in-place 時必填")
    dir_cmd.add_argument("--in-place", action="store_true", help="在原資料夾內輸出 _zyTw 檔案")
    dir_cmd.add_argument("--overwrite", action="store_true", help="允許覆蓋輸出檔")
    dir_cmd.add_argument("--extensions", help="逗號分隔副檔名，預設 .txt,.md")
    dir_cmd.add_argument("--replacements", action="append", help="額外自訂替換 TSV，可重複指定")
    dir_cmd.add_argument("--no-quote-convert", action="store_true", help="不要把西式彎引號轉成直角引號")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    replacements = _replacement_paths(getattr(args, "replacements", None))
    convert_quotes = not getattr(args, "no_quote_convert", False)

    if args.command == "text":
        source = " ".join(args.text) if args.text else sys.stdin.read()
        converted = Converter(replacements, convert_quotes=convert_quotes).convert(source) or ""
        print(converted, end="" if converted.endswith("\n") else "\n")
        return 0

    if args.command == "file":
        output = convert_file(
            args.input,
            args.output,
            replacement_paths=replacements,
            convert_quotes=convert_quotes,
            overwrite=args.overwrite,
        )
        print(output)
        return 0

    if args.command == "dir":
        output = convert_directory(
            args.input,
            args.output,
            replacement_paths=replacements,
            convert_quotes=convert_quotes,
            extensions=_extensions(args.extensions),
            in_place=args.in_place,
            overwrite=args.overwrite,
        )
        for path in output:
            print(path)
        return 0

    raise AssertionError(f"未知命令：{args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
