import os.path
import uuid

import click
import pytest

from rasterio.rio.options import file_in_handler


class MockContext:

    def __init__(self):
        self.obj = {}


class MockOption:

    def __init__(self, name):
        self.name = name


def test_file_in_handler_no_vfs_nonexistent():
    """file does not exist"""
    ctx = MockContext()
    with pytest.raises(click.BadParameter):
        file_in_handler(ctx, 'INPUT', '{0}.tif'.format(uuid.uuid4()))


def test_file_in_handler_no_vfs():
    """file path is expanded to abspath"""
    ctx = MockContext()
    retval = file_in_handler(ctx, 'INPUT', 'tests/data/RGB.byte.tif')
    assert retval == os.path.abspath('tests/data/RGB.byte.tif')


def test_file_in_handler_bad_scheme():
    """lolwut scheme is not supported"""
    ctx = MockContext()
    with pytest.raises(click.BadParameter):
        _ = file_in_handler(ctx, 'INPUT', 'lolwut://bogus')


def test_file_in_handler_with_vfs_nonexistent():
    """archive does not exist"""
    ctx = MockContext()
    with pytest.raises(click.BadParameter):
        _ = file_in_handler(
            ctx, 'INPUT', 'zip://{0}/files.zip!/inputs/RGB.byte.tif'.format(uuid.uuid4()))


def test_file_in_handler_with_vfs():
    """vfs file path path is expanded"""
    ctx = MockContext()
    retval = file_in_handler(ctx, 'INPUT', 'zip://tests/data/files.zip!/inputs/RGB.byte.tif')
    assert retval.startswith('zip:///')
    assert retval.endswith('tests/data/files.zip!/inputs/RGB.byte.tif')


def test_file_in_handler_with_vfs_file():
    """vfs file path path is expanded"""
    ctx = MockContext()
    retval = file_in_handler(ctx, 'INPUT', 'file://tests/data/RGB.byte.tif')
    assert retval.endswith('tests/data/RGB.byte.tif')
