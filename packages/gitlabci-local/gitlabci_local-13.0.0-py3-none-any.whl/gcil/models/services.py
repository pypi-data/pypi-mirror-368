#!/usr/bin/env python3

# Standard libraries
from typing import List, NamedTuple

# Components
from .images import Image

# ServiceAlias type
ServiceAlias = str

# Service class
class Service(NamedTuple):

    # Members
    image: Image
    alias: ServiceAlias

# Services type
Services = List[Service]
