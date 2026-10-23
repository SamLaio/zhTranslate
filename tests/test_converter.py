from __future__ import annotations

from pathlib import Path

import pytest

from s2tw_converter.converter import Converter, convert_directory, convert_file, read_text_with_fallback
from s2tw_converter import simplified_pattern


def test_shenme_before_erzi_does_not_leave_simplified_me():
    converter = Converter()
    for text in ('什么儿子', '什么兒子', '什麼兒子', '你要什么兒子？'):
        expected = '你要什麼兒子？' if text.startswith('你') else '什麼兒子'
        assert converter.convert(text) == expected
        assert converter.convert(expected) == expected
    # 保留獨立的么兒詞條，不新增無上下文的么單字替換。
    assert converter.convert('么兒') == '么兒'


def test_dictionary_detection_covers_short_names_and_preserves_valid_traditional():
    pattern = simplified_pattern()
    for text in ("军代表吴峥嵘", "张陈", "药", "项桓", "顾虑", "视线", "归宿", "怎么", "什么", "糙漢将軍"):
        assert pattern.search(text), text
    for text in ("帶回伙伴，祕密。霉女喜嫁", "皇后于此干涉台灣", "病灶，雇用，佳肴，瀟洒，幺么", "机の上。鹿島研究所出版会", "狎昵感，晾晒，庄司博士"):
        assert not pattern.search(text), text
    assert simplified_pattern(True).search("中国")


def test_na_before_yaoezi_does_not_cross_word_boundary():
    converter = Converter()
    for text in ('讓那么蛾子都滅了', '那些么蛾子', '那幺蛾子', '整這麼多么蛾子', '吃個飯都能鬧出這麼多么蛾子'):
        converted = converter.convert(text)
        assert not simplified_pattern().search(converted)
        assert converter.convert(converted) == converted
    for text in ('那么好', '那么蛾', '什么蛾子', '那么蛾子与他', '多么好', '多么蛾', '多么蛾子与他'):
        assert simplified_pattern().search(text), text


def test_valid_traditional_religious_medical_and_classical_glyphs():
    pattern = simplified_pattern()
    for text in ("祢是神，水疱與疱疹", "恒卦與恒河，苯并唑，虱子", "青葱與葱花"):
        assert not pattern.search(text), text
    for text in ("内疱疹", "恒卦与神", "政治肥皂剧", "卓别林"):
        assert pattern.search(text), text


def test_verified_yang_shuangfu_name_preserves_its_published_glyph():
    converter = Converter()
    for text in ('楊双福', '楊雙福', '杨双福'):
        assert converter.convert(text) == '楊双福'
    assert not simplified_pattern().search('用文字起飛—楊双福')
    for text in ('双福', '楊双喜', '杨双福', '楊双福与他', '双双'):
        assert simplified_pattern().search(text), text


def test_verified_lin_faner_name_does_not_allow_general_simplified_er():
    converter = Converter()
    for text in ('林凡儿', '林凡兒'):
        assert converter.convert(text) == '林凡儿'
        assert not simplified_pattern().search(text)
    for text in ('凡儿', '林儿', '儿子', '林凡儿与他'):
        assert simplified_pattern().search(text), text


def test_verified_lin_yuti_name_keeps_other_simplified_characters_detectable():
    converter = Converter()
    for text in ('林玉体', '林玉體'):
        assert converter.convert(text) == '林玉体'
        assert not simplified_pattern().search('教育史學者' + converter.convert(text))
        assert converter.convert(converter.convert(text)) == '林玉体'
    for text in ('玉体', '林体', '身体', '林玉体与他'):
        assert simplified_pattern().search(text), text
    assert converter.convert('林玉体与身体') == '林玉体與身體'


def test_hou_uses_context_and_keeps_translator_name():
    converter = Converter()
    converted = converter.convert("皇后 太后 后羿 后土 后稷 后来 后面 皇後 呂郁青")
    assert converted == "皇后 太后 后羿 后土 后稷 後來 後面 皇后 呂郁青"
    assert converter.convert(converted) == converted
    assert converter.convert('林郁芬 林鬱芬 憂鬱') == '林郁芬 林郁芬 憂鬱'


def test_character_rules_run_before_phrase_exceptions(tmp_path: Path) -> None:
    replacements = tmp_path / "custom.tsv"
    replacements.write_text("AB\tAC\nZ\tB\n", encoding="utf-8")
    converter = Converter((replacements,))
    assert converter._apply_replacements("AZ") == "AC"
    assert converter._apply_replacements("太后 后") == "太后 後"


def test_convert_text_uses_opencc_replacements_and_quotes() -> None:
    converted = Converter().convert("实时信息和“后面”")
    assert converted == "即時資訊和「後面」"


def test_duiyu_uses_standard_traditional_form() -> None:
    assert Converter().convert("对于山神庙的事情") == "對於山神廟的事情"


def test_guanxi_uses_standard_traditional_form() -> None:
    converter = Converter()
    assert converter.convert("母女关系") == "母女關係"
    assert converter.convert("母女關系與親屬關繫") == "母女關係與親屬關係"


def test_demonstrative_kind_does_not_join_following_historical_name():
    converter=Converter()
    for text in ('這种放棄所有倫理','这种放弃所有伦理','這种放縱','这种放纵'):
        assert converter.convert(text).startswith('這種放')
    assert converter.convert('這种放棄所有倫理')=='這種放棄所有倫理'
    assert converter.convert('這種放棄所有倫理')=='這種放棄所有倫理'
    # 不加「种→種」全域規則；獨立人名仍交給原來的OpenCC詞典。
    assert converter.convert('种放先生')==converter._converter.convert('种放先生')


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


def test_author_xiangsuli_preserves_official_pen_name() -> None:
    converter=Converter()
    text=converter.convert("香酥栗 香酥慄 战栗")
    assert text=="香酥栗 香酥栗 戰慄"
    assert converter.convert(text)==text


def test_verified_author_and_translator_names_keep_official_characters():
    converter = Converter()
    for name, expected in (("郁保林", "郁保林"), ("鬱保林", "郁保林"),
                           ("朴容基", "朴容基"), ("樸容基", "朴容基"),
                           ("游紫晴", "游紫晴"), ("遊紫晴", "游紫晴")):
        assert converter.convert(name) == expected
        assert converter.convert(expected) == expected
    assert converter.convert("憂鬱 純樸 遊戲") == "憂鬱 純樸 遊戲"
    assert converter.convert("G．約翰．伊肯伯里 G．約翰．伊肯伯裡") == "G．約翰．伊肯伯里 G．約翰．伊肯伯里"


def test_translator_name_lin_yuting_keeps_official_character() -> None:
    converted = Converter().convert("譯者林于楟")
    assert converted == "譯者林于楟"


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


def test_translator_tu_yucheng_preserves_official_name():
    converter = Converter()
    for name in ("涂育诚", "涂育誠", "塗育誠"):
        assert converter.convert(name) == "涂育誠"
    assert converter.convert("塗料") == "塗料"


def test_verified_japanese_author_keeps_official_complete_name():
    converter = Converter()
    assert converter.convert("理不盡な孫の手 尽力") == "理不尽な孫の手 盡力"
    assert converter.convert("理不尽な孫の手") == "理不尽な孫の手"
    assert not simplified_pattern().search("理不尽な孫の手")
    for text in ("尽力", "理不尽", "尽な孫の手", "理不尽な孫の手 写作"):
        assert simplified_pattern().search(text), text


def test_then_royal_son_preserves_phrase_boundary():
    converter = Converter()
    for text in ("那么儿臣可以告退了？", "那么兒臣可以告退了？", "那麼兒臣可以告退了？"):
        result = converter.convert(text)
        assert result == "那麼兒臣可以告退了？"
        assert converter.convert(result) == result
    assert converter.convert("么兒、那些么蛾子") == "么兒、那些么蛾子"


def test_so_childish_preserves_phrase_boundary():
    converter = Converter()
    for text in ("婚事豈能那么儿戏？", "婚事豈能那么兒戲？", "婚事豈能那麼兒戲？"):
        result = converter.convert(text)
        assert result == "婚事豈能那麼兒戲？"
        assert converter.convert(result) == result
    assert converter.convert("么兒、那些么蛾子") == "么兒、那些么蛾子"


def test_do_something_phrase_does_not_become_dry_food():
    converter = Converter()
    for text in ("该干点什么呢？", "該乾點什麼呢？", "該干點什麼呢？", "該幹點什麼呢？"):
        result = converter.convert(text)
        assert result == "該幹點什麼呢？"
        assert converter.convert(result) == result
    assert converter.convert("干点心和干燥剂") == "乾點心和乾燥劑"
    assert converter.convert("乾點心和乾燥劑") == "乾點心和乾燥劑"


def test_convert_directory_skips_existing_zytw_outputs(tmp_path: Path) -> None:
    source_root = tmp_path / "src"
    source_root.mkdir()
    (source_root / "book.txt").write_text("实时信息", encoding="utf-8")
    (source_root / "book_zyTw.txt").write_text("即時資訊", encoding="utf-8")

    converted = convert_directory(source_root, in_place=True)

    assert converted == [source_root / "book_zyTw.txt"]
    assert not (source_root / "book_zyTw_zyTw.txt").exists()
