from collections.abc import Collection
from urllib.parse import quote_plus

from terminusgps.wialon import constants, flags
from terminusgps.wialon.items.base import WialonBase


class WialonResource(WialonBase):
    """A Wialon `resource/account <https://help.wialon.com/en/wialon-hosting/user-guide/management-system/accounts-and-resources>`_."""

    def __init__(self, *args, **kwargs) -> None:
        """Sets :py:attr:`_is_account` to :py:obj:`None`."""
        super().__init__(*args, **kwargs)
        self._is_account = None

    def create(
        self, creator_id: str | int, name: str, skip_creator_check: bool = False
    ) -> int | None:
        """
        Creates a new Wialon resource.

        :param creator_id: Creator user id.
        :type creator_id: :py:obj:`str` | :py:obj:`int`
        :param name: A name for the resource.
        :type name: :py:obj:`str`
        :param skip_creator_check: Bypass object creation restrictions while creating the resource.
        :type skip_creator_check: :py:obj:`bool`
        :raises ValueError: If ``creator_id`` wasn't a digit.
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: The Wialon id for the new resource, if it was created.
        :rtype: :py:obj:`int` | :py:obj:`None`

        """
        if isinstance(creator_id, str) and not creator_id.isdigit():
            raise ValueError(f"'creator_id' must be a digit, got '{creator_id}'.")

        response = self.session.wialon_api.core_create_resource(
            **{
                "creatorId": creator_id,
                "name": name,
                "dataFlags": flags.DataFlag.UNIT_BASE,
                "skipCreatorCheck": int(skip_creator_check),
            }
        )
        return (
            int(response.get("item", {}).get("id"))
            if response and response.get("item")
            else None
        )

    def delete(self) -> None:
        """
        Deletes all micro-objects assigned to the resource.

        If the resource is an account, instead deletes all macro-objects and micro-objects assigned to the account.

        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.delete_account() if self.is_account else super().delete()

    def get_remaining_days(self) -> int:
        """Returns the remaining account days for the resource."""
        if not self.is_account:
            return 0
        return int(
            self.session.wialon_api.account_get_account_data(
                **{"itemId": self.id, "type": 1}
            ).get("daysCounter", 0)
        )

    @property
    def is_dealer(self) -> bool:
        """
        Whether or not the resource/account has dealer rights.

        If the resource is **not** an account, this always returns :py:obj:`False`.

        :type: :py:obj:`bool`

        """
        return (
            bool(
                self.session.wialon_api.account_get_account_data(
                    **{"itemId": self.id, "type": 1}
                ).get("dealerRights")
            )
            if self.is_account
            else False
        )

    @property
    def is_account(self) -> bool:
        """
        Whether or not the resource is an account.

        :type: :py:obj:`bool`

        """
        if self._is_account is None:
            response = self.session.wialon_api.core_search_item(
                **{"id": self.id, "flags": flags.DataFlag.RESOURCE_BILLING_PROPERTIES}
            )
            self._is_account = int(response.get("item", {}).get("bact", 0)) == self.id
        return self._is_account

    @property
    def creator_id(self) -> int | None:
        """
        The account user id, if the resource is an account.

        :type: :py:obj:`int` | :py:obj:`None`

        """
        if self.is_account:
            response = self.session.wialon_api.core_search_item(
                **{"id": self.id, "flags": flags.DataFlag.RESOURCE_BILLING_PROPERTIES}
            )
            return int(response.get("item", {}).get("crt"))

    def create_geofence(
        self,
        name: str,
        x: float,
        y: float,
        _type: constants.WialonGeofenceType = constants.WialonGeofenceType.CIRCLE,
        desc: str = "",
        flags: int = 0x10,
        color: int = int("6d0204", 16),
        text_color: int = int("21130d", 16),
        text_size: int = 12,
        width: int = 100,
        min_zoom: int = 4,
        max_zoom: int = 19,
    ) -> None:
        """
        Creates a geofence in Wialon for the resource.

        :param name: Name of the geofence.
        :type name: :py:obj:`str`
        :param x: X-coordinate for the geofence.
        :type x: :py:obj:`float`
        :param y: Y-coordinate for the geofence.
        :type y: :py:obj:`float`
        :param _type: *Optional.* Type of Wialon geofence.
        :type _type: :py:obj:`int`
        :param desc: *Optional.* Description of the geofence.
        :type desc: :py:obj:`str`
        :param flags: *Optional.* Flags to use on the creation API call.
        :type flags: :py:obj:`int`
        :param color: *Optional.* Color of the geofence.
        :type color: :py:obj:`int`
        :param text_color: *Optional.* Text color of the geofence.
        :type text_color: :py:obj:`int`
        :param text_size: *Optional.* Text size of the geofence.
        :type text_size: :py:obj:`int`
        :param width: *Optional.* Width of the geofence.
        :type width: :py:obj:`int`
        :param min_zoom: *Optional.* Minimum zoom level the geofence will be visible at.
        :type min_zoom: :py:obj:`int`
        :param max_zoom: *Optional* Maximum zoom level the geofence will be visible at.
        :type max_zoom: :py:obj:`int`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.resource_update_zone(
            **{
                "itemId": self.id,
                "id": 0,
                "callMode": "create",
                "n": name,
                "d": desc,
                "t": _type,
                "w": width,
                "f": flags,
                "c": color,
                "tc": text_color,
                "ts": text_size,
                "min": min_zoom,
                "max": max_zoom,
                "path": "",
                "libId": 0,
                "p": [{"x": x, "y": y, "r": width}],
            }
        )

    def is_migrated(self, unit: WialonBase) -> bool:
        """
        Checks if a unit is migrated into the account.

        If the resource isn't an account, this always returns :py:obj:`False`.

        :param unit: A Wialon object.
        :type unit: :py:obj:`~terminusgps.wialon.items.base.WialonBase`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Whether or not the unit is migrated into the account.
        :rtype: :py:obj:`bool`

        """
        if not self.is_account:
            return False
        response = self.session.wialon_api.account_list_change_accounts(
            **{"units": [unit.id]}
        )
        return any([self.id == int(item.get("id")) for item in response])

    def set_dealer_rights(self, enabled: bool = False) -> None:
        """
        Sets dealer rights on the account.

        You **probably don't** need to use this method.

        :param enabled: Whether or not to enable dealer rights on the account. Default is :py:obj:`False`.
        :type enabled: :py:obj:`bool`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.is_account:
            self.session.wialon_api.account_update_dealer_rights(
                **{"itemId": self.id, "enable": str(enabled).lower()}
            )

    def migrate_unit(self, unit: WialonBase) -> None:
        """
        Migrates a :py:obj:`WialonUnit` into the account.

        :param unit: A Wialon object.
        :type unit: :py:obj:`~terminusgps.wialon.items.base.WialonBase`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.is_account:
            self.session.wialon_api.user_update_item_access(
                **{
                    "userId": self.creator_id,
                    "itemId": unit.id,
                    "accessMask": constants.ACCESSMASK_UNIT_MIGRATION,
                }
            )
            self.session.wialon_api.account_change_account(
                **{"itemId": unit.id, "resourceId": self.id}
            )

    def update_plan(self, new_plan: str) -> None:
        """
        Updates the account billing plan.

        :param new_plan: The name of a billing plan.
        :type new_plan: :py:obj:`str`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.is_account:
            self.session.wialon_api.account_update_plan(
                **{"itemId": self.id, "plan": new_plan}
            )

    def create_account(self, billing_plan: str) -> None:
        """
        Transforms the resource into an account.

        :param billing_plan: The name of a billing plan.
        :type billing_plan: :py:obj:`str`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if not self.is_account:
            self.session.wialon_api.account_create_account(
                **{"itemId": self.id, "plan": billing_plan}
            )
            self.set_settings_flags()
            self._is_account = True

    def delete_account(self) -> None:
        """
        Deletes the account if it exists, as well as any micro-objects and macro-objects it contains.

        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.is_account:
            self.session.wialon_api.account_delete_account(**{"itemId": self.id})
            self._is_account = False

    def enable_account(self) -> None:
        """
        Enables the Wialon account.

        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.is_account:
            self.session.wialon_api.account_enable_account(
                **{"itemId": self.id, "enable": int(True)}
            )

    def disable_account(self) -> None:
        """
        Disables the Wialon account.

        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.is_account:
            self.session.wialon_api.account_enable_account(
                **{"itemId": self.id, "enable": int(False)}
            )

    def set_minimum_days(self, days: int = 0) -> None:
        """
        Sets the minimum days counter value to ``days``.

        :param days: Number of days to set the counter to. Default is ``0``.
        :type days: :py:obj:`int`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.is_account:
            self.session.wialon_api.account_update_min_days(
                **{"itemId": self.id, "minDays": days}
            )

    def add_days(self, days: int = 30) -> None:
        """
        Adds days to the account.

        :param days: Number of days to add to the account. Default is ``30``.
        :type days: :py:obj:`int`
        :raises AssertionError: If the resource is not an account.
        :raises WialonError: If something goes wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.is_account:
            self.session.wialon_api.account_do_payment(
                **{
                    "itemId": self.id,
                    "balanceUpdate": "0.00",
                    "daysUpdate": days,
                    "description": f"{self.session.id} - Added {days} days.",
                }
            )

    def set_settings_flags(
        self,
        flags: int = 0x20,
        block_balance_val: float = 0.00,
        deny_balance_val: float = 0.00,
    ) -> None:
        """
        Sets account settings flags.

        :param flags: A flag integer to set on the account.
        :type flags: :py:obj:`int`
        :param block_balance_val: Minimum amount on the account's balance before blocking the account.
        :type block_balance_val: :py:obj:`float`
        :param deny_balance_val: Minimum amount on the account's balance before denying the account.
        :type deny_balance_val: :py:obj:`float`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.is_account:
            self.session.wialon_api.account_update_flags(
                **{
                    "itemId": self.id,
                    "flags": flags,
                    "blockBalance": block_balance_val,
                    "denyBalance": deny_balance_val,
                }
            )

    def bind_unit_driver(self, unit_id: int, driver_id: int) -> None:
        self.session.wialon_api.resource_bind_unit_driver(
            **{
                "resourceId": self.id,
                "unitId": unit_id,
                "driverId": driver_id,
                "time": 0,
                "mode": 1,  # Assign driver
            }
        )

    def unbind_unit_driver(self, unit_id: int, driver_id: int) -> None:
        self.session.wialon_api.resource_bind_unit_driver(
            **{
                "resourceId": self.id,
                "unitId": unit_id,
                "driverId": driver_id,
                "time": 0,
                "mode": 0,  # Separate driver
            }
        )

    def create_driver(
        self,
        name: str,
        code: str = "",
        desc: str = "",
        phone: str = "",
        mobile_auth_code: str = "",
        custom_fields: dict[str, str] | None = None,
    ) -> int | None:
        """
        Creates a driver for the resource and returns its id.

        :param name: A name for the new driver.
        :type name: :py:obj:`str`
        :param code: A unique code for the new driver.
        :type code: :py:obj:`str`
        :param desc: Description for the driver.
        :type desc: :py:obj:`str`
        :param phone: A phone number in `E.164 <https://en.wikipedia.org/wiki/E.164>`_ format.
        :type phone: :py:obj:`str`
        :param mobile_auth_code: Authentication code for Wialon mobile app.
        :type mobile_auth_code: :py:obj:`str`
        :param custom_fields: Additional custom fields to add to the driver.
        :type custom_fields: :py:obj:`dict` | :py:obj:`None`
        :returns: The driver id, if created.
        :rtype: :py:obj:`int` | :py:obj:`None`

        """
        params = {
            "itemId": self.id,
            "id": 0,
            "callMode": "create",
            "c": code,
            "ds": desc,
            "ej": {"apps": []},
            "f": 1,
            "n": name,
            "p": quote_plus(phone) if phone else phone,
            "pwd": mobile_auth_code,
        }

        if custom_fields:
            params.update({"jp": custom_fields})
        response = self.session.wialon_api.resource_update_driver(**params)
        if not response:
            return
        return response[0]

    def create_passenger(
        self,
        name: str,
        code: str,
        phone: str = "",
        custom_fields: dict[str, str] | None = None,
    ) -> None:
        """
        Creates a passenger/tag for the resource.

        :param name: A name for the new passenger.
        :type name: :py:obj:`str`
        :param code: A unique code for the new passenger.
        :type code: :py:obj:`str`
        :param phone: A phone number in `E.164 <https://en.wikipedia.org/wiki/E.164>`_ format.
        :type phone: :py:obj:`str`
        :param custom_fields: Additional custom fields to add to the passenger.
        :type custom_fields: :py:obj:`dict` | :py:obj:`None`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        params = {
            "itemId": self.id,
            "id": 0,
            "callMode": "create",
            "c": code,
            "n": name,
        }
        if phone:
            params.update({"p": quote_plus(phone)})
        if custom_fields:
            params.update({"jp": custom_fields})
        self.session.wialon_api.resource_update_tag(**params)

    def update_attachable_drivers(self, units: Collection[str | int]) -> None:
        """
        Updates the pool of units for the resource to attach drivers to the new unit list.

        :param units: A collection of unit ids.
        :type units: :py:obj:`~collections.abc.Collection`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.update_driver_units(
            **{"itemId": self.id, "units": units}
        )

    def update_attachable_passengers(self, units: Collection[str | int]) -> None:
        """
        Updates the pool of units for the resource to attach passengers to the new unit list.

        :param units: A collection of unit ids.
        :type units: :py:obj:`~collections.abc.Collection`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.update_tag_units(**{"itemId": self.id, "units": units})

    def create_trailer(
        self,
        name: str,
        code: str,
        desc: str = "",
        phone: str = "",
        custom_fields: dict[str, str] | None = None,
    ) -> None:
        """
        Creates a trailer for the resource.

        :param name: A name for the new trailer.
        :type name: :py:obj:`str`
        :param code: A unique code for the new trailer.
        :type code: :py:obj:`str`
        :param desc: A description for the trailer.
        :type desc: :py:obj:`str`
        :param phone: A phone number in `E.164 <https://en.wikipedia.org/wiki/E.164>`_ format.
        :type phone: :py:obj:`str`
        :param custom_fields: Additional custom fields to add to the trailer.
        :type custom_fields: :py:obj:`dict` | :py:obj:`None`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        params = {
            "itemId": self.id,
            "id": 0,
            "callMode": "create",
            "c": code,
            "ds": desc,
            "n": name,
            "f": 1,
        }
        if phone:
            params.update({"p": quote_plus(phone)})
        if custom_fields:
            params.update({"jp": custom_fields})
        self.session.wialon_api.resource_update_trailer(**params)
