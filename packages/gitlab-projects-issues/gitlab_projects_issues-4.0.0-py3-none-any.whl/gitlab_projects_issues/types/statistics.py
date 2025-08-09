#!/usr/bin/env python3

# Standard libraries
from math import isclose
from typing import Dict

# TimesStatistics class, pylint: disable=too-few-public-methods
class TimesStatistics:

    # Constants
    # PROGRESS_DECADE = '⣀⣄⣄⣆⣆⣇⣇⣧⣧⣷⣿'
    PROGRESS_DECADE = '▁▂▂▃▄▄▅▅▆▇█'

    # Members
    defaulted: bool
    estimates: int
    spent: int

    # Constructor
    def __init__(self) -> None:
        self.defaulted = False
        self.estimates = 0
        self.spent = 0

    # Properties
    @property
    def remaining(self) -> int:
        return self.estimates - self.spent if self.estimates >= self.spent else 0

    # Convert time estimates
    @staticmethod
    def human(time_estimate_seconds: int, defaulted: bool = False) -> str:

        # Variables
        days: int
        minutes: int
        output: str = ''
        seconds: int

        # Defaulted times
        if defaulted:
            output += '~?'

        # Extract days
        days, seconds = divmod(time_estimate_seconds, 3600 * 8)
        if days:
            if output:
                output += ' '
            output += f'{days}d'

        # Extract hours
        hours, seconds = divmod(seconds, 3600)
        if hours:
            if output:
                output += ' '
            output += f'{hours}h'

        # Extract minutes
        minutes, _ = divmod(seconds, 60)
        if minutes:
            if output:
                output += ' '
            output += f'{minutes}min'

        # Empty fallback
        if not output:
            output = '/'

        # Result
        return output

    # Progress
    def progress(self) -> str:

        # Variables
        output: str = ''
        percentage: float
        unit: int

        # Evaluate percentage
        if self.spent >= self.estimates:
            percentage = 100.0
            unit = 0
        else:
            percentage = 100.0 * self.spent / self.estimates
            unit = int(percentage) % 10

        # Add progress bar
        for percent in range(0, 100, 10):
            if percent == 0 and isclose(percentage, 0.0):
                output += TimesStatistics.PROGRESS_DECADE[0]
            elif percentage >= percent + 10:
                output += TimesStatistics.PROGRESS_DECADE[10]
            elif percent == 100 and isclose(percentage, 100.0):
                output += TimesStatistics.PROGRESS_DECADE[10]
            elif percentage >= percent:
                output += TimesStatistics.PROGRESS_DECADE[unit]
            else:
                output += TimesStatistics.PROGRESS_DECADE[0]

        # Add percentage
        output += f' {percentage:.2f}%'

        # Result
        return output

# AssigneeStatistics class, pylint: disable=too-few-public-methods
class AssigneeStatistics:

    # Members
    name: str
    issues_count: int
    times: TimesStatistics

    # Constructor
    def __init__(
        self,
        name: str,
    ):
        self.name = name
        self.issues_count = 0
        self.times = TimesStatistics()

# MilestoneStatistics class, pylint: disable=too-few-public-methods
class MilestoneStatistics:

    # Members
    title: str
    issues_count: int
    times: TimesStatistics
    assignees: Dict[str, AssigneeStatistics]

    # Constructor
    def __init__(
        self,
        title: str,
    ):
        self.title = title
        self.issues_count = 0
        self.times = TimesStatistics()
        self.assignees = {}
