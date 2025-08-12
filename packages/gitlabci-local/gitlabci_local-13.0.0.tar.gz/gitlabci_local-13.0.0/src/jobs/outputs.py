#!/usr/bin/env python3

# Components
from ..prints.colors import Colors
from ..system.platform import Platform

# Outputs class
class Outputs:

    # Debugging
    @staticmethod
    def debugging(
        container_exec: str,
        container_name: str,
        shell: str,
        console: bool,
    ) -> None:

        # Debugging informations
        print(' ')
        print(
            f'  {Colors.YELLOW}‣ INFORMATION: {Colors.BOLD}' \
                f'Job execution held active for debugging purposes{Colors.RESET}'
        )
        print(
                f'                 {Colors.BOLD}' \
                f"Use '{Colors.CYAN}{container_exec} {container_name} {shell}" \
                f'{Colors.BOLD}\' to debug manually{Colors.RESET}'
        )

        # Console informations
        if console:
            print(
                f'                 {Colors.BOLD}' \
                    f'Launching console in container, ' \
                    f'use \'{Colors.CYAN}exit{Colors.BOLD}\' to interrupt...{Colors.RESET}'
            )

        # Interruption informations
        else:
            print(
                f'                 {Colors.BOLD}' \
                    f'Interrupt job execution with Ctrl+C...{Colors.RESET}'
            )

        # Footer
        print(' ')
        Platform.flush()

    # Interruption
    @staticmethod
    def interruption() -> None:

        # Interruption output
        print(' ')
        print(' ')
        print(
            f'  {Colors.YELLOW}‣ WARNING: {Colors.BOLD}' \
                f'User interruption detected, stopping the container...{Colors.RESET}'
        )
        print(' ')
        Platform.flush()

    # Warning
    @staticmethod
    def warning(message: str) -> None: # pragma: no cover

        # Warning output
        print(f'  {Colors.YELLOW}‣ WARNING: {Colors.BOLD}{message}{Colors.RESET}')
        print(' ')
        Platform.flush()
