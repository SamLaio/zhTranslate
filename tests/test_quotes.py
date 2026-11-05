import pytest
from s2tw_converter import Converter, normalize_quotes


@pytest.mark.parametrize(('source', 'expected'), [
    ('“？”\n“……”\n“是。”', '「？」\n「……」\n「是。」'),
    ('他说："你好。"', '他說：「你好。」'),
    ("她說：'好。'", '她說：『好。』'),
    ('"她说：\'你好\'。"', '「她說：『你好』。」'),
    ('"？"\n"……"', '「？」\n「……」'),
])
def test_dialogue_quotes_and_idempotence(source, expected):
    result = Converter().convert(source)
    assert result == expected
    assert Converter().convert(result) == result


@pytest.mark.parametrize('source', [
    "I'm fine. Don't change John's book.",
    'I’m fine. John’s book.',
    'He said "hello"; 5\' 10"; 12" screen.',
    '{"標題":"中文"}',
    '<p title="中文">正文</p>',
    'print("中文") # 程式範例',
    '變數 = "中文"',
    '使用 `"中文"` 作為範例。',
    '保留 " " 與空字串 ""。',
    '她說："沒有結束',
])
def test_non_dialogue_ascii_quotes_are_preserved(source):
    assert normalize_quotes(source) == source


def test_quote_only_api_and_disabled_conversion():
    source = '皇后帶回祕密：“？”'
    assert normalize_quotes(source) == '皇后帶回祕密：「？」'
    assert Converter(convert_quotes=False).convert('他说："你好“？”"') == '他說："你好“？”"'
