import numpy as np


class HistogramContinue:
    def __init__(
        self,
        data: list | np.ndarray,
        bins: int | list | np.ndarray | None = None,
        bin_width: float | None = None,
    ):
        # raw data
        self.data = data
        self.bins = bins
        self.bin_width = bin_width

        # properties
        if bins is None and bin_width is None:
            self.bins = 10
        elif bins is not None and bin_width is not None:
            raise ValueError("Either bins or bin_width can be set")

        return None

    @property
    def bins(self):
        return self._bins

    @bins.setter
    def bins(self, value: int | list | np.ndarray):
        self._bins = value
        self._bin_width = None
        return None

    @property
    def bin_width(self):
        return self._bin_width

    @bin_width.setter
    def bin_width(self, value: float):
        self._bin_width = value
        self._bins = np.arange(
            min(self.data),
            max(self.data) + self.bin_width,
            self.bin_width,
        )
        return None

    def get_histogram(
        self,
        density: bool = False,
        percentage: bool = False,
    ) -> tuple[np.ndarray, np.ndarray]:
        if self.bins is None:
            raise ValueError("bins must be set")
        if density is False and percentage is True:
            raise ValueError("percentage can be set only if density is True")

        hist, bin_edges = np.histogram(
            self.data,
            bins=self.bins,
            density=density,
        )
        if percentage is True:
            hist = hist * 100
        return hist, bin_edges
