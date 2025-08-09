from aclib.builtins import Rect
from aclib.builtins import MatTarget

def test_rect():
    rect = Rect(0, 0, 10, 10)
    assert rect.left == 0
    assert rect.top == 0
    assert rect.right == 10
    assert rect.bottom == 10
    assert rect.width == 10
    assert rect.height == 10
    assert rect.size == (10, 10)
    assert rect.start == (0, 0)
    assert rect.end == (10, 10)
    assert rect.center == (5, 5)
    assert rect.border == (0, 0, 10, 10)
    assert rect.offset(1, 1).border == (1, 1, 11, 11)
    print('Rect tests passed')

test_rect()

def test_mat_target():
    target = MatTarget(0, 0, 10, 10, 'test', 0.5)
    print(target)

test_mat_target()