"""
FILE: covid_model.py
DESCRIPTION: Prepare the data as API-ready
AUTHOR: Nuttaphat Arunoprayoch
DATE: 9-Feb-2020
"""
# Import libraries
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
from utils.helper import get_data
from collections import OrderedDict


# Create a model and its methods
class NovelCoronaAPI:
    """ Model and Its methods """
    def __init__(self) -> None:
        """ Get data from helper -> the source data """
        list_of_dataframes = get_data()
        self.df_confirmed = list_of_dataframes['confirmed']
        self.df_deaths = list_of_dataframes['deaths']
        self.df_recovered = list_of_dataframes['recovered']

        list_of_time_series = get_data(time_series=True)
        self.df_time_series_confirmed = list_of_time_series['confirmed']
        self.df_time_series_deaths = list_of_time_series['deaths']
        self.df_time_series_recovered = list_of_time_series['recovered']

        self.datetime_raw = self.df_confirmed['datetime'].unique().tolist()[0]
        self.timestamp = datetime.strptime(self.datetime_raw, '%m/%d/%y').timestamp()

    def add_dt_and_ts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """ Add datetime and timestamp to Dict data """
        data['dt'] = self.datetime_raw
        data['ts'] = self.timestamp
        return data

    def get_current_status(self, list_required: bool = False) -> Dict[str, Any]:
        """ Current data (Lastest date) """
        # Create a template
        countries = self.df_confirmed['Country/Region'].unique().tolist()
        current_data = {country: {'confirmed': 0, 'deaths': 0, 'recovered': 0} for country in countries}

        # Extractor
        def extractor(col: str, df: pd.DataFrame) -> None:
            temp_data = df.T.to_dict()
            for data in temp_data.values():
                current_data[data['Country/Region']][col] += int(data[col.capitalize()])
            return None

        # Add data to current_data
        df_list = {'confirmed': self.df_confirmed, 'deaths': self.df_deaths, 'recovered': self.df_recovered}
        [extractor(col, df) for col, df in df_list.items()]

        sorted_data = OrderedDict()
        for key, value in sorted(current_data.items(), key=lambda item: item[1]["confirmed"]):
            sorted_data[key] = value

        # Check if a List form is required
        if list_required:
            sorted_data['countries'] = [{k: v for k, v in sorted_data.items()}]
            sorted_data = {k:v for k, v in sorted_data.items() if k in ['countries']} # Filter out other keys except countries

        # Add datetime and timestamp
        sorted_data = self.add_dt_and_ts(sorted_data)

        return sorted_data

    def get_confirmed_cases(self) -> Dict[str, int]:
        """ Summation of all confirmed cases """
        data = {'confirmed': sum([int(i) for i in self.df_confirmed['Confirmed']])}
        data = self.add_dt_and_ts(data)
        return data

    def get_deaths(self) -> Dict[str, int]:
        """ Summation of all deaths """
        data = {'deaths': sum([int(i) for i in self.df_deaths['Deaths']])}
        data = self.add_dt_and_ts(data)
        return data

    def get_recovered(self) -> Dict[str, int]:
        """ Summation of all recovers """
        data = {'recovered': sum([int(i) for i in self.df_recovered['Recovered']])}
        data = self.add_dt_and_ts(data)
        return data

    def get_total(self) -> Dict[str, Any]:
        """ Summation of Confirmed, Deaths, Recovered """
        data = {
            'confirmed': self.get_confirmed_cases()['confirmed'],
            'deaths': self.get_deaths()['deaths'],
            'recovered': self.get_recovered()['recovered']
            }
        data = self.add_dt_and_ts(data)
        return data

    def get_affected_countries(self) -> Dict[str, List]:
        """ The affected countries """
        data = {'countries': sorted(self.df_confirmed['Country/Region'].unique().tolist())}
        data = self.add_dt_and_ts(data)
        return data

    def get_time_series(self) -> Dict[str, Dict]:
        """ Raw time series """
        data = {
            'confirmed': self.df_time_series_confirmed,
            'deaths': self.df_time_series_deaths,
            'recovered':  self.df_time_series_recovered,
        }
        data = self.add_dt_and_ts(data)
        return data
