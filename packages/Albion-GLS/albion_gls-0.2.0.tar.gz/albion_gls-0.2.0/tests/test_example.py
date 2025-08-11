import Albion_GLS

def test_hello(capsys):
    Albion_GLS.hello()
    captured = capsys.readouterr()
    assert "Hello from Albion_GLS" in captured.out