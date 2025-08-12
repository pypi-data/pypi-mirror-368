

import glasswall
from glasswall.content_management.policies.policy import Policy


class Editor(Policy):
    """ A content management policy for Editor."""

    def __init__(self, default: str = "sanitise", config: dict = {}):
        self.default = default
        self.default_config_elements = [
            glasswall.content_management.config_elements.gifConfig(default=default),
            glasswall.content_management.config_elements.jpegConfig(default=default),
            glasswall.content_management.config_elements.pdfConfig(default=default),
            glasswall.content_management.config_elements.pptConfig(default=default),
            glasswall.content_management.config_elements.svgConfig(default=default),
            glasswall.content_management.config_elements.sysConfig(),
            glasswall.content_management.config_elements.tiffConfig(default=default),
            glasswall.content_management.config_elements.webpConfig(default=default),
            glasswall.content_management.config_elements.wordConfig(default=default),
            glasswall.content_management.config_elements.xlsConfig(default=default),
        ]
        self.config = config or {}

        super().__init__(
            default=self.default,
            default_config_elements=self.default_config_elements,
            config=self.config,
        )
