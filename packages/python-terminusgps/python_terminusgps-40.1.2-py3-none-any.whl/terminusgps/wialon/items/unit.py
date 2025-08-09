from datetime import datetime

from django.core.exceptions import ValidationError

from terminusgps.django.validators import validate_e164_phone_number
from terminusgps.wialon import flags
from terminusgps.wialon.items.base import WialonBase


class WialonUnit(WialonBase):
    """A Wialon `unit <https://help.wialon.com/en/wialon-hosting/user-guide/management-system/units>`_."""

    def __init__(self, *args, **kwargs) -> None:
        """Sets :py:attr:`_imei_number` and :py:attr:`_active` to :py:obj:`None`."""
        super().__init__(*args, **kwargs)
        self._imei_number = None
        self._active = None

    def create(
        self, creator_id: str | int, name: str, hw_type_id: str | int
    ) -> int | None:
        """
        Creates a new Wialon unit.

        :param creator_id: Creator user id.
        :type creator_id: :py:obj:`str` | :py:obj:`int`
        :param name: A name for the new unit.
        :type name: :py:obj:`str`
        :param hw_type_id: A Wialon hardware type id for the new unit.
        :type hw_type_id: :py:obj:`str` | :py:obj:`int`
        :raises ValueError: If ``creator_id`` isn't a digit.
        :raises ValueError: If ``hw_type_id`` isnt' a digit.
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: A new Wialon unit id, if created.
        :rtype: :py:obj:`int` | :py:obj:`None`

        """
        if isinstance(creator_id, str) and not creator_id.isdigit():
            raise ValueError(f"'creator_id' must be a digit, got '{creator_id}'.")
        if isinstance(hw_type_id, str) and not hw_type_id.isdigit():
            raise ValueError(f"'hw_type_id' must be a digit, got '{hw_type_id}'.")

        response = self.session.wialon_api.core_create_unit(
            **{
                "creatorId": str(creator_id),
                "name": str(name),
                "hwTypeId": str(hw_type_id),
                "dataFlags": flags.DataFlag.UNIT_BASE,
            }
        )
        return (
            int(response.get("item", {}).get("id"))
            if response and response.get("item")
            else None
        )

    def populate(self) -> None:
        """Sets :py:attr:`imei_number`, :py:attr:`active` and :py:attr:`image_uri`."""
        super().populate()
        response = self.session.wialon_api.core_search_item(
            **{
                "id": self.id,
                "flags": (
                    flags.DataFlag.UNIT_ADVANCED_PROPERTIES
                    | flags.DataFlag.UNIT_IMAGE
                    | flags.DataFlag.UNIT_ADMIN_FIELDS
                ).value,
            }
        )
        if response is not None:
            item = response.get("item", {})
            self._imei_number = item.get("uid")
            self._active = item.get("act", False)

    def get_position(self) -> dict:
        """
        Returns the current position of the unit.

        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: The unit's current position.
        :rtype: :py:obj:`dict`

        Response format:

        +----------+------------------------------+-----------------+
        | key      | type                         | desc            |
        +==========+==============================+=================+
        | ``"t"``  | :py:obj:`~datetime.datetime` | Time (UTC)      |
        +----------+------------------------------+-----------------+
        | ``"y"``  | :py:obj:`float`              | Latitude        |
        +----------+------------------------------+-----------------+
        | ``"x"``  | :py:obj:`float`              | Longitude       |
        +----------+------------------------------+-----------------+
        | ``"z"``  | :py:obj:`float`              | Altitude        |
        +----------+------------------------------+-----------------+
        | ``"s"``  | :py:obj:`int`                | Speed           |
        +----------+------------------------------+-----------------+
        | ``"c"``  | :py:obj:`int`                | Course          |
        +----------+------------------------------+-----------------+
        | ``"sc"`` | :py:obj:`int`                | # of satellites |
        +----------+------------------------------+-----------------+

        """
        response = (
            self.session.wialon_api.core_search_item(
                **{"id": self.id, "flags": flags.DataFlag.UNIT_POSITION}
            )
            .get("item", {})
            .get("pos", {})
        )
        if response:
            response["t"] = datetime.fromtimestamp(response["t"])
        return response

    def get_command_messages(
        self, start_time: datetime, total: int = 1, count: int = 1
    ) -> list[dict[str, str]]:
        return self.session.wialon_api.messages_load_last(
            **{
                "itemId": self.id,
                "lastTime": int(start_time.timestamp()),
                "flags": 0x0200,
                "flagsMask": 0,
                "lastCount": total,
                "loadCount": count,
            }
        )

    def execute_command(
        self,
        name: str,
        link_type: str,
        timeout: int = 5,
        flags: int = 0,
        param: dict | None = None,
    ) -> None:
        """
        Executes a command on the unit.

        :param name: A Wialon command name.
        :type name: :py:obj:`str`
        :param link_type: A protocol to use for the Wialon command.
        :type link_type: :py:obj:`str`
        :param timeout: How long (in seconds) to wait before timing out command execution. Default is ``5``.
        :type timeout: :py:obj:`int`
        :param flags: Flags to pass to the Wialon command execution.
        :type flags: :py:obj:`int`
        :param param: Additional parameters to execute the command with.
        :type param: :py:obj:`dict` | :py:obj:`None`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.unit_exec_cmd(
            **{
                "itemId": self.id,
                "commandName": name,
                "linkType": link_type,
                "timeout": timeout,
                "flags": flags,
                "param": param if param else {},
            }
        )

    def set_access_password(self, password: str) -> None:
        """
        Sets the unit's access password.

        :param password: A new access password.
        :type password: :py:obj:`str`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.unit_update_access_password(
            **{"itemId": self.id, "accessPassword": password}
        )

    def activate(self) -> None:
        """
        Activates the unit.

        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.unit_set_active(
            **{"itemId": self.id, "active": int(True)}
        )

    def deactivate(self) -> None:
        """
        Deactivates the unit.

        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.unit_set_active(
            **{"itemId": self.id, "active": int(False)}
        )

    def get_phone_numbers(
        self, cfield_key: str = "to_number", afield_key: str = "to_number"
    ) -> list[str]:
        """
        Retrieves all phone numbers assigned to the unit.

        This includes any attached drivers, custom/admin fields or otherwise assigned phone numbers.

        :param cfield_key: A custom field key used to retrieve phone numbers. Default is :py:obj:`"to_number"`.
        :type cfield_key: :py:obj:`str`
        :param afield_key: An admin field key used to retrieve phone numbers. Default is :py:obj:`"to_number"`.
        :type afield_key: :py:obj:`str`
        :raises WialonError: If something goes wrong with Wialon.
        :returns: A list of phone numbers.
        :rtype: :py:obj:`list`

        """
        phones_0: list[str] = self._get_driver_phone_numbers()
        phones_1: list[str] = self._get_cfield_phone_numbers(key=cfield_key)
        phones_2: list[str] = self._get_afield_phone_numbers(key=afield_key)

        return [
            phone
            for phone in list(frozenset(phones_0 + phones_1 + phones_2))
            if self._validate_phone_number(phone)
        ]

    def _validate_phone_number(self, phone: str) -> bool:
        """Returns :py:obj:`True` if ``phone`` is a valid E.164 formatted phone number."""
        try:
            validate_e164_phone_number(phone)
            return True
        except ValidationError:
            return False

    def _get_afield_phone_numbers(self, key: str) -> list[str]:
        """
        Retrives phone numbers saved in an admin field by key.

        :param key: An admin field key.
        :type key: :py:obj:`str`
        :raises WialonError: If something goes wrong with Wialon.
        :returns: A list of phone numbers.
        :rtype: :py:obj:`list`

        """
        if key not in self.afields.keys():
            return []

        afield_val = self.afields[key]
        return afield_val.split(",") if "," in afield_val else [afield_val]

    def _get_cfield_phone_numbers(self, key: str) -> list[str]:
        """
        Retrives phone numbers saved in a custom field by key.

        :param key: A custom field key.
        :type key: :py:obj:`str`
        :raises WialonError: If something goes wrong with Wialon.
        :returns: A list of phone numbers.
        :rtype: :py:obj:`list`

        """
        if key not in self.cfields.keys():
            return []

        cfield_val = self.cfields[key]
        return cfield_val.split(",") if "," in cfield_val else [cfield_val]

    def _get_driver_phone_numbers(self) -> list[str]:
        """
        Returns a list of phone numbers assigned to drivers attached to the unit.

        :raises WialonError: If something goes wrong with Wialon.
        :returns: A list of phone numbers.
        :rtype: :py:obj:`list`

        """
        response = self.session.wialon_api.resource_get_unit_drivers(
            **{"unitId": self.id}
        )
        if not response:
            return []

        return [driver[0].get("ph") for driver in response.values()]

    @property
    def exists(self) -> bool:
        """Whether or not the unit exists in Wialon."""
        return bool(
            self.session.wialon_api.core_search_item(
                **{"id": self.id, "flags": flags.DataFlag.UNIT_BASE}
            ).get("item", False)
        )

    @property
    def available_commands(self) -> dict:
        """
        Commands assigned to the unit.

        :type: :py:obj:`dict`

        """
        return (
            self.session.wialon_api.core_search_item(
                **{"id": self.id, "flags": flags.DataFlag.UNIT_AVAILABLE_COMMANDS}
            )
            .get("item", {})
            .get("cml", {})
        )

    @property
    def imei_number(self) -> str:
        """
        IMEI # for the unit.

        :type: :py:obj:`str`

        """
        if self._imei_number is None:
            self.populate()
        return str(self._imei_number)

    @property
    def iccid(self) -> str | None:
        """
        SIM Card # for the unit, if any.

        :type: :py:obj:`str` | :py:obj:`None`

        """
        return self.afields.get("iccid")

    @property
    def carrier(self) -> str | None:
        """
        Name of the telecommunications company associated with the unit's SIM card, if any.

        :type: :py:obj:`str` | :py:obj:`None`

        """
        return self.afields.get("carrier")

    @property
    def active(self) -> bool:
        """Whether or not the unit is activated."""
        if self._active is None:
            self.populate()
        return bool(self._active)
