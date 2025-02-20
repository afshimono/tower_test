from typing import Tuple
import numpy as np
class LocationPoint:
    def __init__(self, location:Tuple[float,float], page:int, item:int, date_and_time:str):
        self.location = location
        self.page = page
        self.item = item
        self.date_and_time = date_and_time
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
            "page":self.page,
            "item":self.item,
            "date_and_time":self.date_and_time,
            "tower_jump": self.tower_jump,
            "accuracy": "{:.2f}".format(float(self.accuracy))
        }

    @staticmethod
    def from_row(input):
        lat = input["Latitude"]
        lon = input["Longitude"]
        if isinstance(lat, np.float64):
            lat = float(lat)
        if isinstance(lon, np.float64):
            lon = float(lon)
        return LocationPoint((lat,lon),input["Page Number"],input["Item Number"],input["Local Date & Time"])