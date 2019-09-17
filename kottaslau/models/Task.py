from typing import Set

class Task:
    """
    Class used to represent a single  task in the production process

    ...

    Attributes
    ----------
    task_id : str
        task's unique id
    m : float
        mean of the task's execution time (time unit coherent with other parameters, e.g. minutes)
    s : float
        variance of the task's execution time (time unit coherent with other parameters, e.g. minutes)
    out_line_cost : float
        task's completition cost outside the assembly line (in general, higher than the in-line cost) [€/pc]
    predecessor_set : Set[str]
        set of tasks that to complete before the task (with a direct relation in the operation process chart)
    out_completion_cost : float
        completition cost outside the assembly line of the task and all the following tasks (according with the operation process chart)
    in_line_cost : float
        task's completition cost in a station (computed from mean execution time and the station cost)
    z_limit : float
        task's normalized execution time limit that solves: inline_cost = out_completion_cost*P with P the probability of missed complition of the task
    n_successors : int
        number of tasks that depend on the task according with the operation process chart
    """
    def __init__(self, task_id: str, m: float, s: float, out_line_cost: float, predecessor_set: Set[str]):
        self.task_id = task_id
        self.m = m
        self.s = s
        self.predecessor_set = predecessor_set
        self.out_line_cost = out_line_cost
        self.out_completion_cost = None
        self.in_line_cost = None
        self.z_limit = None
        self.n_successors = None