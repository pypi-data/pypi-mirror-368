#!/usr/bin/env python3

# Standard libraries
from os import environ

# Modules libraries
from pexpect_executor import Executor

# Engine
environ['CI_LOCAL_ENGINE'] = 'docker,auto'

# Terminal
environ['PROMPT_TOOLKIT_NO_CPR'] = '1'

# Configure, pylint: disable=line-too-long
Executor.configure(
    host='preview',
    tool='gcil',
    masks=[
        f'{environ["REGISTRY_HOST"]}/{environ["REGISTRY_NAMESPACE"]}/{environ["REGISTRY_PROJECT"]}/',
    ],
)

# Jobs selector
Executor('gcil',
         delay_init=0.1, delay_press=0.2, delay_prompt=0.5,
         workdir='./examples/').\
    read().\
    press(Executor.KEY_SPACE).\
    read().\
    press(Executor.KEY_DOWN).\
    press(Executor.KEY_DOWN).\
    press(Executor.KEY_DOWN).\
    read().\
    press(Executor.KEY_SPACE).\
    read().\
    press(Executor.KEY_DOWN).\
    press(Executor.KEY_DOWN).\
    read().\
    press(Executor.KEY_SPACE).\
    read().\
    press(Executor.KEY_DOWN).\
    read().\
    press(Executor.KEY_SPACE).\
    read().\
    wait(1).\
    press(Executor.KEY_ENTER).\
    finish()

# Job selector
Executor('gcil -l',
         delay_init=0.1, delay_press=0.2, delay_prompt=0.5).\
    read().\
    press(Executor.KEY_SPACE).\
    read().\
    press(Executor.KEY_DOWN).\
    press(Executor.KEY_DOWN).\
    press(Executor.KEY_DOWN).\
    press(Executor.KEY_DOWN).\
    read().\
    wait(1).\
    press(Executor.KEY_ENTER).\
    finish()

# Job runner
Executor('gcil \'Job 1 - 3\'',
         delay_init=0.5, delay_press=0.2, delay_prompt=0.5).\
    finish()

# Pipeline runner
Executor('gcil -p',
         delay_init=0.5, delay_press=0.2, delay_prompt=0.5,
         workdir='../tests/failures/').\
    finish()

# Stage runner
Executor('gcil -p one two',
         delay_init=0.5, delay_press=0.2, delay_prompt=0.5,
         workdir='../stages/').\
    finish()

# Bash console
Executor('gcil --bash \'Job 1 - 3\'',
         delay_init=0.5, delay_press=0.2, delay_prompt=0.5,
         workdir='../../examples/').\
    wait(1).\
    read().\
    press('echo "Console ready for development in the job"').\
    read().\
    press(Executor.KEY_ENTER).\
    read().\
    press('exit').\
    press(Executor.KEY_ENTER).\
    read().\
    wait(1).\
    finish()

# Debug console
Executor('gcil --debug \'Job 1 - 3\'',
         delay_init=0.5, delay_press=0.2, delay_prompt=0.5).\
    wait(1).\
    read().\
    press('echo "Console ready for debugging the job"').\
    read().\
    press(Executor.KEY_ENTER).\
    read().\
    press('exit').\
    press(Executor.KEY_ENTER).\
    read().\
    wait(1).\
    finish()

# Prompt
Executor(delay_prompt=3.0, hold_prompt=True)
