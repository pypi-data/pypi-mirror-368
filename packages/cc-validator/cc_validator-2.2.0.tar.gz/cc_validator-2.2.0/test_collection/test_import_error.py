from nonexistent_module import something

def test_should_fail():
    assert something() == 42