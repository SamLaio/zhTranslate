from s2tw_converter import Converter


def test_yichu_is_not_a_global_classifier_replacement():
    converter = Converter()
    assert converter.convert('此言一出，消息一出，他一出门就一出手。') == '此言一出，消息一出，他一出門就一出手。'
    assert converter.convert('一出戏，两出戏。') == '一齣戲，兩齣戲。'
