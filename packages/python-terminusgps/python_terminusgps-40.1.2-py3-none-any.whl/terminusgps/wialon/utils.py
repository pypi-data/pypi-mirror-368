import secrets
import string
import typing

from . import constants, flags
from .items import WialonResource, WialonUnit
from .session import WialonSession


def get_hw_types(session: WialonSession) -> list[dict[str, str | int]]:
    """
    Returns a list of hardware type objects for Wialon.

    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :returns: A list of hardware types.
    :rtype: :py:obj:`list`

    Hardware type format:

    +----------+--------------------+
    | key      | value              |
    +==========+====================+
    | ``id``   | Hardware type id   |
    +----------+--------------------+
    | ``name`` | Hardware type name |
    +----------+--------------------+

    """
    return session.wialon_api.core_get_hw_types()


def get_user_by_name(name: str, session: WialonSession) -> WialonUnit | None:
    """
    Returns a Wialon user by name, if it exists.

    :param name: A Wialon user name.
    :type name: :py:obj:`str`
    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :returns: A Wialon unit, if any.
    :rtype: :py:obj:`~terminusgps.wialon.items.unit.WialonUnit` | :py:obj:`None`

    """
    results: dict = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": constants.WialonItemsType.USER,
                "propName": constants.WialonItemProperty.NAME,
                "propValueMask": name,
                "sortType": constants.WialonItemProperty.NAME,
            },
            "force": 0,
            "flags": flags.DataFlag.USER_BASE,
            "from": 0,
            "to": 0,
        }
    )
    if results and results.get("items", [{}]):
        return WialonUnit(id=results.get("items", [{}])[0].get("id"), session=session)


def get_carrier_names(session: WialonSession) -> list[str]:
    """
    Returns a list of all telecommunication carrier company names present in Wialon.

    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :returns: A list of telecommunication carrier company names.
    :rtype: :py:obj:`list`

    """
    afname: str = constants.WialonItemProperty.ADMIN_FIELD_NAME
    afval: str = constants.WialonItemProperty.ADMIN_FIELD_VALUE
    results: dict = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": constants.WialonItemsType.UNIT,
                "propName": ",".join([afname, afval]),
                "propValueMask": "carrier,*",
                "sortType": ",".join([afname, afval]),
            },
            "force": 0,
            "flags": flags.DataFlag.UNIT_BASE + flags.DataFlag.UNIT_ADMIN_FIELDS,
            "from": 0,
            "to": 0,
        }
    )
    carrier_names: list[str] = [
        field["v"]
        for item in results.get("items", [{}])
        for field in item.get("aflds", {}).values()
        if field["n"] == "carrier" and field["v"]
    ]
    return sorted(list(frozenset(carrier_names)))


def get_units_by_carrier(
    carrier_name: str, session: WialonSession
) -> list[WialonUnit] | None:
    """
    Returns a list of all units by telecommunications carrier company name.

    :param carrier_name: A telecommunications carrier company name, e.g. ``"US Cell"`` or ``"Conetixx"``.
    :type carrier_name: :py:obj:`str`
    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :returns: A list of units, if any were found.
    :rtype: :py:obj:`list`

    """
    results = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_unit",
                "propName": constants.WialonItemProperty.ADMIN_FIELD_NAME_VALUE,
                "propValueMask": f"carrier:{carrier_name}",
                "sortType": constants.WialonItemProperty.ADMIN_FIELD_NAME_VALUE,
            },
            "force": 0,
            "flags": flags.DataFlag.UNIT_BASE,
            "from": 0,
            "to": 0,
        }
    )
    if results:
        return [
            WialonUnit(id=item.get("id"), session=session)
            for item in results.get("items", [])
        ]


def get_unit_by_iccid(iccid: str, session: WialonSession) -> WialonUnit | None:
    """
    Returns a unit by iccid (SIM card #).

    :param iccid: A SIM card #.
    :type iccid: :py:obj:`str`
    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :returns: The unit, if it was found.
    :rtype: :py:obj:`~terminusgps.wialon.items.WialonUnit` | :py:obj:`None`

    """
    results = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_unit",
                "propName": constants.WialonItemProperty.ADMIN_FIELD_NAME_VALUE,
                "propValueMask": f"iccid:{iccid}",
                "sortType": constants.WialonItemProperty.ADMIN_FIELD_NAME_VALUE,
            },
            "force": 0,
            "flags": flags.DataFlag.UNIT_BASE,
            "from": 0,
            "to": 0,
        }
    )
    if results and results.get("totalItemsCount") == 1:
        return WialonUnit(id=results["items"][0]["id"], session=session)


def get_resources(session: WialonSession) -> list[WialonResource] | None:
    """
    Returns a list of all resources in Wialon.

    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :returns: A list of resources, if found.
    :rtype: :py:obj:`list` | :py:obj:`None`

    """
    results = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_resource",
                "propName": "sys_id",
                "propValueMask": "*",
                "sortType": "sys_id",
                "propType": "property",
                "or_logic": False,
            },
            "force": 0,
            "flags": 1,
            "from": 0,
            "to": 0,
        }
    )
    if results:
        return [
            WialonResource(id=item.get("id"), session=session)
            for item in results.get("items", [])
        ]


def get_hw_type_id(name: str, session: WialonSession) -> int | None:
    """
    Takes a Wialon hardware type name and returns its id, if it exists.

    :param name: The name of a Wialon hardware type.
    :type name: :py:obj:`str`
    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :raises WialonError: If something goes wrong during a Wialon API call.
    :returns: A Wialon hardware type id, if it was found.
    :rtype: :py:obj:`int` | :py:obj:`None`

    """
    response = session.wialon_api.core_get_hw_types(
        **{
            "filterType": "id",
            "filterValue": "name,id",
            "includeType": "true",
            "ignoreRename": "true",
        }
    )
    hw_types = {item.get("name"): item.get("id") for item in response}
    return int(hw_types.get(name)) if name in hw_types.keys() else None


def get_unit_by_imei(imei: str, session: WialonSession) -> WialonUnit | None:
    """
    Takes a Wialon unit's IMEI # and returns its unit id.

    :param imei: A Wialon unit's IMEI #.
    :type imei: :py:obj:`str`
    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :raises ValueError: If ``imei`` contains non-digit characters.
    :returns: A Wialon object id, if it was found.
    :rtype: :py:obj:`str` | :py:obj:`None`

    """
    if not imei.isdigit():
        raise ValueError(f"'imei' must be a digit, got '{imei}'.")

    results: dict[str, typing.Any] | None = session.wialon_api.core_search_items(
        **{
            "spec": {
                "itemsType": "avl_unit",
                "propName": "sys_unique_id",
                "propValueMask": imei,
                "sortType": "sys_unique_id",
                "propType": "property",
            },
            "force": 0,
            "flags": flags.DataFlag.UNIT_BASE,
            "from": 0,
            "to": 0,
        }
    )

    if results and results.get("totalItemsCount", 0) == 1:
        return WialonUnit(id=results["items"][0]["id"], session=session)


def get_vin_info(vin_number: str, session: WialonSession) -> dict[str, typing.Any]:
    """
    Retrieves vehicle data from a VIN number.

    :param value: A vehicle's VIN number.
    :type value: :py:obj:`str`
    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :returns: A dictionary of vehicle information, if any was found.
    :rtype: :py:obj:`dict`

    """
    response: dict[str, typing.Any] | None = session.wialon_api.unit_get_vin_info(
        **{"vin": vin_number}
    )

    if response is None or "error" in response.get("vin_lookup_result", {}).keys():
        return {}

    return {
        field.get("n"): field.get("v")
        for field in response.get("vin_lookup_result", {}).get("pflds")
    }


def is_unique(
    value: str,
    session: WialonSession,
    items_type: str = constants.WialonItemsType.UNIT.value,
) -> bool:
    """
    Determines if the value is unique among Wialon objects of type 'items_type'.

    :param value: A Wialon object name.
    :type value: :py:obj:`str`
    :param session: A valid Wialon API session.
    :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
    :param items_type: Type of Wialon objects to validate the value against. Default is ``"avl_unit"``.
    :type items_type: :py:obj:`str`
    :raises WialonError: If something goes wrong during a Wialon API call.
    :returns: Whether or not the value is unique among 'items_type'.
    :rtype: :py:obj:`bool`

    """
    response = session.wialon_api.core_check_unique(
        **{"type": items_type, "value": value.strip()}
    )
    return not bool(response.get("result")) if response else False


def generate_wialon_password(length: int = 32) -> str:
    """
    Generates a Wialon compliant password between ``8`` and ``64`` characters.

    The generated password will contain:

        - At least one uppercase letter.
        - At least one lowercase letter.
        - At least one special symbol.
        - At least three digits.

    :param length: Length of the generated password. Default is :py:obj:`32`.
    :type length: :py:obj:`int`
    :raises ValueError: If ``length`` is less than ``8`` or greater than ``64``.
    :returns: A Wialon compliant password.
    :rtype: :py:obj:`str`

    """
    min_length, max_length = 8, 64
    if length > max_length:
        raise ValueError(
            f"Password cannot be greater than {max_length} characters in length, got {length}."
        )
    elif length < min_length:
        raise ValueError(
            f"Password cannot be less than {min_length} characters in length, got {length}."
        )

    s0 = list(string.ascii_uppercase)
    s1 = list(string.ascii_lowercase)
    s2 = list(string.digits)
    s3 = list("!@#$%^*()[]-_+")

    while True:
        password = "".join([secrets.choice(s0 + s1 + s2 + s3) for _ in range(length)])
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= 3
            and any(c in s3 for c in password)
        ):
            break
    return password
