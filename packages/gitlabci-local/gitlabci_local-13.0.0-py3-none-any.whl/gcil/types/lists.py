#!/usr/bin/env python3

# Standard libraries
from re import error, escape, search
from typing import List

# Lists class, pylint: disable=too-few-public-methods
class Lists:

    # Match
    @staticmethod
    def match(items: List[str], name: str, ignore_case: bool, no_regex: bool) -> bool:

        # Search without regex
        if name in items:
            return True

        # Search with regex
        if not no_regex:
            for item in items:

                # Search with string inclusion
                if item in name:
                    return True

                # Search with string case insensitive inclusion
                if ignore_case and item.lower() in name.lower():
                    return True

                # Search with real regex
                try:
                    if search(item, escape(name)):
                        return True
                    if ignore_case and search(item.lower(), escape(name.lower())):
                        return True
                except error: # pragma: no cover
                    pass

        # Result
        return False
