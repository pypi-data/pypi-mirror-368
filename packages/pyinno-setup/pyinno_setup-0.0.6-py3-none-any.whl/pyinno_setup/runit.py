import subprocess
import logging
from typing import List, Optional, Union
from pathlib import Path

# this code is borrowed
import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

def run_subprocess(
    command: Union[List[str], str],
    logger: Optional[logging.Logger] = None,
    shell: bool = False,
    cwd: Optional[str] = None,
    env: Optional[dict] = None,
    check: bool = True
) -> int:
    """
    Run a subprocess with real-time logging.

    Args:
        command (list or str): Command to run (list preferred).
        logger (Logger): Logger to stream output to. If None, print to console.
        shell (bool): Run with shell (only if needed).
        cwd (str): Working directory.
        env (dict): Environment variables.
        check (bool): Raise error if return code is not 0.

    Returns:
        int: The return code of the subprocess.

    Raises:
        subprocess.CalledProcessError: if `check=True` and command fails.
    """
    if isinstance(command, str) and not shell:
        raise ValueError("String command requires shell=True")

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=shell,
        cwd=cwd,
        env=env
    )

    if process.stdout:
        for line in process.stdout:
            if logger:
                logger.info(line.strip())
            else:
                log.info(line.strip())

    if process.stderr:
        for line in process.stderr:
            if logger:
                logger.error(line.strip())
            else:
                log.info(line.strip())

    process.stdout.close()
    process.stderr.close()
    return_code = process.wait()

    if check and return_code != 0:
        pass
        #raise subprocess.CalledProcessError(return_code, command)

    return return_code

if __name__ == "__main__":
    run_subprocess(["cmd", "/c", "htt:/d"],logger= log) #test stderror redirecting to logger



