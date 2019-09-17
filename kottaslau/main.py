from models.Instance import Instance
from models.Task import Task
from util.InstanceBuilder import *

# import data
with open('../data/instance.json', 'r') as f:
    instance = json.load(f, cls=Decoder)

instance.execute_algorithm()
instance.log_result()

# output results
with open('../data/out.json', 'w') as f:
    json.dump(instance, fp=f, cls=Encoder)
