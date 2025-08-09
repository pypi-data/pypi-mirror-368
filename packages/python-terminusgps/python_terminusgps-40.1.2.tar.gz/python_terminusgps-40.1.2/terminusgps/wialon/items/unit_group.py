from terminusgps.wialon import flags
from terminusgps.wialon.items.base import WialonBase


class WialonUnitGroup(WialonBase):
    """A Wialon `unit group <https://help.wialon.com/en/wialon-local/2504/user-guide/monitoring-system/units/unit-groups>`_."""

    def create(self, creator_id: str | int, name: str) -> int | None:
        """
        Creates a new Wialon unit group and returns its id.

        :param creator_id: Creator user id.
        :type creator_id: :py:obj:`str` | :py:obj:`int`
        :param name: Name for the new unit group.
        :type name: :py:obj:`str`
        :raises ValueError: If ``creator_id`` wasn't a digit.
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: A new Wialon unit group id, if created.
        :rtype: :py:obj:`int` | :py:obj:`None`

        """
        if isinstance(creator_id, str) and not creator_id.isdigit():
            raise ValueError(f"'creator_id' must be a digit, got '{creator_id}'.")

        response = self.session.wialon_api.core_create_unit_group(
            **{
                "creatorId": creator_id,
                "name": name,
                "dataFlags": flags.DataFlag.UNIT_BASE,
            }
        )
        return (
            int(response.get("item", {}).get("id"))
            if response and response.get("item")
            else None
        )

    def set_items(self, new_items: list[str]) -> None:
        """
        Sets this group's members to a list of Wialon unit ids.

        :param new_items: A list of Wialon unit ids.
        :type new_items: :py:obj:`list`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.unit_group_update_units(
            **{"itemId": self.id, "units": new_items}
        )

    def is_member(self, item: WialonBase) -> bool:
        """
        Determines whether or not ``item`` is a member of the group.

        :param item: A Wialon object.
        :type item: :py:obj:`~terminusgps.wialon.items.base.WialonBase`
        :raises ValueError: If ``item`` didn't have an :py:attr:`id` attribute.
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Whether or not ``item`` is a member of the group.
        :rtype: :py:obj:`bool`

        """
        if not hasattr(item, "id"):
            raise ValueError(f"'{item}' didn't have an id.")
        return True if item.id in self.items else False

    def add_item(self, item: WialonBase) -> None:
        """
        Adds a Wialon object to the group.

        :param item: A Wialon object.
        :type item: :py:obj:`~terminusgps.wialon.items.base.WialonBase`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        new_items: list[str] = self.items.copy() + [str(item.id)]
        self.set_items(new_items)

    def rm_item(self, item: WialonBase) -> None:
        """
        Removes a Wialon object from the group.

        :param item: A Wialon object.
        :type item: :py:obj:`~terminusgps.wialon.items.base.WialonBase`
        :raises AssertionError: If ``item`` wasn't a member of the group.
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        assert self.is_member(item), f"Cannot remove {item}, it's not in the group."
        new_items: list[str] = self.items.copy()
        new_items.remove(str(item.id))
        self.set_items(new_items)

    @property
    def items(self) -> list[str]:
        """
        Returns a list of Wialon object ids in the group.

        :type: :py:obj:`list`

        """
        response = self.session.wialon_api.core_search_items(
            **{
                "spec": {
                    "itemsType": "avl_unit_group",
                    "propName": "sys_id",
                    "propValueMask": str(self.id),
                    "sortType": "sys_id",
                    "propType": "property",
                    "or_logic": 0,
                },
                "force": 1,
                "flags": flags.DataFlag.UNIT_BASE.value,
                "from": 0,
                "to": 0,
            }
        )
        return [unit_id for unit_id in response.get("items")[0].get("u", [])]
