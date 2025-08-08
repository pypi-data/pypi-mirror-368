from typing import Any, Dict, List, Optional, Tuple, Callable
from multiprocessing.pool import Pool

import numpy as np
import pandas as pd



class ParallelComputing:
    def __init__(
        self,
        func: Optional[Callable] = None,
        list_to_proceed: Optional[List] = None,
        num_cores: int = 3
    ):
        """
        Initialize the ParallelComputing instance.

        Parameters:
        -----------
        func : Callable, optional
            The function to apply in parallel.
        list_to_proceed : list, optional
            The list of items to process.
        num_cores : int, default=3
            Number of parallel processes to use.
        """
        self.func = func
        self.list = list_to_proceed
        self.result = []
        self.num_cores = num_cores

    @staticmethod
    def split_df_to_list_by_group(df: pd.DataFrame, group_name: str) -> List[pd.DataFrame]:
        """
        Split a DataFrame into a list of DataFrames grouped by a column.

        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame to split.
        group_name : str
            Column name to group by.

        Returns:
        --------
        List[pd.DataFrame]
            List of grouped DataFrames.
        """
        return [pd.DataFrame(v) for _, v in df.groupby(group_name)]

    def set_list(self, newlist: List) -> None:
        """Set the list of items to process."""
        self.list = newlist

    def set_func(self, func: Callable) -> None:
        """Set the function to apply in parallel."""
        self.func = func

    def set_num_cores(self, num_cores: int) -> None:
        """Set the number of parallel processes."""
        self.num_cores = num_cores

    def run_in_parallel(self) -> None:
        """Run the function in parallel over the list of items."""
        if not self.func or not self.list:
            raise ValueError("Function and list to process must be set before running.")
        with Pool(self.num_cores) as pool:
            self.result = pool.map(self.func, self.list)
        print('Finished')

    def get_result(self) -> List:
        """Get the result list after parallel processing."""
        return self.result

