from functools import reduce
from math import sqrt
from typing import Dict, Set, Tuple

from scipy.stats import norm

from models.Task import Task
from models.Station import Station


class Instance():
    """
    Class used to represent a single instance containing all the problem's parameters.
    Run algorithm with execute_algorithm method.

    ...

    Attributes
    ----------
    instance_id : str
        instance's unique id
    task_list : Dict[str, Task]
        dictionary of tasks to be assigned to stations
    q : float
        line's target production rate [pc/time] (time unit coherent with other parameters, e.g. minutes)
    c : float
        station cost [€/time] (time unit coherent with other parameters, e.g. minutes)
    T : float
        line's target time to produce one unit (is the reciprocal of q)
    total_unit_cost : float
        unit cost of production computed by the algorithm
    """
    def __init__(self, instance_id: str, task_list: Dict[str, Task], q: float, c: float):
        self.instance_id = instance_id
        self.task_list = task_list
        self.station_list = dict()
        self.T = 1/q
        self.c = c
        self.total_unit_cost = 0

        self.fill_task_properties()

    def successors_of(self, task_id: str) -> Set[str]:
        """
        For a given task, returns all the following tasks according with the operation process chart.

        Parameters
        ----------
        task_id : str
            the task's unique id 

        Returns
        -------
        set
            a set of tasks (unique IDs)
        """
        successors = set()
        for key, task in self.task_list.items():
            if task_id in task.predecessor_set: successors.add(key)

        return successors

    def deep_first_search(self, start_task_id: str, visited_tasks_id: Set[str] = None) -> Set[str]:
        """
        For a given task, recursive function that returns all the following tasks untill the last according to the operation process chart paths.

        Parameters
        ----------
        start_task_id : str
            the task's unique id
        visited_tasks_id : Set[str]
            current set of tasks that follow the starting task

        Returns
        -------
        set
            a set of tasks (unique IDs)
        """
        if visited_tasks_id is None:
            visited_tasks_id = set()

        visited_tasks_id.add(start_task_id)
        
        for task_id in self.successors_of(start_task_id).difference(visited_tasks_id):
            self.deep_first_search(task_id, visited_tasks_id)

        return visited_tasks_id

    def assigned_tasks(self) -> Set[str]:
        """
        Set of the already assigned task to stations.

        Returns
        -------
        set
            a set of tasks (unique IDs)
        """
        ass_tasks = set()
        for station in self.station_list.values():
            tasks_id = set(station.out_line_cost.keys())
            if len(tasks_id) == 0:
                continue
            else:   
                ass_tasks.update(tasks_id)
        return ass_tasks

    def task_out_line_completion_cost(self, task_id: str) -> float:
        """
        Method that computes the task's out_completion_cost as the sum of the out_line_cost
        of the following tasks according to the operation process chart.

        Parameters
        ----------
        task_id : str
            the task's unique id

        Returns
        -------
        float
            the task's out_completion_cost
        """
        cost = 0
        for current_task_id in self.deep_first_search(task_id):
            cost += self.task_list[current_task_id].out_line_cost
        return cost

    def task_in_line_completion_cost(self, task_id: str) -> float:
        """
        Method that computes the task's in_line_cost based on the mean execution time and the sation cost.

        Parameters
        ----------
        task_id : str
            the task's unique id

        Returns
        -------
        float
            the task's in_line_cost
        """
        return self.task_list[task_id].m*self.c

    def compute_z_limit(self, task_id: str) -> float:
        """
        Method that computes the task's normalized execution time limit that solves    
        inline_cost = out_completion_cost*P    
        with P the probability of missed complition of the task

        Parameters
        ----------
        task_id : str
            the task's unique id

        Returns
        -------
        float
            the task's normalized execution time limit (z_limit)
        """
        return norm.ppf(1-self.task_list[task_id].in_line_cost/self.task_list[task_id].out_completion_cost)

    def fill_task_properties(self) -> None:
        """
        Method that helps creating the Task objects and populate their properties.
        """
        for key, task in self.task_list.items():
            task.out_completion_cost = self.task_out_line_completion_cost(key)
            task.in_line_cost = self.task_in_line_completion_cost(key)
            task.z_limit = self.compute_z_limit(key)
            task.n_successors = len(self.successors_of(key))

    def potential_tasks(self) -> Set[str]:
        """
        Available tasks, given those already assigned, according to the operation process chart.

        Returns
        -------
        Set[str]
            Set of available tasks. 
        """
        ass_tasks = self.assigned_tasks()
        missing_tasks = set(self.task_list.keys()).difference(ass_tasks)

        pot_tasks = set()
        for task_id in missing_tasks:
            # if firts task or all predecessor tasks already assigned
            if len(self.task_list[task_id].predecessor_set) == 0 or self.task_list[task_id].predecessor_set.issubset(ass_tasks):
                pot_tasks.add(task_id)

        return pot_tasks

    
    def compute_status(self, task_id: str, station: Station) -> Tuple[str, float, float, float, float]:
        """
        For a given task, and a given station with assigned tasks, computes the status according to the equation:
        inline_cost = out_completion_cost*P    
        with P the probability of missed complition of the task.
        This status determines whether the task could be assigned to the station or a new station should be opened.

        Returns
        -------
        Tuple[str, float, float, float, float]
            Tuple of task's informations needed to decide the assignment among other available tasks:
            - status: "safe", "desirable" or "critical"
            - z: the station's normalized execution time of the assigned tasks (with the current task assigned)
            - out_compl_cost: task's completition cost outside the production line.
            - expected_cost_out_line: tasks completion cost outside the production line multiplied by the probability of this occurrence
            - n_successors: number of tasks directly following the current one.
        """
        m_list = [self.task_list[t].m for t in station.out_line_cost.keys()]
        if len(m_list) > 0:
            m_sum = reduce(lambda x, y: x+y, m_list) + self.task_list[task_id].m
        else:
            m_sum = self.task_list[task_id].m

        s_list = [self.task_list[t].s for t in station.out_line_cost.keys()]
        if len(s_list) > 0:
            s_sum = reduce(lambda x, y: x+y, s_list) + self.task_list[task_id].s
        else:
            s_sum = self.task_list[task_id].s

        z = (self.T-m_sum)/sqrt(s_sum)
        out_compl_cost = self.task_list[task_id].out_completion_cost
        n_successors = self.task_list[task_id].n_successors
        expected_cost_out_line = (1-norm.cdf(z))*out_compl_cost

        if z > 2.575: # z-value that corresponds to a very low probability of task incompletion (P<0.005)
            status = "safe"
        elif z > self.task_list[task_id].z_limit:
            status = "desirable"
        else:
            status = "critical"

        return status, z, out_compl_cost, expected_cost_out_line, n_successors

    def execute_algorithm(self):
        """
        Main method that executes the algorithm updqating the Instance object properties.
        """
        n_station = 0 # station counter and id.

        while len(self.potential_tasks()) > 0: # Tasks loop
            n_station += 1
            current_station = str(n_station)
            self.station_list[current_station] = Station(current_station)

            while True: # Station loop

                pot_tasks = [] # potential tasks
                for task_id in self.potential_tasks():
                    status, z, out_compl_cost, expected_cost_out_line, n_successors = self.compute_status(task_id, self.station_list[current_station])
                    pot_tasks.append([task_id, status, z, out_compl_cost, expected_cost_out_line, n_successors])

                if len(self.potential_tasks()) == 0: break # end algorithm

                critical_tasks = list(filter(lambda x: x[1] == 'critical', pot_tasks))
                safe_tasks = list(filter(lambda x: x[1] == 'safe', pot_tasks))
                desirable_tasks = list(filter(lambda x: x[1] == 'desirable', pot_tasks))

                if len(critical_tasks) > 0 and len(self.station_list[current_station].out_line_cost.keys()) == 0: # a task is critical only if no task is already assigned
                    selected_task = sorted(critical_tasks , key=lambda x: x[5], reverse=True)[0] #take critical task with highest number of succesors
                elif len(safe_tasks) > 0:
                    selected_task = sorted(safe_tasks , key=lambda x: x[3], reverse=True)[0] #take safe task with highest out_compl_cost
                elif len(desirable_tasks) > 0:
                    selected_task = sorted(desirable_tasks , key=lambda x: x[3])[0] #take desirable task with lowest out_compl_cost
                else:
                    selected_task = []
                    break # new station

                self.station_list[current_station].out_line_cost[selected_task[0]] = selected_task[4]

        # compute total_unit_cost
        for station in self.station_list.values():
            for value in station.out_line_cost.values():
                self.total_unit_cost += value
        self.total_unit_cost += self.T*self.c*len(self.station_list) # TODO: check time unit

    def log_result(self):
        """
        Print the instance solution.
        """
        for key, station in self.station_list.items():
            print(f"+++++++++++++++ station {key} +++++++++++++++")
            print(f"task\tunit_cost_out_line")
            for key, value in station.out_line_cost.items():
                print(f"{key}\t{value}")
        print("\n###################\n")
        print(f"TOTAL COST [€/pc]: {self.total_unit_cost}") # TODO: check time unit
        print("\n###################")
