import subprocess
import logging
from typing import List, Optional, Union
from pathlib import Path

# this code is borrowed

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
        stderr=subprocess.STDOUT,
        text=True,
        shell=shell,
        cwd=cwd,
        env=env
    )

    assert process.stdout is not None
    for line in process.stdout:
        if logger:
            logger.info(line.strip())
        else:
            print(line.strip())

    process.stdout.close()
    return_code = process.wait()

    if check and return_code != 0:
        pass
        #raise subprocess.CalledProcessError(return_code, command)

    return return_code

if __name__ == "__main__":
    current_folder = Path(__file__).parent.resolve()
    exe_path = Path(current_folder) / "libs/Inno6/ISCC.exe"
    input_path = Path(current_folder) / "data/template.iss"
    print ( "### building started " ,exe_path , "\n   ", input_path  )
    run_subprocess([str (exe_path),str (input_path) ])
