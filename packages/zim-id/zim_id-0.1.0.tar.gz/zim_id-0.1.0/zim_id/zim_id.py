"""Defines the `ZimID` class."""

import re
import random
from typing import Dict, Optional


class ZimID:
    """Represents a Zimbabwean national ID number."""

    REGEXP: re.Pattern = re.compile(
        r"^\s*"
        r"(?P<reg_office>\d\d)"
        r"\s*-?\s*"
        r"(?P<national_number>\d{6,7})"
        r"\s*"
        r"(?P<check_letter>\w)"
        r"\s*"
        r"(?P<origin_district>\d\d)"
        r"\s*$"
    )

    DISTRICT_CODES: Dict[str, str] = {
        "02": "Beitbridge",
        "03": "Mberengwa",
        "04": "Bikita",
        "05": "Bindura",
        "06": "Binga",
        "07": "Buhera",
        "08": "Bulawayo",
        "10": "Mhondoro-Ngezi",
        "11": "Muzarabani",
        "13": "Chipinge",
        "14": "Chiredzi",
        "15": "Mazowe",
        "18": "Chikomba",
        "19": "Umzingwane",
        "21": "Insiza",
        "22": "Masvingo",
        "23": "Gokwe South",
        "24": "Kadoma",
        "25": "Goromonzi",
        "26": "Gokwe North",
        "27": "Gutu",
        "28": "Gwanda",
        "29": "Gweru",
        "32": "Chegutu",
        "34": "Nyanga",
        "35": "Bubi",
        "37": "Kariba",
        "38": "Hurungwe",
        "39": "Matobo",
        "41": "Lupane",
        "42": "Makoni",
        "43": "Marondera",
        "44": "Chimanimani",
        "45": "Mt. Darwin",
        "46": "Mbire",
        "47": "Murehwa",
        "48": "Mutoko",
        "49": "Mudzi",
        "50": "Mutasa",
        "53": "Nkayi",
        "54": "Mwenezi",
        "56": "Bulilimamangwe",
        "58": "Kwekwe",
        "59": "Seke",
        "61": "Rushinga",
        "63": "Harare",
        "66": "Shurugwi",
        "67": "Zvishavane",
        "68": "Shamva",
        "70": "Makonde",
        "71": "Guruve",
        "73": "Tsholotsho",
        "75": "Mutare",
        "77": "Chirumanzu",
        "79": "Hwange",
        "80": "Hwedza",
        "83": "Zaka",
        "84": "Umguza",
        "85": "U.M.P. (Uzumba, Maramba, Pfungwe)",
        "86": "Zvimba",
    }

    FOREIGN_ORIGIN_CODE: str = "00"

    CHECK_LETTERS: str = "ZABCDEFGHJKLMNPQRSTVWXY"  # No I, O, U

    @classmethod
    def debug(cls, id_number: str) -> int:
        """Helps debug issues with a Zimbabwean national ID number."""
        match = re.match(cls.REGEXP, id_number)
        if not match:
            return 1

        reg_office = match["reg_office"]
        if reg_office not in cls.DISTRICT_CODES:
            return 2

        check_letter = match["check_letter"].upper()
        if check_letter not in cls.CHECK_LETTERS:
            return 3

        origin_district = match["origin_district"]
        if origin_district not in cls.DISTRICT_CODES and origin_district != cls.FOREIGN_ORIGIN_CODE:
            return 4

        national_number = match["national_number"]
        if check_letter != cls.CHECK_LETTERS[int(f"{reg_office}{national_number}") % 23]:
            return 5

        return 0

    @classmethod
    def validate(cls, id_number: str) -> bool:
        """Checks if a Zimbabwean national ID number is valid."""
        return cls.debug(id_number) == 0

    @classmethod
    def generate(
        cls, reg_office: Optional[str] = None, origin_district: Optional[str] = None
    ) -> str:
        """Generates a valid random/custom Zimbabwean national ID number."""
        if reg_office is not None:
            if isinstance(reg_office, str):
                reg_office = reg_office.strip()

            if reg_office not in cls.DISTRICT_CODES:
                raise ValueError(f"Unkown registration office '{reg_office}'. ")

        if origin_district is not None:
            if isinstance(origin_district, str):
                origin_district = origin_district.strip()

            if origin_district not in cls.DISTRICT_CODES:
                raise ValueError(f"Unkown district of origin '{origin_district}'. ")

        reg_office = reg_office or random.choice(tuple(cls.DISTRICT_CODES))
        origin_district = origin_district or random.choice(tuple(cls.DISTRICT_CODES))
        national_number = f"{random.randint(100000, 9999999)}"
        check_letter = cls.CHECK_LETTERS[int(f"{reg_office}{national_number}") % 23]
        return f"{reg_office}-{national_number}{check_letter}{origin_district}"
