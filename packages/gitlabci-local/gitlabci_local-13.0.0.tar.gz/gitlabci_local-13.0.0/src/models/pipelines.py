#!/usr/bin/env python3

# Standard libraries
from argparse import Namespace

# Components
from .images import Entrypoint, Image
from .jobs import Jobs
from .scripts import Scripts
from .services import Services
from .stages import Stages
from .variables import VariablesParser

# Pipeline class, pylint: disable=too-few-public-methods,too-many-instance-attributes
class Pipeline:

    # Members
    image: Image
    entrypoint: Entrypoint
    before_script: Scripts
    after_script: Scripts
    jobs: Jobs
    services: Services
    stages: Stages
    variables: VariablesParser

    # Constructor
    def __init__(self, options: Namespace) -> None:
        self.image = ''
        self.entrypoint = None
        self.before_script = []
        self.after_script = []
        self.jobs = {}
        self.services = []
        self.stages = []
        self.variables = VariablesParser(options)
