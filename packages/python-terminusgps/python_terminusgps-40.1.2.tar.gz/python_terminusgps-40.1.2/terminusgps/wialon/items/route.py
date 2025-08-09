from terminusgps.wialon import flags
from terminusgps.wialon.items.base import WialonBase


class WialonRoute(WialonBase):
    """A Wialon `route <https://help.wialon.com/en/wialon-hosting/user-guide/monitoring-system/routes>`_."""

    def create(self, creator_id: str | int, name: str) -> int | None:
        """
        Creates a new Wialon route.

        :param creator_id: A Wialon user id.
        :type creator_id: :py:obj:`str` | :py:obj:`int`
        :param name: A name for the route.
        :type name: :py:obj:`str`
        :raises ValueError: If ``creator_id`` is not a digit.
        :raises WialonError: If something goes wrong with Wialon.
        :returns: The Wialon id for the new route, if it was created.
        :rtype: :py:obj:`int` | :py:obj:`None`

        """
        if isinstance(creator_id, str) and not creator_id.isdigit():
            raise ValueError(f"'creator_id' must be a digit, got '{creator_id}'.")

        response = self.session.wialon_api.core_create_route(
            **{
                "creatorId": creator_id,
                "name": name,
                "dataFlags": flags.DataFlag.ROUTE_BASE.value,
            }
        )
        return (
            int(response.get("item", {}).get("id"))
            if response and response.get("item")
            else None
        )
