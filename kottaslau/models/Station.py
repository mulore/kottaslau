from models.Task import Task

class Station:
    """
    Class used to represent a single station to which tasks are assigned.

    ...

    Attributes
    ----------
    station_id : str
        station's unique id
    out_line_cost : Dict[str, float]
        for each task in the station, saved the out-line completition cost (based on out-line completition probability)
    """
    def __init__(self, station_id: str):
        self.station_id = station_id
        self.out_line_cost = dict() # Dict[str, float]
