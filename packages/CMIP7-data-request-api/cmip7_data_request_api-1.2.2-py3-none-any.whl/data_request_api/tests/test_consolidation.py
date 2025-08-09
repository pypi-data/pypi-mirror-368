import pytest

import data_request_api.utilities.config as dreqcfg
from data_request_api.content import dreq_content as dc
from data_request_api.content.consolidate_export import (
    _apply_consistency_fixes,
    _filter_references,
    _map_attribute,
    _map_record_id,
    map_data,
)
from data_request_api.content.mapping_table import version_consistency_drop_fields, version_consistency_fields
from data_request_api.tests import filepath
from data_request_api.utilities.logger import change_log_file, change_log_level
from data_request_api.utilities.tools import read_json_file, write_json_output_file_content


@pytest.mark.skip(reason="Work on this test deferred to allow release")
def test_map_record_id():
    # Read 3-base export
    several_bases_input = read_json_file(filepath("several_bases_input.json"))
    # Select a variable record to map (day.wap)
    record = several_bases_input["Data Request Variables (Public)"]["Variable"]["records"]["recIHH5OexHWtBNgn"]
    # Select the list of records to map against
    records = several_bases_input["Data Request Opportunities (Public)"]["Variables"]["records"]
    # Assert successful mapping via keys UID and Compound Name
    assert _map_record_id(record, records, ["Compound Name"]) == ["recIEe4GucNn5Bp1t"]
    assert _map_record_id(record, records, ["UID"]) == ["recIEe4GucNn5Bp1t"]
    # Delete the mapped record and assert no match is found
    record_rm = records.pop("recIEe4GucNn5Bp1t")
    assert _map_record_id(record, records, ["Compound Name"]) == []
    # Duplicate the record back in and assert two matches are found now
    records["test1"] = record_rm
    records["test2"] = record_rm.copy()
    assert _map_record_id(record, records, ["UID", "Compound Name"]) == ["test1", "test2"]
    # Alter the UID of one duplicated entry and assert one match is found
    records["test2"]["UID"] = "someUID"
    assert _map_record_id(record, records, ["UID", "Compound Name"]) == ["test1"]


def test_map_attribute():
    # Read 3-base export
    several_bases_input = read_json_file(filepath("several_bases_input.json"))
    # Select a CF Standard Name to map (lagrangian_tendency_of_air_pressure)
    attr = "lagrangian_tendency_of_air_pressure"
    # Select the list of records to map against
    records = several_bases_input["Data Request Physical Parameters (Public)"]["CF Standard Name"]["records"]
    # Assert successful mapping via key "name"
    assert _map_attribute(attr, records, ["name"]) == ["rectR4F3k6a6p7VPv"]
    # Delete the mapped record and assert no match is found
    record_rm = records.pop("rectR4F3k6a6p7VPv")
    assert _map_attribute(attr, records, ["name"]) == []
    # Duplicate the record back in and assert two matches are found now
    records["test1"] = record_rm
    records["test2"] = record_rm.copy()
    assert _map_attribute(attr, records, ["name"]) == ["test1", "test2"]
    # Alter the name of one duplicated entry and assert one match is found
    records["test2"]["name"] = "someName"
    assert _map_attribute(attr, records, ["name"]) == ["test1"]


def test_apply_consistency_fixes():
    # Consistency fixes for Variables table fields
    varfield_renamed = list(version_consistency_fields["Variables"].values())
    varfield_torename = list(version_consistency_fields["Variables"].keys())
    varfield_dropped = list(version_consistency_drop_fields["Variables"])
    assert varfield_renamed != []
    assert varfield_torename != []
    assert varfield_dropped != []
    # Read 1-base export and select certain tables
    one_base_input = read_json_file(filepath("one_base_input.json"))["Data Request v1.2.2"]
    selected_tables = ["Variables", "Variable Group", "Time Subset", "CF Standard Names", "Structure"]
    subset = {table: one_base_input[table] for table in one_base_input if table in selected_tables}
    # Apply consistency fixes
    subset = _apply_consistency_fixes(subset)
    # Assert consistency fixes are applied, i.e. tables and fields renamed or removed as intended
    assert set(subset.keys()) == {"Variables", "Variable Group", "Time Subset", "CF Standard Names"}
    fields = {j["name"] for i, j in subset["Variables"]["fields"].items()}
    assert all([i not in fields for i in varfield_dropped])
    assert all([i in fields for i in varfield_renamed])
    for r, v in subset["Variables"]["records"].items():
        assert all([i not in v.keys() for i in varfield_dropped + varfield_torename])
