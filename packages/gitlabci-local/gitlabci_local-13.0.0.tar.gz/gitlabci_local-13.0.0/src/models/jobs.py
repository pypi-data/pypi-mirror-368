#!/usr/bin/env python3

# Standard libraries
from typing import Dict, Optional

# Components
from .images import Entrypoint, Image
from .options import Options
from .scripts import Scripts
from .services import Services
from .settings import AllowFailure, Retry, Trigger, When
from .stages import Stage
from .tags import Tags
from .variables import Variables

# JobName type
JobName = str

# JobData class, pylint: disable=too-few-public-methods,too-many-instance-attributes
class JobData:

    # Members
    name: JobName
    stage: Optional[Stage]
    image: Optional[Image]
    entrypoint: Entrypoint
    variables: Variables
    before_script: Optional[Scripts]
    script: Optional[Scripts]
    after_script: Optional[Scripts]
    retry: Optional[Retry]
    when: Optional[When]
    allow_failure: Optional[AllowFailure]
    services: Optional[Services]
    tags: Optional[Tags]
    trigger: Optional[Trigger]
    options: Options

    # Constructor
    def __init__(self, name: JobName) -> None:
        self.name = name
        self.stage = None
        self.image = None
        self.entrypoint = None
        self.variables = {}
        self.before_script = None
        self.script = None
        self.after_script = None
        self.retry = None
        self.when = None
        self.allow_failure = None
        self.services = None
        self.tags = None
        self.trigger = None
        self.options = Options()

# Job class, pylint: disable=too-few-public-methods,too-many-instance-attributes
class Job:

    # Members
    name: JobName
    stage: Stage
    image: Image
    entrypoint: Entrypoint
    variables: Variables
    before_script: Scripts
    script: Scripts
    after_script: Scripts
    retry: Retry
    when: When
    allow_failure: AllowFailure
    services: Services
    tags: Optional[Tags]
    trigger: Optional[Trigger]
    options: Options

    # Constructor
    def __init__(self, data: JobData) -> None:
        self.name = data.name
        assert data.stage is not None
        self.stage = data.stage
        assert data.image is not None
        self.image = data.image
        self.entrypoint = data.entrypoint
        self.variables = data.variables
        assert data.before_script is not None
        self.before_script = data.before_script
        assert data.script is not None
        self.script = data.script
        assert data.after_script is not None
        self.after_script = data.after_script
        assert data.retry is not None
        self.retry = data.retry
        assert data.when is not None
        self.when = data.when
        assert data.allow_failure is not None
        self.allow_failure = data.allow_failure
        assert data.services is not None
        self.services = data.services
        self.tags = data.tags
        self.trigger = data.trigger
        self.options = data.options

# Jobs type
Jobs = Dict[str, Job]
