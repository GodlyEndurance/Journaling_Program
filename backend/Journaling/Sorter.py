'''
Sorter.py

'''
from enum import Enum
import config   

class SortMetric(Enum):
    Filename = 1    # foldername (name) or filename(date)
    DateModified = 2
    Favorite = 3

class Sorter():
    def __init__(self, metric: SortMetric):
        if (config.TEST_MODE): print(f"\nSorter initialized with metric: {metric}")
        self.metric: SortMetric = metric
        if (config.TEST_MODE): print(f"Sorter metric set to: {self.metric}")

    def SortByMetric(self, nodes: list):
        if (config.TEST_MODE): print(f"\nSorting nodes by metric: {self.metric}")

        if self.metric == SortMetric.Filename:
            nodes.sort(key=lambda x: x.name)
        elif self.metric == SortMetric.DateModified:
            nodes.sort(key=lambda x: x.date_modified)
        elif self.metric == SortMetric.Favorite:
            nodes.sort(key=lambda x: x.favorite, reverse=True)
            
        if (config.TEST_MODE): print(f"Nodes sorted by metric: {self.metric}")