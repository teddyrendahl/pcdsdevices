"""
PCDS plugins and Overrides for AreaDetector Plugins.
"""
import numpy as np
from ophyd.areadetector.plugins import *


class ImagePlugin(ophyd.plugins.ImagePlugin, PluginBase):

    # The issue that required the need for this plugin is solved in
    # https://github.com/NSLS-II/ophyd/pull/634. This can be removed after that PR
    # is merged and released
    @property
    def image(self):
        """
        Overriden image method to add in some corrections
        """
        array_size = self.array_size.get()
        if array_size == (0, 0, 0):
            raise RuntimeError('Invalid image; ensure array_callbacks are on')

        if array_size[-1] == 0:
            array_size = array_size[:-1]

        pixel_count = self.array_pixels
        image = self.array_data.get(count=pixel_count)
        return np.array(image).reshape(array_size)


# Skip plugin_type checks on this plugin, as old versions of AD did not
# reflect this correctly
NexusPlugin._plugin_type = None
