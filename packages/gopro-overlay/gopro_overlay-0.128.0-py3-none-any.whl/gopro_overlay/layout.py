from typing import Callable

from PIL import ImageFont, Image, ImageDraw

from gopro_overlay.widgets.info import ComparativeEnergy
from .framemeta import FrameMeta
from .layout_components import moving_map
from .point import Coordinate
from .units import units
from .widgets.text import CachingText, Text
from .widgets.widgets import Scene, Translate, Composite, Widget


def gps_info(at, entry, font):
    return Composite(
        CachingText(at + Coordinate(0, 0), lambda: "GPS INFO", font, align="right"),
        Text(at + Coordinate(-130, 24), lambda: f"Lat: {entry().point.lat:0.6f}", font, align="right"),
        Text(at + Coordinate(0, 24), lambda: f"Lon: {entry().point.lon:0.6f}", font, align="right"),
    )


def time(clock):
    return lambda: clock().strftime("%H:%M:%S.%f")[:-5]


def date(clock):
    return lambda: clock().strftime("%Y/%m/%d")


def date_and_time(at, entry, font_title, font_metric):
    return Composite(
        CachingText(at + Coordinate(0, 0), date(lambda: entry().dt), font_title, align="right"),
        Text(at + Coordinate(0, 24), time(lambda: entry().dt), font_metric, align="right"),
    )


class BigMetric(Widget):

    def __init__(self, at, title, value, font_title, font_metric=None):
        self.widget = Translate(
            at,
            Composite(
                CachingText(Coordinate(0, 0), title, font_title),
                CachingText(Coordinate(0, 0), value, font_metric),
            )
        )

    def draw(self, image: Image, draw: ImageDraw):
        self.widget.draw(image, draw)


def big_mph(at, entry, font_title, font_metric=None):
    if font_metric is None:
        font_metric = font_title.font_variant(size=160)

    return Composite(
        BigMetric(
            at,
            lambda: "MPH",
            lambda: f"{entry().speed.to('MPH').magnitude:.0f}" if entry().speed else "-",
            font_title=font_title,
            font_metric=font_metric
        )
    )


def speed_awareness_layout(renderer, font: ImageFont):
    def create(entry):
        font_title = font.font_variant(size=16)
        font_metric = font.font_variant(size=32)

        return [
            date_and_time(Coordinate(260, 30), entry, font_title, font_metric),
            gps_info(Coordinate(1900, 36), entry, font_title),
            big_mph(Coordinate(16, 800), entry, font_title),
            moving_map(Coordinate(1900 - 384, 100), entry, size=384, zoom=16, renderer=renderer),
            Translate(
                Coordinate(450, 850),
                ComparativeEnergy(
                    font=font_title,
                    speed=lambda: entry().speed,
                    person=units.Quantity(84, units.kg),
                    bike=units.Quantity(12, units.kg),
                    car=units.Quantity(2000, units.kg),
                    van=units.Quantity(3500, units.kg)
                )
            )
        ]

    return create


class Overlay:

    def __init__(self, framemeta: FrameMeta, create_widgets: Callable):
        self.scene = Scene(create_widgets(self.entry))
        self.framemeta = framemeta
        self._entry = None

    def entry(self):
        return self._entry

    def draw(self, pts, image: Image.Image) -> Image.Image:
        self._entry = self.framemeta.get(pts)
        return self.scene.draw(image)
