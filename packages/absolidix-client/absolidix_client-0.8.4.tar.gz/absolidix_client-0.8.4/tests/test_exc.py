"Test AbsolidixError"

from absolidix_client.exc import AbsolidixError


def test_error_string():
    "Test AbsolidixError"
    status = -1234
    message = "mEsSaGe"
    err = AbsolidixError(status=status, message=message)
    assert str(status) in str(err), "Status should be printed"
    assert str(message) in str(err), "Message should be printed"
