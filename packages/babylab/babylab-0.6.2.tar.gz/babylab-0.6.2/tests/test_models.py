"""Test database models"""

from datetime import datetime
from polars import DataFrame
from babylab import api


def test_participant_class(ppt_record):
    """Test participant class."""
    ppt = api.Participant(ppt_record)
    assert hasattr(ppt, "record_id")
    assert hasattr(ppt, "data")

    assert isinstance(ppt.record_id, str)
    assert isinstance(ppt.data, dict)

    assert isinstance(repr(ppt), str)
    assert "Participant " in repr(ppt)
    assert isinstance(str(ppt), str)
    assert "Participant " in str(ppt)


def test_appointment_class(apt_record):
    """Test appointment class."""
    apt = api.Appointment(apt_record)
    assert hasattr(apt, "appointment_id")
    assert hasattr(apt, "record_id")
    assert hasattr(apt, "date")
    assert hasattr(apt, "status")
    assert hasattr(apt, "data")

    assert isinstance(apt.appointment_id, str)
    assert isinstance(apt.record_id, str)
    assert isinstance(apt.date, datetime)
    assert isinstance(apt.status, str)
    assert isinstance(apt.data, dict)

    assert isinstance(repr(apt), str)
    assert "Appointment " in repr(apt)
    assert isinstance(str(apt), str)
    assert "Appointment " in str(apt)


def test_questionnaire_class(que_record):
    """Test questionnaire class."""
    que = api.Questionnaire(que_record)
    assert hasattr(que, "questionnaire_id")
    assert hasattr(que, "isestimated")
    assert hasattr(que, "record_id")
    assert hasattr(que, "data")
    assert isinstance(repr(que), str)
    assert "questionnaire " in repr(que).lower()
    assert isinstance(str(que), str)
    assert "questionnaire " in str(que).lower()


def test_records_class():
    """Test participant class."""
    records = api.Records()
    assert hasattr(records, "appointments")
    assert hasattr(records, "participants")
    assert hasattr(records, "questionnaires")
    assert isinstance(records.appointments, api.RecordList)
    assert isinstance(records.participants, api.RecordList)
    assert isinstance(records.questionnaires, api.RecordList)

    assert isinstance(repr(records), str)
    assert "REDCap database" in repr(records)
    assert isinstance(str(records), str)
    assert "REDCap database" in str(records)


def test_recordlist_class_participants():
    """Test RecordList class with participants."""
    records = api.Records().participants
    assert isinstance(records.records, dict)
    assert isinstance(records.to_df(), DataFrame)
    assert isinstance(records.kind, str)
    assert records.kind == "participants"


def test_recordlist_class_appointments():
    """Test RecordList class with appointments."""
    records = api.Records().appointments
    assert isinstance(records.records, dict)
    assert isinstance(records.to_df(), DataFrame)
    assert isinstance(records.kind, str)
    assert records.kind == "appointments"


def test_recordlist_class_questionnaires():
    """Test RecordList class with questionnaires."""
    records = api.Records().questionnaires
    assert isinstance(records.records, dict)
    assert isinstance(records.to_df(), DataFrame)
    assert isinstance(records.kind, str)
    assert records.kind == "questionnaires"


def test_records_class_participants(records_fixture):
    """Test records class (Participants)"""
    assert hasattr(records_fixture.participants, "records")
    assert hasattr(records_fixture.participants, "to_df")
    assert isinstance(records_fixture.participants.records, dict)
    assert all(
        isinstance(r, api.Participant)
        for r in records_fixture.participants.records.values()
    )


def test_records_class_appointments(records_fixture):
    """Test records class (Appointments)"""
    assert hasattr(records_fixture.appointments, "records")
    assert hasattr(records_fixture.appointments, "to_df")
    assert isinstance(records_fixture.appointments.records, dict)
    assert all(
        isinstance(r, api.Appointment)
        for r in records_fixture.appointments.records.values()
    )


def test_records_class_questionnaires(records_fixture):
    """Test records class (Questionnaires)"""
    assert hasattr(records_fixture.questionnaires, "records")
    assert hasattr(records_fixture.questionnaires, "to_df")
    assert isinstance(records_fixture.questionnaires.records, dict)
    assert all(
        isinstance(r, api.Questionnaire)
        for r in records_fixture.questionnaires.records.values()
    )
