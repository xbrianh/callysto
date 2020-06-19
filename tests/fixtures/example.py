import os
import sys

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from callysto import Callysto


with Callysto("markdown"):
    """
    # This is a header
    doom and gloom
    
    ## frank is a ganster
    evidence
    """

with Callysto("python"):
    import os
    print("blaksdjf")
    foo = 3
    doom = "frank"
    comp = dict(c=dict(a="b"))

with Callysto("python", is_cell=False):
    assert foo == 3
    doom = "gloom"
    comp["c"]["a"] = 4

with Callysto("python"):
    foo += 21
    print(os.path)
    print(doom)
    print(comp)
