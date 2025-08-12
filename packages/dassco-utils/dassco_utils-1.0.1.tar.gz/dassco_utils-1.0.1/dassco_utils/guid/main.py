import random
from datetime import datetime

def padding(value: str, length: int) -> str:
    """
    Supplies a string with a padding of leading zeros to a specified length
    :param value: the string to be padded
    :param length: number of digits to be shown
    :return: modified string with leading zeros
    """
    return value[2:].zfill(length)

def get_components(year, month, day, hour, minute, second, microsecond, random_number, constant) -> list[str]:
    components = [
            constant,
            padding(year, 3),
            padding(month, 1),
            padding(day, 2),
            padding(hour, 2),
            padding(minute, 2),
            padding(second, 2),
            padding(microsecond, 3),
            padding(random_number, 6)
        ]
    return components

def create_guid_list(institution_name: str, request_amount: int = 1) -> list[str]:
    list_of_guids = []

    for r in range(request_amount):
        guid = create_guid(institution_name)
        list_of_guids.append(guid)
    
    return list_of_guids

def create_guid(constant: str) -> str:
    """
    Create a unique guid.
    :param constant: added to the guid
    :return: a unique guid
    """
    now = datetime.now()

    year = hex(now.year)
    month = hex(now.month)
    day = hex(now.day)
    hour = hex(now.hour)
    minute = hex(now.minute)
    second = hex(now.second)
    microsecond = hex(now.microsecond//1000)
    random_number = hex(random.randint(0, 15999999))

    components = get_components(year, month, day, hour, minute, second, microsecond, random_number, constant)

    guid = ''.join(components)
    return guid

# This is the old way of creating GUIDs, kept for reference
def create_old_version_guid(mapping: dict, date_str: str, institution_name: str, collection_name: str,
                workstation_name: str) -> str:
    """
    Creates a unique ID according to the following specs:
    [date created]-[institution]-[collection]-[workstation]-[random number]-[unreserved digits]
    :param mapping: input mapping to get the values of the specific institution, collection and workstation.

        Example of the structure of the mapping:

        {
            "institution": {
                "NHMD": 0,
                "AU": 1,
            },
            "collection": {
                "Vascular plants": 0,
                "Entomology": 1
            },
            "workstation": {
                "WORKHERB0001": 0,
                "WORKHERB0002": 1,
            },
        }

    :param date_str: date the image was taken
    :param institution_name: the institution where the image was taken
    :param collection_name: the collection the image is part of
    :param workstation_name: the workstation the image was taken on
    :return: a unique GUID
    """

    institution = hex(mapping["institution"][institution_name])
    collection = hex(mapping["collection"][collection_name])
    workstation = hex(mapping["workstation"][workstation_name])

    year = hex(int(date_str[:4]))
    month = hex(int(date_str[5:7]))
    day = hex(int(date_str[8:10]))
    hour = hex(int(date_str[11:13]))
    minute = hex(int(date_str[14:16]))
    second = hex(int(date_str[17:19]))
    random_number = hex(random.randint(0, 999999))
    derivative = hex(0)
    future_use = hex(0)

    components = [
        padding(year, 3),
        padding(month, 1),
        padding(day, 2),
        padding(hour, 2),
        padding(minute, 2),
        padding(second, 2),
        padding(institution, 1),
        padding(collection, 3),
        padding(workstation, 2),
        padding(derivative, 3),
        padding(random_number, 6),
        padding(future_use, 5)
    ]
    return '-'.join(components)

# This is the old way of creating GUIDs for derivatives, kept for reference
def create_old_version_derivative_guid(guid: str, derivative_number: int) -> str:
    """
    Creates a GUID for derivatives from the existing GUID of the parent asset. Only works if the parent guid is not derived as well.
    :param guid: the GUID of the parent asset
    :param derivative_number: the derivative number
    :return: a unique GUID
    """
    parts = guid.split('-')

    if parts[9] != "000":
        raise ValueError("GUID indicates that the image is already a derivative")

    parts[9] = padding(hex(derivative_number), 3)

    new_guid = '-'.join(parts)

    return new_guid
