#!/usr/bin/env python

"""
Functions to interact with the REDCap API.
"""

from dataclasses import dataclass
from os import mkdir, walk, getenv
from os.path import join, exists, expanduser
from collections import OrderedDict
from warnings import warn
from json import loads, dumps, dump
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime
from dateutil.relativedelta import relativedelta as rdelta
from pytz import UTC as utc
from dotenv import load_dotenv
import requests
import polars as pl
from babylab.globals import COLNAMES, FIELDS_TO_RENAME, INT_FIELDS

URI = "https://apps.sjdhospitalbarcelona.org/redcap/api/"


class MissingEnvException(Exception):
    """.env file is not found in user folder"""


class MissingEnvToken(Exception):
    """Token is not provided as key in .env"""


class MissingRecord(Exception):
    """Record is not found."""


class BadToken(Exception):
    """Token is ill-formed"""


class BadRecordListKind(Exception):
    """Bad RecordList kind"""


class BadAgeFormat(Exception):
    """If Age des not follow the right format"""


def get_api_key(path: str = None, name: str = "API_KEY"):
    """Retrieve API credentials.

    Args:
        path (str, optional): Path to the .env file with global variables. Defaults to ``expanduser(join("~", ".env"))``.
        name (str, optional): Name of the variable to import. Defaults to "API_KEY".

    Raises:
        MissingEnvException: If .en file is not found  in ``path``.
    """  # pylint: disable=line-too-long
    if getenv("GITHUB_ACTIONS") == "true":
        t = getenv(name)
    else:
        path = expanduser(join("~", ".env")) if path is None else path
        if not exists(path):
            raise MissingEnvException(f".env file not found in {path}")
        load_dotenv(path, override=True)
        t = getenv(name)
    if t is None:
        raise MissingEnvToken(f"No env variable named '{name}' found")
    if not isinstance(t, str) or not t.isalnum():
        raise BadToken("Token must be str with no non-alphanumeric characters")
    return t


@dataclass
class RecordList:
    """List of REDCap records."""

    records: dict
    kind: str | None = None

    def __len__(self) -> int:
        return len(self.records)

    def to_df(self) -> pl.DataFrame:
        """Transforms a a RecordList to a Pandas DataFrame.

        Returns:
            DataFrame: Tabular dataset.
        """  # pylint: disable=line-too-long
        recs = [p.data for p in self.records.values()]
        names = COLNAMES[self.kind]
        if not recs:
            return pl.DataFrame(schema=names)
        id_lookup = {
            "participants": "none",
            "appointments": "appointment_id",
            "questionnaires": "questionnaire_id",
        }
        df = (
            pl.DataFrame(data=recs)
            .rename({"redcap_repeat_instance": id_lookup[self.kind]}, strict=False)
            .select(names)
            .with_columns(
                pl.when(pl.col(pl.String).str.len_chars() == 0)
                .then(None)
                .otherwise(pl.col(pl.String))
                .name.keep()
            )
        )
        df = df.with_columns(
            pl.col(
                [f for f in INT_FIELDS if f in df.columns],
            ).cast(pl.Int128)
        )
        return df


def filter_fields(data: dict, prefix: str, fields: list[str]) -> dict:
    """Filter a data dictionary based on a prefix and field names.

    Args:
        records (dict): Record data dictionary.
        prefix (str): Prefix to look for.
        fields (list[str]): Field names to look for.

    Returns:
        dict: Filtered records.
    """  # pylint: disable=line-too-long
    return {
        k.replace(prefix, ""): v
        for k, v in data.items()
        if k.startswith(prefix) or k in fields
    }


class Participant:
    """Participant in database"""

    def __init__(self, data, apt: RecordList = None, que: RecordList = None):
        if (apt and apt.kind != "appointments") or (
            que and que.kind != "questionnaires"
        ):
            raise BadRecordListKind()
        data = filter_fields(data, "participant_", ["record_id"])
        age_created = (data["age_created_months"], data["age_created_days"])
        months, days = get_age(age_created, data["date_created"])
        data["age_now_months"], data["age_now_days"] = months, days
        self.record_id = data["record_id"]
        self.data = data
        self.appointments = apt
        self.questionnaires = que

    def __repr__(self) -> str:
        n_apt = 0 if not self.appointments else len(self.appointments) > 0
        n_que = 0 if not self.questionnaires else len(self.questionnaires) > 0
        return f"Participant {self.record_id}: {str(n_apt)} appointments, {str(n_que)} questionnaires"  # pylint: disable=line-too-long

    def __str__(self) -> str:
        n_apt = 0 if self.appointments is None else len(self.appointments)
        n_que = 0 if self.questionnaires is None else len(self.questionnaires)
        return f"Participant {self.record_id}: {str(n_apt)} appointments, {str(n_que)} questionnaires"  # pylint: disable=line-too-long


class Appointment:
    """Appointment in database"""

    def __init__(self, data: dict):
        data = filter_fields(
            data, "appointment_", ["record_id", "redcap_repeat_instance"]
        )
        self.record_id = data["record_id"]
        self.data = data
        self.appointment_id = make_id(data["record_id"], data["redcap_repeat_instance"])
        self.status = data["status"]
        if isinstance(data["date"], str):
            self.date = parse_str_date(data["date"])
        else:
            self.date = data["date"]
        self._description = (
            f"Appointment {self.appointment_id}"
            + f"participant {self.record_id}, "
            + f"{self.date}, {self.status}"
        )

    def __repr__(self) -> str:
        return self._description

    def __str__(self) -> str:
        return self._description


class Questionnaire:
    """Language questionnaire in database"""

    def __init__(self, data: dict):
        data = filter_fields(data, "language_", ["record_id", "redcap_repeat_instance"])
        self.record_id = data["record_id"]
        self.questionnaire_id = make_id(
            self.record_id,
            data["redcap_repeat_instance"],
        )
        self.isestimated = data["isestimated"]
        self.data = data
        for i in range(1, 5):
            lang = f"lang{i}_exp"
            self.data[lang] = int(self.data[lang]) if self.data[lang] else 0

    def __repr__(self) -> str:
        return f"Questionnaire {self.questionnaire_id}, participant {self.record_id}"

    def __str__(self) -> str:
        return f" Questionnaire {self.questionnaire_id}, participant {self.record_id}"


def post_request(fields: dict, timeout: list[int] = (5, 10)) -> dict:
    """Make a POST request to the REDCap database.

    Args:
        fields (dict): Fields to retrieve.
        timeout (list[int], optional): Timeout of HTTP request in seconds. Defaults to 10.

    Raises:
        requests.exceptions.HTTPError: If HTTP request fails.
        BadToken: If API token contains non-alphanumeric characters.

    Returns:
        dict: HTTP request response in JSON format.
    """  # pylint: disable=line-too-long
    t = get_api_key()
    if t is None:
        raise MissingEnvToken("No key found in your .env file")
    fields = OrderedDict(fields)
    fields["token"] = t
    fields.move_to_end("token", last=False)
    r = requests.post(URI, data=fields, timeout=timeout)
    r.raise_for_status()
    return r


def get_redcap_version() -> str:
    """Get REDCap version.

    Returns:
        str: REDCAp version number.
    """  # pylint: disable=line-too-long
    fields = {"content": "version"}
    r = post_request(fields=fields)
    return r.content.decode("utf-8")


def get_data_dict() -> dict:
    """Get data dictionaries for categorical variables.

    Returns:
        dict: Data dictionary.
    """  # pylint: disable=line-too-long
    fields = {"content": "metadata", "format": "json", "returnFormat": "json"}
    for idx, i in enumerate(FIELDS_TO_RENAME):
        fields[f"fields[{idx}]"] = i
    r = loads(post_request(fields=fields).text)
    items_ordered = [i["field_name"] for i in r]
    dicts = {}
    for k, v in zip(items_ordered, r):
        options = v["select_choices_or_calculations"].split("|")
        options = [tuple(o.strip().split(", ")) for o in options]
        if k.startswith("language_"):
            options = sorted(options, key=lambda x: x[1])
        dicts[k] = dict(options)
    return dicts


def str_to_dt(data: dict) -> dict:
    """Parse strings in a dictionary as formatted datetimes.

    It first tries to format the date as "Y-m-d H:M:S". If error, it assumes the "Y-m-d H:M" is due and tries to format it accordingly.

    Args:
        data (dict): Dictionary that may contain string formatted datetimes.

    Returns:
        dict: Dictionary with strings parsed as datetimes.
    """  # pylint: disable=line-too-long
    for k, v in data.items():
        if v and "date" in k:
            try:
                data[k] = datetime.strptime(data[k], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                data[k] = datetime.strptime(data[k], "%Y-%m-%d %H:%M")
    return data


def dt_to_str(data: dict) -> dict:
    """Format datatimes in a dictionary as strings following the ISO 8061 date format.

    Args:
        data (dict): Dictionary that may contain datetimes.

    Returns:
        dict: Dictionary with datetimes formatted as strings.
    """  # pylint: disable=line-too-long
    for k, v in data.items():
        if isinstance(v, datetime):
            data[k] = data[k].isoformat()
    return data


def get_next_id() -> str:
    """Get next record_id in REDCap database.

    Returns:
        str: record_id of next record.
    """  # pylint: disable=line-too-long
    fields = {"content": "generateNextRecordName"}
    return str(post_request(fields=fields).json())


def get_records(record_id: str | list | None = None) -> dict:
    """Return records as JSON.

    Args:
        record_id  (str): ID of record to retrieve. Defaults to None.

    Returns:
        dict: REDCap records in JSON format.
    """  # pylint: disable=line-too-long
    fields = {"content": "record", "format": "json", "type": "flat"}
    if record_id and isinstance(record_id, list):
        fields["records[0]"] = record_id
        for r in record_id:
            fields[f"records[{record_id}]"] = r
    records = post_request(fields=fields).json()
    return [str_to_dt(r) for r in records]


def make_id(ppt_id: str, repeat_id: str = None) -> str:
    """Make a record ID.

    Args:
        ppt_id (str): Participant ID.
        repeat_id (str, optional): Appointment or Questionnaire ID, or ``redcap_repeated_id``. Defaults to None.

    Returns:
        str: Record ID.
    """  # pylint: disable=line-too-long
    ppt_id = str(ppt_id)
    if not ppt_id.isdigit():
        raise ValueError(f"`ppt_id`` must be a digit, but '{ppt_id}' was provided")
    if not repeat_id:
        return ppt_id
    repeat_id = str(repeat_id)
    if not repeat_id.isdigit():
        raise ValueError(
            f"`repeat_id`` must be a digit, but '{repeat_id}' was provided"
        )
    return ppt_id + ":" + repeat_id


def get_participant(ppt_id: str) -> Participant:
    """Get participant record.

    Args:
        ppt_id: ID of participant (record_id).

    Returns:
        Participant: Participant object.
    """  # pylint: disable=line-too-long
    fields = {
        "content": "record",
        "action": "export",
        "format": "json",
        "type": "flat",
        "csvDelimiter": "",
        "records[0]": ppt_id,
        "rawOrLabel": "raw",
        "rawOrLabelHeaders": "raw",
        "exportCheckboxLabel": "false",
        "exportSurveyFields": "false",
        "exportDataAccessGroups": "false",
        "returnFormat": "json",
    }
    for i, f in enumerate(["participants", "appointments", "language"]):
        fields[f"forms[{i}]"] = f
    recs = [str_to_dt(r) for r in post_request(fields).json()]
    apt, que = {}, {}
    for r in recs:
        repeat_id = make_id(r["record_id"], r["redcap_repeat_instance"])
        if r["redcap_repeat_instrument"] == "appointments":
            apt[repeat_id] = Appointment(r)
        if r["redcap_repeat_instrument"] == "language":
            que[repeat_id] = Questionnaire(r)
    try:
        return Participant(
            recs[0],
            apt=RecordList(apt, kind="appointments"),
            que=RecordList(que, kind="questionnaires"),
        )
    except IndexError as e:
        raise MissingRecord(f"Record {ppt_id} not found") from e


def get_appointment(apt_id: str) -> Appointment:
    """Get appointment record.

    Args:
        apt_id (str): ID of appointment (``redcap_repeated_id``).

    Returns:
        Appointment: Appointment object.
    """  # pylint: disable=line-too-long
    ppt_id, _ = apt_id.split(":")
    ppt = get_participant(ppt_id)
    try:
        return ppt.appointments.records[apt_id]
    except KeyError as e:
        raise MissingRecord(f"Record {apt_id} not found") from e


def get_questionnaire(que_id: str) -> Questionnaire:
    """Get questionnaire record.

    Args:
        que_id (str): ID of appointment (``redcap_repeated_id``).

    Returns:
        Questionnaire: Appointment object.
    """  # pylint: disable=line-too-long
    ppt_id, _ = que_id.split(":")
    ppt = get_participant(ppt_id)
    try:
        return ppt.questionnaires.records[que_id]
    except KeyError as e:
        raise MissingRecord(f"Record {que_id} not found") from e


def add_participant(data: dict, modifying: bool = False):
    """Add new participant to REDCap database.

    Args:
        data (dict): Participant data.
        modifying (bool, optional): Modifying existent participant?
    """  # pylint: disable=line-too-long
    fields = {
        "content": "record",
        "action": "import",
        "format": "json",
        "type": "flat",
        "overwriteBehavior": "normal" if modifying else "overwrite",
        "forceAutoNumber": "false" if modifying else "true",
        "data": f"[{dumps(dt_to_str(data))}]",
    }
    return post_request(fields=fields)


def delete_participant(data: dict):
    """Delete participant from REDCap database.

    Args:
        data (dict): Participant data.
        modifying (bool, optional): Modifying existent participant?
    """  # pylint: disable=line-too-long
    fields = {
        "content": "record",
        "action": "delete",
        "returnFormat": "json",
        "instrument": "",
        "records[0]": f"{data['record_id']}",
    }
    r = post_request(fields=fields)
    try:
        r.raise_for_status()
        return r
    except requests.exceptions.HTTPError as e:
        rid = make_id(data["record_id"])
        raise MissingRecord(f"Record {rid} not found") from e


def add_appointment(data: dict):
    """Add new appointment to REDCap database.

    Args:
        record_id (dict): ID of participant.
        data (dict): Appointment data.
    """  # pylint: disable=line-too-long
    fields = {
        "content": "record",
        "action": "import",
        "format": "json",
        "type": "flat",
        "overwriteBehavior": "overwrite",
        "forceAutoNumber": "false",
        "data": f"[{dumps(dt_to_str(data))}]",
    }
    return post_request(fields=fields)


def delete_appointment(data: dict):
    """Delete appointment from REDCap database.

    Args:
        data (dict): Participant data.
        modifying (bool, optional): Modifying existent participant?
    """  # pylint: disable=line-too-long
    fields = {
        "content": "record",
        "action": "delete",
        "returnFormat": "json",
        "instrument": "appointments",
        "repeat_instance": int(data["redcap_repeat_instance"]),
        f"records[{data['record_id']}]": f"{data['record_id']}",
    }
    r = post_request(fields=fields)
    warn_missing_record(r)
    return r


def add_questionnaire(data: dict):
    """Add new questionnaire to REDCap database.

    Args:
        data (dict): Questionnaire data.
    """  # pylint: disable=line-too-long
    fields = {
        "content": "record",
        "action": "import",
        "format": "json",
        "type": "flat",
        "overwriteBehavior": "overwrite",
        "forceAutoNumber": "false",
        "data": f"[{dumps(dt_to_str(data))}]",
    }
    return post_request(fields=fields)


def delete_questionnaire(data: dict):
    """Delete questionnaire from REDCap database.

    Args:
        data (dict): Participant data.
        modifying (bool, optional): Modifying existent participant?
    """  # pylint: disable=line-too-long
    fields = {
        "content": "record",
        "action": "delete",
        "returnFormat": "json",
        "instrument": "language",
        "repeat_instance": int(data["redcap_repeat_instance"]),
        f"records[{data['record_id']}]": f"{data['record_id']}",
    }
    r = post_request(fields=fields)
    warn_missing_record(r)
    return r


def warn_missing_record(r: requests.models.Response):
    """Warn user about absent record.

    Args:
        r (requests.models.Response): HTTPS response.
    """  # pylint: disable=line-too-long
    if "registros proporcionados no existen" in r.content.decode():
        warn("Record does not exist!")


def redcap_backup(path: str = "tmp") -> dict:
    """Download a backup of the REDCap database

    Args:
        path (str, optional): Output directory. Defaults to "tmp".

    Returns:
        dict: A dictionary with the key data and metadata of the project.
    """  # pylint: disable=line-too-long
    if not exists(path):
        mkdir(path)
    pl = {}
    for k in ["project", "metadata", "instrument"]:
        pl[k] = {"format": "json", "returnFormat": "json", "content": k}
    d = {k: loads(post_request(v).text) for k, v in pl.items()}
    with open(join(path, "records.csv"), "w+", encoding="utf-8") as f:
        fields = {
            "content": "record",
            "action": "export",
            "format": "csv",
            "csvDelimiter": ",",
            "returnFormat": "json",
        }
        records = post_request(fields).content.decode().split("\n")
        records = [r + "\n" for r in records]
        f.writelines(records)

    b = {
        "project": d["project"],
        "instruments": d["instrument"],
        "fields": d["metadata"],
    }
    for k, v in b.items():
        with open(join(path, k + ".json"), "w", encoding="utf-8") as f:
            dump(v, f)
    timestamp = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%M")
    file = join(path, "backup_" + timestamp + ".zip")
    for root, _, files in walk(path, topdown=False):
        with ZipFile(file, "w", ZIP_DEFLATED) as z:
            for f in files:
                z.write(join(root, f))
    return file


class Records:
    """REDCap records"""

    def __init__(self, record_id: str | list = None):
        records = get_records(record_id)
        ppt, apt, que = {}, {}, {}
        for r in records:
            ppt_id = r["record_id"]
            repeat_id = r["redcap_repeat_instance"]
            if repeat_id and r["appointment_status"]:
                r["appointment_id"] = make_id(ppt_id, repeat_id)
                apt[r["appointment_id"]] = Appointment(r)
            if repeat_id and r["language_lang1"]:
                r["questionnaire_id"] = make_id(ppt_id, repeat_id)
                que[r["questionnaire_id"]] = Questionnaire(r)
            if not r["redcap_repeat_instrument"]:
                ppt[ppt_id] = Participant(r)

        # add appointments and questionnaires to each participant
        for p, v in ppt.items():
            apts = {k: v for k, v in apt.items() if v.record_id == p}
            v.appointments = RecordList(apts, kind="appointments")
            ques = {k: v for k, v in que.items() if v.record_id == p}
            v.questionnaires = RecordList(ques, kind="questionnaires")

        self.participants = RecordList(ppt, kind="participants")
        self.appointments = RecordList(apt, kind="appointments")
        self.questionnaires = RecordList(que, kind="questionnaires")

    def __repr__(self) -> str:
        return (
            "REDCap database:"
            + f"\n- {len(self.participants.records)} participants"
            + f"\n- {len(self.appointments.records)} appointments"
            + f"\n- {len(self.questionnaires.records)} questionnaires"
        )

    def __str__(self) -> str:
        return (
            "REDCap database:"
            + f"\n- {len(self.participants.records)} participants"
            + f"\n- {len(self.appointments.records)} appointments"
            + f"\n- {len(self.questionnaires.records)} questionnaires"
        )


def parse_age(age: tuple) -> tuple[int, int]:
    """Validate age string or tuple.

    Args:
        age (tuple): Age of the participant as a tuple in the ``(months, days)`` format.

    Raises:
        ValueError: If age is not str or tuple.
        BadAgeFormat: If age is ill-formatted.

    Returns:
        tuple[int, int]: Age of the participant in the ``(months, days)`` format.
    """  # pylint: disable=line-too-long
    try:
        assert isinstance(age, tuple)
        assert len(age) == 2
        return int(age[0]), int(age[1])
    except AssertionError as e:
        raise BadAgeFormat("age must be in (months, age) format") from e


def parse_str_date(x: str) -> datetime:
    """Parse string data to datetime.

    Args:
        x (str): String date to parse.

    Returns:
        datetime: Parsed datetime.
    """
    try:
        return datetime.strptime(x, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.strptime(x, "%Y-%m-%d %H:%M")


def get_age(age: str | tuple, ts: datetime | str, ts_new: datetime = None):
    """Calculate the age of a person in months and days at a new timestamp.

    Args:
        age (tuple): Age in months and days as a tuple of type (months, days).
        ts (datetime | str): Birth date as ``datetime.datetime`` type.
        ts_new (datetime.datetime, optional): Time for which the age is calculated. Defaults to current date (``datetime.datetime.now()``).

    Returns:
        tuple: Age in at ``new_timestamp``.
    """  # pylint: disable=line-too-long
    ts = parse_str_date(ts) if isinstance(ts, str) else ts
    ts_new = datetime.now(utc) if ts_new is None else ts_new

    if ts.tzinfo is None or ts.tzinfo.utcoffset(ts) is None:
        ts = utc.localize(ts, True)
    if ts_new.tzinfo is None or ts_new.tzinfo.utcoffset(ts_new) is None:
        ts_new = utc.localize(ts_new, True)

    tdiff = rdelta(ts_new, ts)
    months, days = parse_age(age)
    new_age_months = months + tdiff.years * 12 + tdiff.months
    new_age_days = days + tdiff.days

    if new_age_days >= 30:
        additional_months = new_age_days // 30
        new_age_months += additional_months
        new_age_days %= 30

    return new_age_months, new_age_days
