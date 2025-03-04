from typing import Tuple
import numpy as np


class LocationError(Exception):
    """
    Problem creating a location...
    """


class LocationPoint:

    def __init__(self, location: Tuple[float, float], page: int, item: int, date_and_time: str, index: int):

        self.location = location if location != (None, None) else (0, 0)
        try:
            self.page = int(page)
            self.item = int(item)
        except Exception as e:
            self.page = None
            self.item = None
        self.date_and_time = date_and_time
        self.index = int(index)
        self.z_dist = None
        self.tower_jump = None
        self.accuracy = None
        self.cluster_avg = None

    def __str__(self):
        return f"Location: {self.location} \n Date_and_time: {self.date_and_time} \n Page: {self.page} \n Item: {self.item} \n Z_dist: {self.z_dist} \n Tower_jump: {self.tower_jump} \n Accuracy: {self.accuracy} \n Cluster AVG: {self.cluster_avg})"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {
            "index": self.index,
            "page": self.page,
            "item": self.item,
            "date_and_time": self.date_and_time,
            "tower_jump": self.tower_jump,
            "accuracy": "{:.2f}".format(float(self.accuracy)),
        }

    @staticmethod
    def from_row(input):
        lat = input["Latitude"]
        lon = input["Longitude"]
        if isinstance(lat, np.float64):
            lat = float(lat)
        if isinstance(lon, np.float64):
            lon = float(lon)
        return LocationPoint(
            (lat, lon), input["Page Number"], input["Item Number"], input["Local Date & Time"], input["index"]
        )
