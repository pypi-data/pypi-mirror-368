#!/usr/bin/env python3

# Standard libraries
from typing import List

# MilestoneState class
class MilestoneState:
    ACTIVATE: str = 'activate'
    CLOSE: str = 'close'

    # Default
    @staticmethod
    def default() -> str:
        return MilestoneState.CLOSE

    # Names
    @staticmethod
    def names() -> List[str]:
        return [
            MilestoneState.ACTIVATE,
            MilestoneState.CLOSE,
        ]
