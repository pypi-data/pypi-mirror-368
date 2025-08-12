from enum import IntFlag


class DayBetterLightFeatures(IntFlag):
    """daybetter Lights capabilities."""

    COLOR_RGB = 0x01
    COLOR_KELVIN_TEMPERATURE = 0x02
    BRIGHTNESS = 0x04
    SEGMENT_CONTROL = 0x08
    SCENES = 0x10


COMMON_FEATURES: DayBetterLightFeatures = (
    DayBetterLightFeatures.COLOR_RGB
    | DayBetterLightFeatures.COLOR_KELVIN_TEMPERATURE
    | DayBetterLightFeatures.BRIGHTNESS
)


class DayBetterLightCapabilities:
    def __init__(
        self,
        features: DayBetterLightFeatures,
        segments: list[bytes] = [],
        scenes: dict[str, bytes] = {},
    ) -> None:
        self.features = features
        self.segments = (
            segments if features & DayBetterLightFeatures.SEGMENT_CONTROL else []
        )
        self.scenes = scenes if features & DayBetterLightFeatures.SCENES else {}

    @property
    def segments_count(self) -> int:
        return len(self.segments)

    @property
    def available_scenes(self) -> list[str]:
        return list(self.scenes.keys())

    def __repr__(self) -> str:
        return f"DayBetterLightCapabilities(features={self.features!r}, segments={self.segments!r}, scenes={self.scenes!r})"

    def __str__(self) -> str:
        return f"DayBetterLightCapabilities(features={self.features!r}, segments={len(self.segments)}, scenes={len(self.scenes)})"


SEGMENT_CODES: list[bytes] = [
    b"\x01\x00",  # 1
    b"\x02\x00",  # 2
    b"\x04\x00",  # 3
    b"\x08\x00",  # 4
    b"\x10\x00",  # 5
    b"\x20\x00",  # 6
    b"\x40\x00",  # 7
    b"\x80\x00",  # 8
    b"\x00\x01",  # 9
    b"\x00\x02",  # 10
    b"\x00\x04",  # 11
    b"\x00\x08",  # 12
    b"\x00\x10",  # 13
    b"\x00\x20",  # 14
    b"\x00\x40",  # 15
    b"\x00\x80",  # 16
    b"\x01\x01",  # 17
    b"\x02\x02",  # 18
    b"\x04\x04",  # 19
    b"\x08\x08",  # 20
]

SCENE_CODES: dict[str, bytes] = {
    "christmas": b"\x01\x22",
    "halloween": b"\x01\x2C",
    "carnival": b"\x01\x2d",
    "fathery": b"\x01\x23",
    "mothers": b"\x01\x24",
    "lover": b"\x01\x25"
}


def create_with_capabilities(
    rgb: bool, temperature: bool, brightness: bool, segments: int, scenes: bool
) -> DayBetterLightCapabilities:
    features: DayBetterLightFeatures = DayBetterLightFeatures(0)
    segments_codes = []

    if rgb:
        features = features | DayBetterLightFeatures.COLOR_RGB
    if temperature:
        features = features | DayBetterLightFeatures.COLOR_KELVIN_TEMPERATURE
    if brightness:
        features = features | DayBetterLightFeatures.BRIGHTNESS
    if segments > 0:
        features = features | DayBetterLightFeatures.SEGMENT_CONTROL
        segments_codes = SEGMENT_CODES[:segments]

    if scenes:
        features = features | DayBetterLightFeatures.SCENES

    return DayBetterLightCapabilities(
        features, segments_codes, SCENE_CODES if scenes else {}
    )


BASIC_CAPABILITIES = create_with_capabilities(
    rgb=True, temperature=True, brightness=True, segments=0, scenes=True
)

ON_OFF_CAPABILITIES = create_with_capabilities(
    rgb=False, temperature=False, brightness=False, segments=0, scenes=False
)


daybetter_LIGHT_CAPABILITIES: dict[str, DayBetterLightCapabilities] = {
    # Models with common features
    # "P076": BASIC_CAPABILITIES,
    "P076": create_with_capabilities(True, True, True, 20, False),   
}
