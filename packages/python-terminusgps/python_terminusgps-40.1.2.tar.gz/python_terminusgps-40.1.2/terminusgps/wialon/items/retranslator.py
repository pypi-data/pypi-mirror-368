from terminusgps.wialon import flags
from terminusgps.wialon.items.base import WialonBase


class WialonRetranslator(WialonBase):
    """A Wialon `retranslator <https://wialon.com/en/gps-hardware/soft>`_."""

    def create(self, creator_id: str | int, name: str, config: dict) -> int | None:
        """
        Creates a Wialon retranslator.

        :param creator_id: Creator user id.
        :type creator_id: :py:obj:`str` | :py:obj:`int`
        :param name: A name for the retranslator.
        :type name: :py:obj:`str`
        :param config: A Wialon retranslator configuration object.
        :type config: :py:obj:`dict`
        :raises ValueError: If a required parameter was not provided.
        :raises WialonError: If something went wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if isinstance(creator_id, str) and not creator_id.isdigit():
            raise ValueError(f"'creator_id' must be a digit, got '{creator_id}'.")

        response = self.session.wialon_api.core_create_retranslator(
            **{
                "creatorId": creator_id,
                "name": name,
                "config": config,
                "dataFlags": flags.DataFlag.UNIT_BASE.value,
            }
        )
        return (
            int(response.get("item", {}).get("id"))
            if response and response.get("item")
            else None
        )

    def update_config(self, new_config: dict) -> None:
        """
        Updates the retranslator config to the new config.

        :param new_config: A Wialon retranslator configuration.
        :type units: :py:obj:`dict`
        :raises WialonError: If something went wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.retranslator_update_config(
            **{"itemId": self.id, "config": new_config}
        )

    def add_units(self, units: list[WialonBase]) -> None:
        """
        Adds a list of units to the Wialon retranslator.

        :param units: A list of Wialon unit objects.
        :type units: :py:obj:`list`
        :raises WialonError: If something went wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.retranslator_update_units(
            **{
                "itemId": self.id,
                "units": [{"a": unit.id, "i": unit.hw_type} for unit in units],
                "callMode": "add",
            }
        )

    def rm_units(self, units: list[WialonBase]) -> None:
        """

        Naively removes a list of units from the Wialon retranslator.

        :param units: A list of Wialon unit objects.
        :type units: :py:obj:`list`
        :raises WialonError: If something went wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.retranslator_update_units(
            **{
                "itemId": self.id,
                "units": [{"a": unit.id, "i": unit.hw_type} for unit in units],
                "callMode": "remove",
            }
        )

    def start(self, stop: int | None = None) -> None:
        """
        Starts the Wialon retranslator.

        :raises WialonError: If something went wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.retranslator_update_operating(
            **{"itemId": self.id, "operate": int(True), "stopTime": stop}
        )

    def stop(self) -> None:
        """
        Stops the Wialon retranslator.

        :raises WialonError: If something went wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.retranslator_update_operating(
            **{"itemId": self.id, "operate": int(False)}
        )
