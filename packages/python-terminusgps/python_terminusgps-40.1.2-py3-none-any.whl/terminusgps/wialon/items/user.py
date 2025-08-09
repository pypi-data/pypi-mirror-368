from terminusgps.wialon import constants, flags
from terminusgps.wialon.items.base import WialonBase


class WialonUser(WialonBase):
    """A Wialon `user <https://help.wialon.com/en/wialon-hosting/user-guide/management-system/users>`_."""

    def create(self, creator_id: str | int, name: str, password: str) -> int | None:
        """
        Creates a new Wialon user.

        :param creator_id: Creator user id.
        :type creator_id: :py:obj:`str` | :py:obj:`int`
        :param name: Name for the new user.
        :type name: :py:obj:`str`
        :param password: Password for the new user.
        :type password: :py:obj:`str`
        :raises ValueError: If ``creator_id`` wasn't a digit.
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: A new Wialon user id, if created.
        :rtype: :py:obj:`int` | :py:obj:`None`

        """
        if isinstance(creator_id, str) and not creator_id.isdigit():
            raise ValueError(f"'creator_id' must be a digit, got '{creator_id}'.")

        response = self.session.wialon_api.core_create_user(
            **{
                "creatorId": str(creator_id),
                "name": name,
                "password": password,
                "dataFlags": flags.DataFlag.UNIT_BASE,
            }
        )
        return (
            int(response.get("item", {}).get("id"))
            if response and response.get("item")
            else None
        )

    def grant_access(
        self, item: WialonBase, access_mask: int = constants.ACCESSMASK_UNIT_BASIC
    ) -> None:
        """
        Grants the user access to ``item``.

        :param item: A Wialon object.
        :type item: :py:obj:`~terminusgps.wialon.items.base.WialonBase`
        :param access_mask: A Wialon access mask integer. Default is :py:obj:`~terminusgps.wialon.constants.ACCESSMASK_UNIT_BASIC`
        :type access_mask: :py:obj:`int`
        :raises ValueError: If ``item`` didn't have an :py:attr:`id` attribute.
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if not hasattr(item, "id"):
            raise ValueError(f"'{item}' doesn't have an id.")

        self.session.wialon_api.user_update_item_access(
            **{"userId": self.id, "itemId": item.id, "accessMask": access_mask}
        )

    def set_settings_flags(self, flags: int, mask: int) -> None:
        """
        Sets the user's settings flags.

        :param flags: A user settings flag integer.
        :type flags: :py:obj:`int`
        :param mask: A user settings flag mask.
        :type mask: :py:obj:`int`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.user_update_user_flags(
            **{"userId": self.id, "flags": flags, "flagsMask": mask}
        )

    def reset_password(self, email: str, url: str) -> None:
        """
        Sends a password reset email for a user to ``email``.

        :param email: An email address.
        :type email: :py:obj:`str`
        :param url: A password reset URL.
        :type url: :py:obj:`str`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.core_reset_password_request(
            **{"user": self.name, "url": url, "email": email}
        )

    def update_password(self, old_password: str, new_password: str) -> None:
        """
        Updates the user's password.

        :param old_password: The user's original password.
        :type old_password: :py:obj:`str`
        :param new_password: A new password.
        :type new_password: :py:obj:`str`
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.user_update_password(
            **{
                "userId": self.id,
                "oldPassword": old_password,
                "newPassword": new_password,
            }
        )

    def verify_auth(self, destination: str, method: str = "email") -> str:
        """
        Sends an authentication code to ``destination`` via ``method``.

        Destination should be an email address or an `E.164 <https://en.wikipedia.org/wiki/E.164>`_ format phone number.

        Method can be ``"email"`` or ``"sms"``.

        :param destination: The email or phone number to send an auth code to.
        :type destination: :py:obj:`str`
        :param method: Authentication method to use. Default is ``"email"``.
        :type method: :py:obj:`str`
        :raises ValueError: If the authentication method wasn't ``"email"`` or ``"sms"``.
        :raises WialonError: If something went wrong with a Wialon API call.
        :returns: An auth code string.
        :rtype: :py:obj:`str`

        """
        if method != "email" or "sms":
            raise ValueError(f"Invalid method '{method}'.")

        return self.session.wialon_api.user_verify_auth(
            **{
                "userId": self.id,
                "type": 1 if method == "email" else 0,
                "destination": destination,
            }
        ).get("code", "")
