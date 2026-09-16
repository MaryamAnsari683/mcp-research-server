from demo_client import text_result


def test_text_result_extracts_text():
    class Item:
        text = "hello"

    class Result:
        content = [Item()]

    assert text_result(Result()) == "hello"
