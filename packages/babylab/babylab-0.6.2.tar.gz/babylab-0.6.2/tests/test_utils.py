"""Test util functions"""

from typing import Generator
from datetime import date, datetime
import polars as pl
import pytest
from babylab import api, utils


def test_fmt_labels_dict(data_dict):
    x = {"source": "1", "sex": "2", "isdropout": "0", "age_now_months": "2"}
    o = utils.fmt_labels(x, data_dict)
    assert isinstance(o, dict)
    assert all(k in o for k in x)
    assert isinstance(o["source"], str)
    assert isinstance(o["sex"], str)
    assert isinstance(o["isdropout"], bool)
    assert isinstance(o["age_now_months"], int)
    assert o["source"] == "SJD Àrea de la Dona"
    assert o["sex"] == "Male"
    assert o["isdropout"] is False
    assert o["age_now_months"] == 2


def test_fmt_labels_polars(data_dict):
    x = pl.DataFrame(
        data={"source": "1", "sex": "2", "isdropout": "0", "age_now_months": "2"},
    )
    o = utils.fmt_labels(x, data_dict)
    assert isinstance(o, pl.DataFrame)
    assert all(k in o for k in x.columns)
    assert o["source"][0] == "SJD Àrea de la Dona"
    assert o["sex"][0] == "Male"
    assert not o["isdropout"][0]
    assert o["age_now_months"][0] == 2


def test_get_ppt_table(records_fixture: api.Records, data_dict: dict):
    df = utils.get_ppt_table(records_fixture, data_dict)
    assert isinstance(df, pl.DataFrame)
    assert all(c in df.columns for c in utils.COLNAMES["participants"])


def test_get_ppt_table_study(records_fixture: api.Records, data_dict: dict):
    for s in data_dict["appointment_study"]:
        df = utils.get_ppt_table(records_fixture, data_dict, study=s)
        assert isinstance(df, pl.DataFrame)
    assert all(c in df.columns for c in utils.COLNAMES["participants"])


def test_get_apt_table(records_fixture: api.Records, data_dict: dict):
    df = utils.get_apt_table(records_fixture, data_dict)
    assert isinstance(df, pl.DataFrame)
    assert all(c in df.columns for c in utils.COLNAMES["appointments"])


def test_is_in_data_dict(data_dict: dict):
    """Test is_in_datadict."""
    assert utils.is_in_data_dict(["Successful"], "appointment_status", data_dict) == [
        "Successful"
    ]
    assert utils.is_in_data_dict(
        ["Successful", "Confirmed"], "appointment_status", data_dict
    ) == ["Successful", "Confirmed"]
    assert utils.is_in_data_dict("Successful", "appointment_status", data_dict) == [
        "Successful"
    ]
    assert utils.is_in_data_dict(
        ["mop_newborns_1_nirs"], "appointment_study", data_dict
    ) == ["mop_newborns_1_nirs"]
    assert utils.is_in_data_dict(
        ["mop_newborns_1_nirs", "mop_infants_1_hpp"], "appointment_study", data_dict
    ) == ["mop_newborns_1_nirs", "mop_infants_1_hpp"]
    assert utils.is_in_data_dict(
        "mop_newborns_1_nirs", "appointment_study", data_dict
    ) == ["mop_newborns_1_nirs"]

    with pytest.raises(ValueError):
        utils.is_in_data_dict(["Badname"], "appointment_status", data_dict)
        utils.is_in_data_dict(
            ["Badname", "Successful"], "appointment_status", data_dict
        )
        utils.is_in_data_dict("Badname", "appointment_status", data_dict)


def test_get_year_weeks():
    """Test get_year_weeks."""
    assert isinstance(utils.get_year_weeks(2025), Generator)
    assert isinstance(next(utils.get_year_weeks(2025)), date)


def test_get_week_n():
    """Test get_week_n."""
    assert isinstance(utils.get_week_n(datetime.today()), int)


def test_get_weekly_apts(data_dict, records_fixture):
    """Test get_weekly_apts."""
    assert isinstance(
        utils.get_weekly_apts(data_dict=data_dict, records=records_fixture), int
    )
    assert isinstance(
        utils.get_weekly_apts(
            data_dict=data_dict, records=records_fixture, study="mop_newborns_1_nirs"
        ),
        int,
    )
    assert isinstance(
        utils.get_weekly_apts(
            data_dict=data_dict,
            records=records_fixture,
            study="mop_newborns_1_nirs",
            status="Successful",
        ),
        int,
    )
    assert isinstance(
        utils.get_weekly_apts(
            data_dict=data_dict,
            records=records_fixture,
            study=["mop_newborns_1_nirs", "mop_infants_1_hpp"],
        ),
        int,
    )
    assert isinstance(
        utils.get_weekly_apts(
            data_dict=data_dict,
            records=records_fixture,
            study=["mop_newborns_1_nirs", "mop_infants_1_hpp"],
            status=["Successful", "Confirmed"],
        ),
        int,
    )
