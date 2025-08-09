#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 - Present Sepine Tam, Inc. All Rights Reserved
#
# @Author : Sepine Tam
# @Email  : sepinetam@gmail.com
# @File   : do.py

import logging
import os
import subprocess

from stata_mcp.utils import get_nowtime


class StataDo:
    def __init__(
            self,
            stata_cli: str,
            log_file_path: str,
            dofile_base_path: str,
            sys_os: str):
        """
        Initialize Stata executor

        Args:
            stata_cli: Path to Stata command line tool
            log_file_path: Path for storing log files
            dofile_base_path: Base path for do files
            sys_os: Operating system type
        """
        self.stata_cli = stata_cli
        self.log_file_path = log_file_path
        self.dofile_base_path = dofile_base_path
        self.sys_os = sys_os

    def execute_dofile(self, dofile_path: str) -> str:
        """
        Execute Stata do file and return log file path

        Args:
            dofile_path: Path to do file

        Returns:
            str: Path to generated log file

        Raises:
            ValueError: Unsupported operating system
            RuntimeError: Stata execution error
        """
        nowtime = get_nowtime()
        log_file = os.path.join(self.log_file_path, f"{nowtime}.log")

        if self.sys_os == "Darwin" or self.sys_os == "Linux":
            self._execute_unix_like(dofile_path, log_file)
        elif self.sys_os == "Windows":
            self._execute_windows(dofile_path, log_file, nowtime)
        else:
            raise ValueError(f"Unsupported operating system: {self.sys_os}")

        return log_file

    def _execute_unix_like(self, dofile_path: str, log_file: str):
        """
        Execute Stata on macOS/Linux systems

        Args:
            dofile_path: Path to do file
            log_file: Path to log file

        Raises:
            RuntimeError: Stata execution error
        """
        proc = subprocess.Popen(
            [self.stata_cli],  # Launch the Stata CLI
            stdin=subprocess.PIPE,  # Prepare to send commands
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,  # Required when the path contains spaces
        )

        # Execute commands sequentially in Stata
        commands = f"""
        log using "{log_file}", replace
        do "{dofile_path}"
        log close
        exit, STATA
        """
        stdout, stderr = proc.communicate(
            input=commands
        )  # Send commands and wait for completion

        if proc.returncode != 0:
            logging.error(f"Stata execution failed: {stderr}")
            raise RuntimeError(f"Something went wrong: {stderr}")
        else:
            logging.info(
                f"Stata execution completed successfully. Log file: {log_file}")

    def _execute_windows(self, dofile_path: str, log_file: str, nowtime: str):
        """
        Execute Stata on Windows systems

        Args:
            dofile_path: Path to do file
            log_file: Path to log file
            nowtime: Timestamp for generating temporary file names
        """
        # Windows approach - use the /e flag to run a batch command
        # Create a temporary batch file
        batch_file = os.path.join(self.dofile_base_path, f"{nowtime}_batch.do")

        try:
            with open(batch_file, "w", encoding="utf-8") as f:
                f.write(f'log using "{log_file}", replace\n')
                f.write(f'do "{dofile_path}"\n')
                f.write("log close\n")
                f.write("exit, STATA\n")

            # Run Stata on Windows using /e to execute the batch file
            # Use double quotes to handle spaces in the path
            cmd = f'"{self.stata_cli}" /e do "{batch_file}"'
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                logging.error(
                    f"Stata execution failed on Windows: {result.stderr}")
                raise RuntimeError(
                    f"Windows Stata execution failed: {result.stderr}")
            else:
                logging.info(
                    f"Stata execution completed successfully on Windows. Log file: {log_file}")

        except Exception as e:
            logging.error(f"Error during Windows Stata execution: {str(e)}")
            raise
        finally:
            # Clean up temporary batch file
            if os.path.exists(batch_file):
                try:
                    os.remove(batch_file)
                    logging.debug(
                        f"Temporary batch file removed: {batch_file}")
                except Exception as e:
                    logging.warning(
                        f"Failed to remove temporary batch file {batch_file}: {str(e)}")

    def read_log(self, log_file_path):
        with open(log_file_path, "r") as file:
            log_content = file.read()
        return log_content
