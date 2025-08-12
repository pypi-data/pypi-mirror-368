import pathlib
import pickle

import pandas as pd

from .yutils import TermColors, print_color
from .config import CACHE_WORKDAY_DATA
from .run_report import run_payroll_report


class PayrollData:
    def __init__(self, year):
        self._df = None
        self.year = year

    def get_workday_data(self, dr):
        # Get payroll
        payroll_cached_path = pathlib.Path("payroll.pkl")

        if payroll_cached_path.exists() and CACHE_WORKDAY_DATA:
            print("Loading payroll from cache...")
            self._df = pd.read_pickle(payroll_cached_path)
        else:
            self._get_payroll_data(dr)
            if CACHE_WORKDAY_DATA:
                self._df.to_pickle("payroll.pkl")

    def _get_payroll_data(self, dr):
        self._df = run_payroll_report(dr, self.year)

    @property
    def df(self):
        """Returns the payroll DataFrame."""
        if self._df is None:
            raise ValueError("Payroll data has not been loaded yet.")
        return self._df

    def to_pkl(self, path=None, xlsx_path=None):
        """Saves the payroll DataFrame to a pickle file."""
        if path is None:
            path = pathlib.Path(f"payroll_{self.year}.pkl")

        print_color(
            TermColors.GREEN, f"Saving {len(self.df)} rows of payroll data to {path}"
        )

        with open(path, "wb") as f:
            pickle.dump(self, f)

        if xlsx_path:
            print_color(
                TermColors.GREEN, f"Saving payroll data to Excel file {xlsx_path}"
            )
            self.df.to_excel(xlsx_path, index=False)
