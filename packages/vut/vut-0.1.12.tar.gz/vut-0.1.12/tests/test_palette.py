from vut.palette import create_palette, template


def test_template():
    cmap = template(64, "plasma")
    assert cmap.N == 64


def test_create_palette():
    colors = [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
    cmap = create_palette(colors)
    assert cmap.N == 3
