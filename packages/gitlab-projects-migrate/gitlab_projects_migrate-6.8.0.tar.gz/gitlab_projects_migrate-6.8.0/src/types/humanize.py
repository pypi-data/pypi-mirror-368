#!/usr/bin/env python3

# Humanize class, pylint: disable=too-few-public-methods
class Humanize:

    # Size
    @staticmethod
    def size(value_in_bytes: int) -> str:

        # Variables
        unit: str = 'B'
        value: int = value_in_bytes

        # Return bytes string
        if value < 1024:
            return f"{value} {unit}"

        # Return kilobytes string
        value = int(value / 1024)
        if value < 1024:
            return f"{value} K{unit}"

        # Return megabytes string
        value = int(value / 1024)
        if value < 1024:
            return f"{value} M{unit}"

        # Return gigabytes string
        value = int(value / 1024)
        if value < 1024:
            return f"{value} G{unit}"

        # Return terabytes string
        value = int(value / 1024)
        if value < 1024:
            return f"{value} T{unit}"

        # Return petabytes string
        value = int(value / 1024)
        return f"{value} P{unit}"
