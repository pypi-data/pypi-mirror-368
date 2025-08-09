from rfnode.common.util import Util


def test_generate_array():
    arrs = Util.generate_array(1, 500, 10, 2)
    assert len(arrs) == 2  # two arrays since we have two devices connected to the node
