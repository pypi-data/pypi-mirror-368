import os
import pathlib
import re
from dataclasses import fields

import pytest

from .. import ESRFPath
from ..schemas._esrf_v1 import ESRFv1Schema
from ..schemas._esrf_v2 import ESRFv2Schema
from ..schemas._esrf_v3 import ESRFv3Schema
from .utils import make_path
from .utils import safe_repr

NOT_ESRF_PATH = make_path("some", "other", "path", "that", "does", "not", "match")

TEST_PATHS = {
    make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "RAW_DATA",
        "foo",
        "foo_bar",
        "foo_bar.h5",
    ): ESRFv3Schema(
        data_root=make_path("visitor"),
        proposal="ma6658",
        beamline="id21",
        session_date="20250509",
        data_type="RAW_DATA",
        collection="foo",
        dataset="bar",
    ),
    make_path(
        "visitor", "ma6658", "id21", "20250509", "raw", "foo", "foo_bar", "foo_bar.h5"
    ): ESRFv2Schema(
        data_root=make_path("visitor"),
        proposal="ma6658",
        beamline="id21",
        session_date="20250509",
        data_type="raw",
        collection="foo",
        dataset="bar",
    ),
    make_path(
        "visitor", "ma6658", "id21", "20250509", "foo", "foo_bar", "foo_bar.h5"
    ): ESRFv1Schema(
        data_root=make_path("visitor"),
        proposal="ma6658",
        beamline="id21",
        session_date="20250509",
        collection="foo",
        dataset="bar",
    ),
    NOT_ESRF_PATH: None,
}


@pytest.mark.parametrize("input_path", TEST_PATHS.keys())
def test_esrf_path_esrf_schema(input_path):
    path = ESRFPath(input_path)
    assert path._esrf_schema == TEST_PATHS[input_path]


@pytest.mark.parametrize("input_path", TEST_PATHS.keys())
def test_esrf_path_attributes(input_path):
    path = ESRFPath(input_path)
    expected_schema = TEST_PATHS[input_path]

    if expected_schema is None:
        # Access schema attributes
        with pytest.raises(
            AttributeError,
            match=r"'ESRFPath' object has no attribute 'data_root' \(not an ESRF path\)",
        ):
            _ = path.data_root
        # Access non-existing attribute
        with pytest.raises(
            AttributeError,
            match=r"'ESRFPath' object has no attribute 'not_an_attribute' \(not an ESRF path\)",
        ):
            _ = path.not_an_attribute
    else:
        # Access schema attributes
        for field in fields(expected_schema):
            actual = getattr(path, field.name)
            expected = getattr(expected_schema, field.name)
            assert actual == expected, field.name
        # Access non-existing attribute
        with pytest.raises(
            AttributeError,
            match="'ESRFPath' object has no attribute 'not_an_attribute'",
        ):
            _ = path.not_an_attribute


def test_inherit_from_existing_path():
    p1 = ESRFPath(
        make_path(
            "visitor",
            "ma6658",
            "id21",
            "20250509",
            "RAW_DATA",
            "foo",
            "foo_bar",
            "foo_bar.h5",
        )
    )
    p2 = ESRFPath(p1)
    assert p2._esrf_schema == p1._esrf_schema


def test_parent():
    path = ESRFPath(
        make_path(
            "visitor",
            "ma6658",
            "id21",
            "20250509",
            "raw",
            "foo",
            "foo_bar",
            "foo_bar.h5",
        )
    )

    parent = path.parent
    assert safe_repr(parent) == f"ESRFPath('{str(parent)}')"
    assert parent._esrf_schema == path._esrf_schema

    parent = parent.parent
    assert safe_repr(parent) == f"ESRFPath('{str(parent)}')"
    assert parent._esrf_schema == ESRFv2Schema(
        data_root=make_path("visitor"),
        proposal="ma6658",
        beamline="id21",
        session_date="20250509",
        data_type="raw",
        collection="foo",
        dataset=None,
    )

    parent = parent.parent
    assert safe_repr(parent) == f"ESRFPath('{str(parent)}')"
    assert parent._esrf_schema == ESRFv2Schema(
        data_root=make_path("visitor"),
        proposal="ma6658",
        beamline="id21",
        session_date="20250509",
        data_type="raw",
        collection=None,
        dataset=None,
    )

    parent = parent.parent
    assert safe_repr(parent) == f"ESRFPath('{str(parent)}')"
    assert parent._esrf_schema == ESRFv1Schema(
        data_root=make_path("visitor"),
        proposal="ma6658",
        beamline="id21",
        session_date="20250509",
        collection=None,
        dataset=None,
    )

    parent = parent.parent
    assert safe_repr(parent) == f"ESRFPath('{str(parent)}')"
    assert parent._esrf_schema is None


def test_str():
    path_str = make_path(
        "visitor", "ma6658", "id21", "20250509", "raw", "foo", "foo_bar", "foo_bar.h5"
    )
    path = ESRFPath(path_str)
    assert str(path) == path_str


def test_repr():
    path_str = make_path(
        "visitor", "ma6658", "id21", "20250509", "raw", "foo", "foo_bar", "foo_bar.h5"
    )
    path = ESRFPath(path_str)
    assert safe_repr(path) == f"ESRFPath('{path_str}')"


def test_dir():
    path_str = make_path(
        "visitor", "ma6658", "id21", "20250509", "raw", "foo", "foo_bar", "foo_bar.h5"
    )
    path = ESRFPath(path_str)
    expected = {field.name for field in fields(ESRFv2Schema)}
    assert expected.issubset(set(dir(path)))


def test_dir_without_esrf_schema():
    esrf_path = ESRFPath(NOT_ESRF_PATH)
    path = pathlib.Path(NOT_ESRF_PATH)

    assert set(dir(path)).issubset(set(dir(esrf_path)))


@pytest.mark.parametrize("input_path", TEST_PATHS.keys())
def test_reconstruct_path(input_path):
    path = ESRFPath(input_path)
    if path._esrf_schema:
        assert path._esrf_schema.reconstruct_path() == os.path.dirname(input_path)


def test_replace_fields():
    path_str1 = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "RAW_DATA",
        "foo",
        "foo_bar",
        "foo_bar.h5",
    )
    path_str2 = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "PROCESSED_DATA",
        "foo",
        "foo_bar",
        "foo_bar.h5",
    )
    path1 = ESRFPath(path_str1)
    path2 = path1.replace_fields(data_type="PROCESSED_DATA")
    assert str(path2) == path_str2

    path_str1 = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "RAW_DATA",
        "foo",
        "foo_bar",
        "foo_bar.h5",
    )
    path_str2 = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "RAW_DATA",
        "baz",
        "baz_bar",
        "foo_bar.h5",
    )
    path1 = ESRFPath(path_str1)
    path2 = path1.replace_fields(collection="baz")
    assert str(path2) == path_str2

    path_str1 = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "RAW_DATA",
        "foo",
        "foo_bar",
    )
    path_str2 = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "RAW_DATA",
        "baz",
        "baz_bar",
    )
    path1 = ESRFPath(path_str1)
    path2 = path1.replace_fields(collection="baz")
    assert str(path2) == path_str2


def test_raw_dataset_path():
    path_str1 = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "PROCESSED_DATA",
        "foo",
        "foo_bar",
        "process1",
        "foo_bar_process1.h5",
    )
    path_str2 = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "RAW_DATA",
        "foo",
        "foo_bar",
    )
    path1 = ESRFPath(path_str1)
    path2 = path1.raw_dataset_path
    assert str(path2) == path_str2

    with pytest.raises(AttributeError, match="Field has no value: 'dataset'"):
        _ = path2.parent.raw_dataset_path


def test_data_type_root_paths():
    path_str1 = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "PROCESSED_DATA",
        "foo",
        "foo_bar",
        "process1",
        "foo_bar_process1.h5",
    )
    path_str2 = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "RAW_DATA",
    )
    path1 = ESRFPath(path_str1)
    path2 = path1.raw_data_path
    assert str(path2) == path_str2

    path_str2 = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "PROCESSED_DATA",
    )
    path2 = path1.processed_data_path
    assert str(path2) == path_str2

    path_str2 = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "SCRIPTS",
    )
    path2 = path1.scripts_path
    assert str(path2) == path_str2

    path_str2 = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "NOBACKUP",
    )
    path2 = path1.nobackup_path
    assert str(path2) == path_str2

    path_str1 = make_path(
        "visitor",
        "ma6658",
        "id21",
    )
    path1 = ESRFPath(path_str1)
    with pytest.raises(
        AttributeError,
        match=re.escape(
            "'ESRFPath' object has no attribute 'raw_data_path' (not an ESRF path)"
        ),
    ):
        _ = path1.raw_data_path


def test_filenames():
    path_str1 = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "PROCESSED_DATA",
        "foo",
        "foo_bar",
        "process1",
        "foo_bar_process1.h5",
    )
    path1 = ESRFPath(path_str1)

    path_str2 = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "RAW_DATA",
        "foo",
        "foo_bar",
        "foo_bar.h5",
    )
    path2 = path1.raw_dataset_file
    assert str(path2) == path_str2

    path_str2 = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "RAW_DATA",
        "foo",
        "ma6658_foo.h5",
    )
    path2 = path1.raw_collection_file
    assert str(path2) == path_str2

    path_str2 = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "RAW_DATA",
        "ma6658_id21.h5",
    )
    path2 = path1.raw_proposal_file
    assert str(path2) == path_str2


def test_from_fields():
    path_str1 = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "RAW_DATA",
        "foo",
    )
    path1 = ESRFPath(path_str1)
    path2 = ESRFPath.from_fields(
        data_root=make_path("visitor"),
        proposal="ma6658",
        beamline="id21",
        session_date="20250509",
        data_type="RAW_DATA",
        collection="foo",
    )
    assert path1 == path2

    path_str1 = make_path(
        "visitor", "ma6658", "id21", "20250509", "RAW_DATA", "foo", "foo_bar"
    )
    path1 = ESRFPath(path_str1)
    path2 = ESRFPath.from_fields(
        data_root=make_path("visitor"),
        proposal="ma6658",
        beamline="id21",
        session_date="20250509",
        data_type="RAW_DATA",
        collection="foo",
        dataset="bar",
    )
    assert path1 == path2


def test_immutable_schema_fields():
    path_str = make_path(
        "visitor",
        "ma6658",
        "id21",
        "20250509",
        "RAW_DATA",
        "foo",
    )
    path = ESRFPath(path_str)
    with pytest.raises(AttributeError, match="can't set attribute 'proposal'"):
        path.proposal = "ma6659"
