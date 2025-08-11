import time
from codewright import timer, retry, cache


def test_timer(capsys):
    @timer
    def short_task():
        return "complete"

    assert short_task() == "complete"
    captured = capsys.readouterr()
    assert "Finished 'short_task'" in captured.out


def test_retry(capsys):
    fail_count = 0

    @retry(tries=3, delay=0.01)
    def fails_twice():
        nonlocal fail_count
        fail_count += 1
        if fail_count < 3:
            raise ValueError("Failed")
        return "succeeded"

    assert fails_twice() == "succeeded"
    assert fail_count == 3
    captured = capsys.readouterr()
    assert captured.out.count("Retrying in") == 2


def test_cache():
    call_count = 0

    @cache
    def expensive_func(x, y):
        nonlocal call_count
        call_count += 1
        return x + y

    assert expensive_func(1, 2) == 3
    assert call_count == 1
    # Call again with same args, count should not increase
    assert expensive_func(1, 2) == 3
    assert call_count == 1
    # Call with different args, count should increase
    assert expensive_func(2, 3) == 5
    assert call_count == 2
