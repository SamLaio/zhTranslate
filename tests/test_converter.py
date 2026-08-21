from __future__ import annotations

from pathlib import Path

import pytest

from s2tw_converter.converter import Converter, convert_directory, convert_file, read_text_with_fallback


def test_convert_text_uses_opencc_replacements_and_quotes() -> None:
    converted = Converter().convert("实时信息和“后面”")
    assert converted == "即時資訊和「後面」"


def test_imported_replacements_from_epub223_and_metafinder() -> None:
    converted = Converter().convert("谷城县的信息安全和计程车兵")
    assert converted == "穀城縣的資訊安全和士兵"


def test_single_character_chu_does_not_break_publishing_terms() -> None:
    converted = Converter().convert("出版社 出版公司 出版日期 联经出版公司 一出好戏")
    assert converted == "出版社 出版公司 出版日期 聯經出版公司 一齣好戲"


def test_imported_replacements_from_kiwqtshoh() -> None:
    converted = Converter().convert("中文繫裏麪髮展，后期并不輕松")
    assert converted == "中文系裡面發展，後期並不輕鬆"


def test_otaku_terms_use_standard_taiwan_wording() -> None:
    converted = Converter().convert("禦宅族與禦宅文化")
    assert converted == "御宅族與御宅文化"


def test_series_after_comma_stays_standard_taiwan_wording() -> None:
    converted = Converter().convert("短篇小說集，系列中關於神靈")
    assert converted == "短篇小說集，系列中關於神靈"


def test_translator_name_zhou_peiyu_keeps_official_character() -> None:
    converted = Converter().convert("譯者周沛郁")
    assert converted == "譯者周沛郁"


def test_custom_replacements_apply_before_and_after_opencc(tmp_path: Path) -> None:
    replacements = tmp_path / "custom.tsv"
    replacements.write_text("测试词\t測試詞\n轉換後\t修正後\n", encoding="utf-8")
    converted = Converter((replacements,)).convert("测试词與转换后")
    assert converted == "測試詞與修正後"


def test_opencc_conversion_errors_are_not_silenced() -> None:
    converter = Converter()

    class BrokenOpenCC:
        def convert(self, text: str) -> str:
            raise RuntimeError("boom")

    converter._converter = BrokenOpenCC()

    with pytest.raises(RuntimeError, match="boom"):
        converter.convert("实时信息")


def test_read_text_with_gb18030_fallback(tmp_path: Path) -> None:
    source = tmp_path / "gb.txt"
    source.write_bytes("实时信息".encode("gb18030"))
    assert read_text_with_fallback(source) == "实时信息"


def test_read_text_prefers_cp950_before_gb18030(tmp_path: Path) -> None:
    source = tmp_path / "big5.txt"
    source.write_bytes("《擇日走紅》作者：宋不留春".encode("cp950"))
    assert read_text_with_fallback(source) == "《擇日走紅》作者：宋不留春"


def test_read_text_accepts_mostly_cp950_with_few_bad_bytes(tmp_path: Path) -> None:
    source = tmp_path / "mostly-big5.txt"
    source.write_bytes("《擇日走紅》作者：宋不留春".encode("cp950") + b"\x99")
    assert read_text_with_fallback(source).startswith("《擇日走紅》作者：宋不留春")


def test_convert_file_writes_utf8(tmp_path: Path) -> None:
    source = tmp_path / "input.txt"
    target = tmp_path / "output.txt"
    output = tmp_path / "output_zyTw.txt"
    source.write_text("实时信息", encoding="utf-8")
    assert convert_file(source, target) == output
    assert output.read_text(encoding="utf-8") == "即時資訊"


def test_convert_file_refuses_to_overwrite_by_default(tmp_path: Path) -> None:
    source = tmp_path / "input.txt"
    target = tmp_path / "output_zyTw.txt"
    source.write_text("实时信息", encoding="utf-8")
    target.write_text("舊內容", encoding="utf-8")
    with pytest.raises(FileExistsError):
        convert_file(source, tmp_path / "output.txt")


def test_convert_directory_preserves_relative_paths(tmp_path: Path) -> None:
    source_root = tmp_path / "src"
    output_root = tmp_path / "out"
    nested = source_root / "nested"
    nested.mkdir(parents=True)
    (nested / "book.txt").write_text("实时信息", encoding="utf-8")
    (nested / "skip.html").write_text("实时信息", encoding="utf-8")

    converted = convert_directory(source_root, output_root)

    assert converted == [output_root / "nested" / "book_zyTw.txt"]
    assert (output_root / "nested" / "book_zyTw.txt").read_text(encoding="utf-8") == "即時資訊"
    assert not (output_root / "nested" / "skip.html").exists()


def test_convert_directory_ignores_output_dir_inside_input(tmp_path: Path) -> None:
    source_root = tmp_path / "src"
    output_root = source_root / "out"
    output_root.mkdir(parents=True)
    (source_root / "book.txt").write_text("实时信息", encoding="utf-8")
    (output_root / "old.txt").write_text("实时信息", encoding="utf-8")

    converted = convert_directory(source_root, output_root, overwrite=True)

    assert converted == [output_root / "book_zyTw.txt"]
    assert (output_root / "book_zyTw.txt").read_text(encoding="utf-8") == "即時資訊"
    assert not (output_root / "old_zyTw.txt").exists()


def test_convert_directory_skips_existing_zytw_outputs(tmp_path: Path) -> None:
    source_root = tmp_path / "src"
    source_root.mkdir()
    (source_root / "book.txt").write_text("实时信息", encoding="utf-8")
    (source_root / "book_zyTw.txt").write_text("即時資訊", encoding="utf-8")

    converted = convert_directory(source_root, in_place=True)

    assert converted == [source_root / "book_zyTw.txt"]
    assert not (source_root / "book_zyTw_zyTw.txt").exists()
