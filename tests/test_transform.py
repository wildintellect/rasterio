import rasterio
from rasterio import transform
from affine import Affine


def test_window_transform():
    with rasterio.open('tests/data/RGB.byte.tif') as src:
        assert src.window_transform(((0, None), (0, None))) == src.affine
        assert src.window_transform(((None, None), (None, None))) == src.affine
        assert src.window_transform(
                ((1, None), (1, None))).c == src.bounds.left + src.res[0]
        assert src.window_transform(
                ((1, None), (1, None))).f == src.bounds.top - src.res[1]
        assert src.window_transform(
                ((-1, None), (-1, None))).c == src.bounds.left - src.res[0]
        assert src.window_transform(
                ((-1, None), (-1, None))).f == src.bounds.top + src.res[1]


def test_from_origin():
    with rasterio.open('tests/data/RGB.byte.tif') as src:
        w, n = src.ul(0, 0)
        xs, ys = src.res
        tr = transform.from_origin(w, n, xs, ys)
        assert [round(v, 7) for v in tr] == [round(v, 7) for v in src.affine]


def test_from_bounds():
    with rasterio.open('tests/data/RGB.byte.tif') as src:
        w, s, e, n = src.bounds
        tr = transform.from_bounds(w, s, e, n, src.width, src.height)
        assert [round(v, 7) for v in tr] == [round(v, 7) for v in src.affine]


def test_window_bounds():
    with rasterio.open('tests/data/RGB.byte.tif') as src:

        rows = src.height
        cols = src.width

        # Test window for entire DS and each window in the DS
        assert src.window_bounds(((0, rows), (0, cols))) == src.bounds
        for _, window in src.block_windows():
            ds_x_min, ds_y_min, ds_x_max, ds_y_max = src.bounds
            w_x_min, w_y_min, w_x_max, w_y_max = src.window_bounds(window)
            assert ds_x_min <= w_x_min <= w_x_max <= ds_x_max
            assert ds_y_min <= w_y_min <= w_y_max <= ds_y_max

        # Test a small window in each corner, both in and slightly out of bounds
        p = 10
        for window in (
                # In bounds (UL, UR, LL, LR)
                ((0, p), (0, p)),
                ((0, p), (cols - p, p)),
                ((rows - p, p), (0, p)),
                ((rows - p, p), (cols - p, p)),

                # Out of bounds (UL, UR, LL, LR)
                ((-1, p), (-1, p)),
                ((-1, p), (cols - p, p + 1)),
                ((rows - p, p + 1), (-1, p)),
                ((rows - p, p + 1), (cols - p, p + 1))):

            # Alternate formula

            ((row_min, row_max), (col_min, col_max)) = window
            win_aff = src.window_transform(window)

            x_min, y_max = win_aff.c, win_aff.f
            x_max = win_aff.c + (src.res[0] * (col_max - col_min))
            y_min = win_aff.f - (src.res[1] * (row_max - row_min))

            expected = (x_min, y_min, x_max, y_max)
            actual = src.window_bounds(window)

            for e, a in zip(expected, actual):
                assert round(e, 7) == round(a, 7)


def test_affine_roundtrip(tmpdir):

    def affine_roundtrip(aft):
        with rasterio.open('tests/data/RGB.byte.tif') as src:
            kwargs = {
                'crs': {'init': 'epsg:4326'},
                'affine': aft,
                'count': 3,
                'dtype': rasterio.uint8,
                'driver': 'GTiff',
                'width': src.shape[1],
                'height': src.shape[0],
                'nodata': 255
            }

            outfilename = str(tmpdir.join("rgb.tif"))
            with rasterio.open(outfilename, 'w', **kwargs) as out:
                assert out.affine == aft
                out.write(src.read())

            with rasterio.open(outfilename) as out_src:
                assert out_src.affine == aft

    affine_roundtrip(Affine(2, 0, 0, 0, -2, 0))
    affine_roundtrip(Affine(1, 0, 0, 0, -1, 0))
