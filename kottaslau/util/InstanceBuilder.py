import json
from models.Task import Task
from models.Station import Station
from models.Instance import Instance

class Encoder(json.JSONEncoder):
    """
    Encodes a custom class to a JSON.
    Used to produce the output.
    """
    def default(self, obj):
        if isinstance(obj,  Task):
            return {'task_id': obj.task_id, 'm': obj.m, 's': obj.s, "out_line_cost": obj.out_line_cost, "predecessor_set": list(obj.predecessor_set)}
        elif isinstance(obj, Station):
            return {'station_id': obj.station_id, 'task_list': list(obj.out_line_cost.keys())}
        elif isinstance(obj, Instance):
            return {'instance_id': obj.instance_id, 'task_list': list(obj.task_list.values()), 'station_list': list(obj.station_list.values()), 'q': 1/obj.T, 'c': obj.c, "total_unit_cost": obj.total_unit_cost}
        else:
            print(obj)
            super().default(self, obj)


class Decoder(json.JSONDecoder):
    """
    Decodes a JSON into a custom class.
    Used to read the data.
    """
    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook)

    def object_hook(self, dct):
        if 'task_id' in dct:
            return Task(dct['task_id'], dct['m'], dct['s'], dct['out_line_cost'], set(dct['predecessor_set']))
        elif 'instance_id' in dct:
            return Instance(dct['instance_id'],{task.task_id: task for task in dct['task_list']}, dct['q'], dct['c'])
        else:
            super().object_hook(self, dct)
