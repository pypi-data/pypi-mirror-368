import json
import os
import shutil
import tempfile

import pytest

import libcoveocds.common_checks
import libcoveocds.exceptions
import libcoveocds.schema
from tests import CONFIG, fixture_path


@pytest.mark.skipif(not CONFIG, reason="not in API context")
def test_bad_context():
    output_dir = tempfile.mkdtemp(prefix="libcoveocds-tests-", dir=tempfile.gettempdir())
    schema = libcoveocds.schema.SchemaOCDS()
    with open(fixture_path("fixtures", "common_checks", "dupe_ids_1.json")) as fp:
        json_data = json.load(fp)

    try:
        with pytest.raises(libcoveocds.exceptions.LibCoveOCDSError):
            libcoveocds.common_checks.common_checks_ocds({"file_type": "json"}, output_dir, json_data, schema)
    finally:
        shutil.rmtree(output_dir)


def test_basic_1():
    output_dir = tempfile.mkdtemp(prefix="libcoveocds-tests-", dir=tempfile.gettempdir())
    schema = libcoveocds.schema.SchemaOCDS(lib_cove_ocds_config=CONFIG)
    with open(fixture_path("fixtures", "common_checks", "basic_1.json")) as fp:
        json_data = json.load(fp)

    try:
        results = libcoveocds.common_checks.common_checks_ocds({"file_type": "json"}, output_dir, json_data, schema)
    finally:
        shutil.rmtree(output_dir)

    assert results["version_used"] == "1.1"


def test_dupe_ids_1():
    output_dir = tempfile.mkdtemp(prefix="libcoveocds-tests-", dir=tempfile.gettempdir())
    schema = libcoveocds.schema.SchemaOCDS(lib_cove_ocds_config=CONFIG)
    with open(fixture_path("fixtures", "common_checks", "dupe_ids_1.json")) as fp:
        json_data = json.load(fp)

    try:
        results = libcoveocds.common_checks.common_checks_ocds({"file_type": "json"}, output_dir, json_data, schema)
    finally:
        shutil.rmtree(output_dir)

    # https://github.com/OpenDataServices/cove/issues/782 Defines how we want this error shown
    assert len(results["validation_errors"][0][1]) == 2
    # test paths
    assert results["validation_errors"][0][1][0]["path"] == "releases"
    assert results["validation_errors"][0][1][1]["path"] == "releases"
    # test values
    # we don't know what order they will come out in, so fix the order ourselves
    values = [
        results["validation_errors"][0][1][0]["value"],
        results["validation_errors"][0][1][1]["value"],
    ]
    values.sort()
    assert values[0] == "ocds-213czf-000-00001, ocds-213czf-000-00001-01-planning"
    assert values[1] == "ocds-213czf-000-00001, ocds-213czf-000-00001-02-planning"


@pytest.mark.parametrize(
    ("record_pkg", "filename", "schema_subdir", "validation_error_jsons_expected"),
    [
        (False, "releases_no_validation_errors.json", "", []),
        (True, "records_no_validation_errors.json", "", []),
        (
            True,
            "records_invalid_releases.json",
            "",
            [
                {
                    "message": "'date' is missing but required within 'releases'",
                    "message_safe": "&#x27;date&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "embedded_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "date",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/2/releases/0"}],
                },
                {
                    "message": "'date' is missing but required within 'releases'",
                    "message_safe": "&#x27;date&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "linked_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "date",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [
                        {"path": "records/1/releases/0"},
                        {"path": "records/3/releases/0"},
                    ],
                },
                {
                    "message": "'initiationType' is missing but required within 'releases'",
                    "message_safe": "&#x27;initiationType&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "embedded_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "initiationType",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/2/releases/0"}],
                },
                {
                    "message": "'ocid' is missing but required within 'releases'",
                    "message_safe": "&#x27;ocid&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "embedded_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "ocid",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/2/releases/0"}],
                },
                {
                    "message": "'releases' is not a JSON array",
                    "message_safe": "&#x27;releases&#x27; is not a JSON array",
                    "validator": "type",
                    "assumption": "linked_releases",
                    "message_type": "array",
                    "path_no_number": "records/releases",
                    "header": "releases",
                    "header_extra": "releases",
                    "null_clause": "is not null, and",
                    "error_id": None,
                    "values": [
                        {"path": "records/6/releases", "value": "a string"},
                        {"path": "records/7/releases", "value": None},
                        {"path": "records/8/releases"},
                    ],
                    "docs_ref": "record-package-schema.json,/definitions/record,releases",
                    "schema_title": "Releases",
                    "schema_description_safe": "<p>An array of linking identifiers or releases</p>\n",
                },
                {
                    "message": "'tag' is missing but required within 'releases'",
                    "message_safe": "&#x27;tag&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "embedded_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "tag",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/2/releases/0"}],
                },
                {
                    "message": "'url' is missing but required within 'releases'",
                    "message_safe": "&#x27;url&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "linked_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "url",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/1/releases/0"}],
                },
                {
                    "message": "This array should contain either entirely embedded releases or linked releases. Embedded releases contain an 'id' whereas linked releases do not. Your releases contain a mixture.",  # noqa: E501
                    "message_safe": "This array should contain either entirely embedded releases or linked releases. Embedded releases contain an &#x27;id&#x27; whereas linked releases do not. Your releases contain a mixture.",  # noqa: E501
                    "validator": "oneOf",
                    "assumption": None,
                    "message_type": "oneOf",
                    "path_no_number": "records/releases",
                    "header": "releases",
                    "header_extra": "releases",
                    "null_clause": "",
                    "error_id": "releases_both_embedded_and_linked",
                    "values": [
                        {"path": "records/4/releases"},
                        {"path": "records/5/releases"},
                    ],
                    "docs_ref": "record-package-schema.json,/definitions/record,releases",
                    "schema_title": "Releases",
                    "schema_description_safe": "<p>An array of linking identifiers or releases</p>\n",
                },
                {
                    "message": "[] should be non-empty",
                    "message_safe": "[] should be non-empty",
                    "validator": "minItems",
                    "assumption": "linked_releases",
                    "message_type": "minItems",
                    "path_no_number": "records/releases",
                    "header": "releases",
                    "header_extra": "releases",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/0/releases"}],
                    "instance": [],
                    "docs_ref": "record-package-schema.json,/definitions/record,releases",
                    "schema_title": "Releases",
                    "schema_description_safe": "<p>An array of linking identifiers or releases</p>\n",
                },
            ],
        ),
        (
            True,
            "records_invalid_releases.json",
            "1-0",
            [
                {
                    "message": "'date' is missing but required within 'releases'",
                    "message_safe": "&#x27;date&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "embedded_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "date",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/2/releases/0"}],
                },
                {
                    "message": "'date' is missing but required within 'releases'",
                    "message_safe": "&#x27;date&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "linked_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "date",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [
                        {"path": "records/1/releases/0"},
                        {"path": "records/3/releases/0"},
                    ],
                },
                {
                    "message": "'initiationType' is missing but required within 'releases'",
                    "message_safe": "&#x27;initiationType&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "embedded_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "initiationType",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/2/releases/0"}],
                },
                {
                    "message": "'ocid' is missing but required within 'releases'",
                    "message_safe": "&#x27;ocid&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "embedded_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "ocid",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/2/releases/0"}],
                },
                {
                    "message": "'releases' is not a JSON array",
                    "message_safe": "&#x27;releases&#x27; is not a JSON array",
                    "validator": "type",
                    "assumption": "linked_releases",
                    "message_type": "array",
                    "path_no_number": "records/releases",
                    "header": "releases",
                    "header_extra": "releases",
                    "null_clause": "is not null, and",
                    "error_id": None,
                    "values": [
                        {"path": "records/6/releases", "value": "a string"},
                        {"path": "records/7/releases", "value": None},
                        {"path": "records/8/releases"},
                    ],
                    "docs_ref": "record-package-schema.json,/definitions/record,releases",
                    "schema_title": "Releases",
                    "schema_description_safe": "<p>An array of linking identifiers or releases</p>\n",
                },
                {
                    "message": "'tag' is missing but required within 'releases'",
                    "message_safe": "&#x27;tag&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "embedded_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "tag",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/2/releases/0"}],
                },
                {
                    "message": "'url' is missing but required within 'releases'",
                    "message_safe": "&#x27;url&#x27; is missing but required within &#x27;releases&#x27;",
                    "validator": "required",
                    "assumption": "linked_releases",
                    "message_type": "required",
                    "path_no_number": "records/releases",
                    "header": "url",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/1/releases/0"}],
                },
                {
                    "message": "This array should contain either entirely embedded releases or linked releases. Embedded releases contain an 'id' whereas linked releases do not. Your releases contain a mixture.",  # noqa: E501
                    "message_safe": "This array should contain either entirely embedded releases or linked releases. Embedded releases contain an &#x27;id&#x27; whereas linked releases do not. Your releases contain a mixture.",  # noqa: E501
                    "validator": "oneOf",
                    "assumption": None,
                    "message_type": "oneOf",
                    "path_no_number": "records/releases",
                    "header": "releases",
                    "header_extra": "releases",
                    "null_clause": "",
                    "error_id": "releases_both_embedded_and_linked",
                    "values": [
                        {"path": "records/4/releases"},
                        {"path": "records/5/releases"},
                    ],
                    "docs_ref": "record-package-schema.json,/definitions/record,releases",
                    "schema_title": "Releases",
                    "schema_description_safe": "<p>An array of linking identifiers or releases</p>\n",
                },
                {
                    "message": "[] should be non-empty",
                    "message_safe": "[] should be non-empty",
                    "validator": "minItems",
                    "assumption": "linked_releases",
                    "message_type": "minItems",
                    "path_no_number": "records/releases",
                    "header": "releases",
                    "header_extra": "releases",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/0/releases"}],
                    "instance": [],
                    "docs_ref": "record-package-schema.json,/definitions/record,releases",
                    "schema_title": "Releases",
                    "schema_description_safe": "<p>An array of linking identifiers or releases</p>\n",
                },
            ],
        ),
        (
            False,
            "releases_non_unique.json",
            "",
            [
                {
                    "message": "Non-unique combination of ocid, id values",
                    "message_safe": "Non-unique combination of ocid, id values",
                    "validator": "uniqueItems",
                    "assumption": None,
                    "message_type": "uniqueItems",
                    "path_no_number": "releases",
                    "header": "releases",
                    "header_extra": "releases",
                    "null_clause": "",
                    "error_id": "uniqueItems_with_ocid__id",
                    "values": [
                        {"path": "releases", "value": "EXAMPLE-1, EXAMPLE-1-1"},
                        {"path": "releases", "value": "EXAMPLE-1, EXAMPLE-1-2"},
                    ],
                    "docs_ref": "release-package-schema.json,,releases",
                    "schema_title": "Releases",
                    "schema_description_safe": "<p>An array of one or more OCDS releases.</p>\n",
                }
            ],
        ),
        (False, "releases_unique_ocids_but_not_ids.json", "", []),
        (
            True,
            "records_non_unique.json",
            "",
            [
                {
                    "message": "Non-unique ocid values",
                    "message_safe": "Non-unique ocid values",
                    "validator": "uniqueItems",
                    "assumption": None,
                    "message_type": "uniqueItems",
                    "path_no_number": "records",
                    "header": "records",
                    "header_extra": "records",
                    "null_clause": "",
                    "error_id": "uniqueItems_with_ocid",
                    "values": [
                        {"path": "records", "value": "EXAMPLE-1"},
                        {"path": "records", "value": "EXAMPLE-2"},
                    ],
                    "docs_ref": "record-package-schema.json,,records",
                    "schema_title": "Records",
                    "schema_description_safe": "<p>The records for this data package.</p>\n",
                }
            ],
        ),
        (
            False,
            "releases_non_unique_no_id.json",
            "",
            [
                {
                    "message": "'id' is missing but required",
                    "message_safe": "&#x27;id&#x27; is missing but required",
                    "validator": "required",
                    "assumption": None,
                    "message_type": "required",
                    "path_no_number": "releases",
                    "header": "id",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "releases/0"}, {"path": "releases/1"}],
                },
                {
                    "message": "Array has non-unique elements",
                    "message_safe": "Array has non-unique elements",
                    "validator": "uniqueItems",
                    "assumption": None,
                    "message_type": "uniqueItems",
                    "path_no_number": "releases",
                    "header": "releases",
                    "header_extra": "releases",
                    "null_clause": "",
                    "error_id": "uniqueItems_no_ids",
                    "values": [{"path": "releases"}],
                    "docs_ref": "release-package-schema.json,,releases",
                    "schema_title": "Releases",
                    "schema_description_safe": "<p>An array of one or more OCDS releases.</p>\n",
                },
            ],
        ),
        (
            True,
            "records_non_unique_no_ocid.json",
            "",
            [
                {
                    "message": "'ocid' is missing but required",
                    "message_safe": "&#x27;ocid&#x27; is missing but required",
                    "validator": "required",
                    "assumption": None,
                    "message_type": "required",
                    "path_no_number": "records",
                    "header": "ocid",
                    "header_extra": "records/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/0"}, {"path": "records/1"}],
                },
                {
                    "message": "Array has non-unique elements",
                    "message_safe": "Array has non-unique elements",
                    "validator": "uniqueItems",
                    "assumption": None,
                    "message_type": "uniqueItems",
                    "path_no_number": "records",
                    "header": "records",
                    "header_extra": "records",
                    "null_clause": "",
                    "error_id": "uniqueItems_no_ids",
                    "values": [{"path": "records"}],
                    "docs_ref": "record-package-schema.json,,records",
                    "schema_title": "Records",
                    "schema_description_safe": "<p>The records for this data package.</p>\n",
                },
            ],
        ),
        # Check that we handle unique arrays correctly also
        # (e.g. that we don't incorrectly claim they are not unique)
        (
            False,
            "releases_unique.json",
            "",
            [
                {
                    "message": "'id' is missing but required",
                    "message_safe": "&#x27;id&#x27; is missing but required",
                    "validator": "required",
                    "assumption": None,
                    "message_type": "required",
                    "path_no_number": "releases",
                    "header": "id",
                    "header_extra": "releases/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "releases/0"}, {"path": "releases/1"}],
                }
            ],
        ),
        (
            True,
            "records_unique.json",
            "",
            [
                {
                    "message": "'ocid' is missing but required",
                    "message_safe": "&#x27;ocid&#x27; is missing but required",
                    "validator": "required",
                    "assumption": None,
                    "message_type": "required",
                    "path_no_number": "records",
                    "header": "ocid",
                    "header_extra": "records/[number]",
                    "null_clause": "",
                    "error_id": None,
                    "values": [{"path": "records/0"}, {"path": "records/1"}],
                }
            ],
        ),
    ],
)
def test_validation_release_or_record_package(record_pkg, filename, validation_error_jsons_expected, schema_subdir):
    output_dir = tempfile.mkdtemp(prefix="libcoveocds-tests-", dir=tempfile.gettempdir())
    schema = libcoveocds.schema.SchemaOCDS(record_pkg=record_pkg, lib_cove_ocds_config=CONFIG)
    with open(os.path.join(fixture_path("fixtures", "common_checks", schema_subdir, ""), filename)) as fp:
        json_data = json.load(fp)

    results = libcoveocds.common_checks.common_checks_ocds({"file_type": "json"}, output_dir, json_data, schema)

    validation_errors = results["validation_errors"]

    validation_error_jsons = []
    for validation_error_json, values in validation_errors:
        validation_error_json = json.loads(validation_error_json)
        validation_error_json["values"] = values
        # Remove this as it can be a rather large schema object
        del validation_error_json["validator_value"]
        validation_error_jsons.append(validation_error_json)

    def strip_nones(list_of_dicts):
        return [{key: value for key, value in a_dict.items() if value is not None} for a_dict in list_of_dicts]

    if CONFIG:  # if in API context
        for validation_error_json in validation_error_jsons_expected:
            for key in ("docs_ref", "message_safe", "schema_description_safe", "schema_title"):
                validation_error_json.pop(key, None)

    assert strip_nones(validation_error_jsons) == strip_nones(validation_error_jsons_expected)


def test_ref_error(tmpdir):
    url = "https://raw.githubusercontent.com/open-contracting/lib-cove-ocds/main/tests/fixtures/extensions/unresolvable/extension.json"
    json_data = {"version": "1.1", "extensions": [url], "releases": [{"unresolvable": "1"}]}
    schema = libcoveocds.schema.SchemaOCDS("1.1", json_data)

    libcoveocds.common_checks.common_checks_ocds({"file_type": "json"}, tmpdir, json_data, schema)
