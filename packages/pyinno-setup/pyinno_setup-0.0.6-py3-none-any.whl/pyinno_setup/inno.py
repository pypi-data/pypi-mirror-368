from pyinno_setup import runit
from pyargman import ArgManager
from pathlib import Path

import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

"""
this is used for calling embedded innosetup compiler exe file,(required files are in libs folder)
it will give iss file as input and output is exe file,
output folder canbe changed all other settings are controlled by contents of iss file
to generate iss file try my other module 'pyinno_gen'
if somehow embeded exe is missing then you can change module attribute EXE_PATH to use your own

author: github.com/its-me-abi
date : 12/7/2025
"""

current_folder = Path(__file__).parent.resolve()
EXE_PATH = current_folder / "libs/Inno6/ISCC.exe"

class Error(Exception):
    def __init__(self, msg):
        logging.error(msg)

class BuildError(Error):
    SUCCESS = 0
    CLI_OR_INTERAL_ERROR = 1
    SCRIPT_ERROR = 2
    def __init__(self,msg,val):
        super().__init__(msg)
        self.message = msg
        self.value = val

class setup:
    def __init__(self,script, outfolder = "", outfile = ""   ,extra_commands =[] ):
        self.script = script
        self.outfolder = outfolder
        self.outfile = outfile
        self.EXE_PATH = EXE_PATH

        self.argman =  ArgManager(EXE_PATH)
        if outfile:
            self.argman.set_arg(f"/F{outfile}" , True )
        if outfolder:
            self.argman.set_arg(f"/O{outfolder}" , True )
        if extra_commands:
            self.argman.set_arg(extra_commands , True )
        if script:
            self.argman.set_arg(script, True )
        
        self.logger = logging.getLogger("innosetup")
        self.logger.setLevel("DEBUG")

    def get_cli_list(self):
        return self.argman.tolist()

    def build(self):
        if not self.EXE_PATH.exists():
            raise Error("embedded ISCC.exe file not found,probably script or exe files moved cwd = ", current_folder)
        if not Path(self.script).exists():
            raise Error(" input iss script file does not exist")

        result = runit.run_subprocess( self.get_cli_list() , logger= self.logger)
        if result == BuildError.SUCCESS:
            return True
        elif result== BuildError.SCRIPT_ERROR:
            raise BuildError("error in compiling usinng ISCC.exe,probably input iss script has errors", result)
        elif result== BuildError.CLI_OR_INTERAL_ERROR:
            raise BuildError("error in compiling usinng ISCC.exe,probably CLI arguemnt or internal error", result)


def build(input_path,outfolder = "", outfile = "" ,extra_commands =[] ):
    try:
        setupman = setup(input_path, outfolder=outfolder, outfile=outfile, extra_commands=extra_commands)
        logger.info(f"cli arguments are {setupman.get_cli_list()} ")
        if setupman.build():
            return True
    except:
        pass


if __name__ == "__main__":

    input_path = current_folder / "data/template.iss"
    output_folder = "output"
    logger.info(f"### building exe {input_path}" )
    if build( input_path , outfolder = output_folder, outfile = "xxx" ):
        logger.info("### successfully built by innosetup ###")
    else:
        logger.error("### innosetup build failed ###")