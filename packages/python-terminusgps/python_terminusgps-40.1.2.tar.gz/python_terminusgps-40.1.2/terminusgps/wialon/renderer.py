import datetime
import secrets
import sys
import typing

from .session import WialonSession


class WialonMapRenderer:
    def __init__(self, session: WialonSession) -> None:
        self.session = session
        self.layers = {}

    def create_messages_layer(
        self,
        name: str,
        unit_id: int | str,
        time_from: datetime.datetime,
        time_to: datetime.datetime,
        enable_trip_detector: bool = False,
        enable_directional_arrows: bool = False,
        enable_points: bool = False,
        enable_annotations: bool = False,
        track_color: str = "FFFF0000",
        point_color: str = "7F00FF00",
        track_width: int = 12,
        flags: int = 0x0004,
    ) -> dict[str, typing.Any]:
        """
        Creates a messages layer and adds it to the renderer.

        :param name: Name of the new messages layer.
        :type name: :py:obj:`str`
        :param unit_id: A Wialon unit id to retrieve messages for.
        :type unit_id: :py:obj:`int` | :py:obj:`str`
        :param time_from: Start time for the messages interval.
        :type time_from: :py:obj:`~datetime.datetime`
        :param time_to: End time for the messages interval.
        :type time_to: :py:obj:`~datetime.datetime`
        :param enable_trip_detector: Whether or not to enable the trip detector on the layer. Default is :py:obj:`False`.
        :type enable_trip_detector: :py:obj:`bool`
        :param enable_directional_arrows: Whether or not to enable directional arrows on the layer. Default is :py:obj:`False`.
        :type enable_directional_arrows: :py:obj:`bool`
        :param enable_points: Whether or not to enable points of interest on the layer. Default is :py:obj:`False`.
        :type enable_points: :py:obj:`bool`
        :param enable_annotations: Whether or not to annotate the points of interest on the layer. Default is :py:obj:`False`.
        :type enable_annotations: :py:obj:`bool`
        :param track_color: ARGB color to use for the track on the layer. Default is :py:obj:`"FFFF0000"`.
        :type track_color: :py:obj:`str`
        :param point_color: ARGB color to use for the points of interest on the layer. Default is :py:obj:`"7F00FF00"`.
        :type point_color: :py:obj:`str`
        :param track_width: Width (in pixels) of the track on the layer. Default is :py:obj:`12`.
        :type track_width: :py:obj:`int`
        :param flags: Determines which points of interest will be rendered on the layer. Default is :py:obj:`0x0004`.
        :type flags: :py:obj:`int`
        :returns: A Wialon API response.
        :rtype: :py:obj:`dict`

        """
        response = self.session.wialon_api.render_create_messages_layer(
            **{
                "layerName": name,
                "itemId": int(unit_id),
                "timeFrom": time_from.timestamp(),
                "timeTo": time_to.timestamp(),
                "tripDetector": int(enable_trip_detector),
                "trackColor": "trip" if enable_trip_detector else track_color,
                "trackWidth": track_width,
                "arrows": int(enable_directional_arrows),
                "points": int(enable_points),
                "pointColor": point_color,
                "annotations": int(enable_annotations),
                "flags": flags,
            }
        )
        self.layers.setdefault(name, {"enabled": False})
        return response if response else {}

    def enable_layer(self, name: str) -> None:
        """
        Enables a layer by name in the renderer.

        :param name: A layer name.
        :type name: :py:obj:`str`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if not self.layers[name]["enabled"]:
            self.session.wialon_api.render_enable_layer(
                **{"layerName": name, "enable": int(True)}
            )
            self.layers[name]["enabled"] = True

    def disable_layer(self, name: str) -> None:
        """
        Disables a layer by name in the renderer.

        :param name: A layer name.
        :type name: :py:obj:`str`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        if self.layers[name]["enabled"]:
            self.session.wialon_api.render_enable_layer(
                **{"layerName": name, "enable": int(False)}
            )
            self.layers[name]["enabled"] = False

    def remove_layer(self, name: str) -> None:
        """
        Removes a layer by name in the renderer.

        :param name: A layer name.
        :type name: :py:obj:`str`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.session.wialon_api.render_remove_layer(**{"layerName": name})
        self.layers.pop(name)

    def set_locale(
        self,
        timezone: int,
        lang: str = "en",
        flags: int = 1,
        date_format: str = "%Y-%m-%E %H:%M:%S",
        density: int = 1,
    ) -> None:
        """
        Updates the locale options for the renderer.

        :param timezone: Timezone offset to use in the renderer.
        :type timezone: :py:obj:`int`
        :param lang: A 2-character language code. Default is :py:obj:`"en"`.
        :type lang: :py:obj:`str`
        :param flags: Measurement system to use in the renderer.
        :type flags: :py:obj:`int`
        :param date_format: Format to use for dates in the renderer.
        :type date_format: :py:obj:`str`
        :param density: Tile density to use in the renderer.
        :type density: :py:obj:`int`

        Flag options:

        +-------------+--------------+
        | value       | measurement  |
        +=============+==============+
        | :py:obj:`0` | Metric       |
        +-------------+--------------+
        | :py:obj:`1` | US           |
        +-------------+--------------+
        | :py:obj:`2` | Imperial     |
        +-------------+--------------+

        Density options:

        +-------------+-----------+-------+
        | value       | tile size | ratio |
        +=============+===========+=======+
        | :py:obj:`1` | 256*256   | 1     |
        +-------------+-----------+-------+
        | :py:obj:`2` | 378*378   | 1.5   |
        +-------------+-----------+-------+
        | :py:obj:`3` | 512*512   | 2     |
        +-------------+-----------+-------+
        | :py:obj:`4` | 768*768   | 3     |
        +-------------+-----------+-------+
        | :py:obj:`5` | 1024*1024 | 4     |
        +-------------+-----------+-------+

        """
        self.session.wialon_api.render_set_locale(
            **{
                "tzOffset": timezone,
                "language": lang,
                "flags": flags,
                "formatDate": date_format,
                "density": density,
            }
        )

    def generate_render_url(self, x: int, y: int, z: int) -> str:
        sid = self.session.id
        random_num = secrets.SystemRandom(sid).randint(1, sys.maxsize)
        return f"https://hst-api.wialon.com/adfurl{random_num}/avl_render/{x}_{y}_{z}/{sid}.png"
