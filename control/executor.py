import subprocess
import logging

logger = logging.getLogger("main")


class ScriptExecutor(object):

    def __init__(self):
        self.exit_code = None
        self.error_output = None

    def execute(self, script):
        """Call bash command

        return bash output or just a command if no output

        """
        try:
            # put additional debug logging here
            # put output assignment to script
            logger.info(f'Executing {script.command_with_arg} (dir = {script.exec_dir})')
            output = subprocess.check_output(script.command_with_arg, shell=True, stderr=subprocess.STDOUT, cwd=script.exec_dir)
        except OSError as os_exc:
            logger.error("FAILED to run bash command (OSError):\n{0}".format(script.command))
            logger.error(os_exc)
            exit(1)
            return False
        except subprocess.CalledProcessError as exc:
            logger.warning("FAILED to run bash command (CalledProcessError):\n{0}".format(script.command))
            logger.warning("===CalledProcessError================================:")
            logger.warning("Return code: {0}".format(exc.returncode))
            logger.warning("Command:\n{0}".format(exc.cmd))
            logger.warning("Output:\n{0}".format(exc.output))
            logger.warning("=====================================================")
            self.exit_code = exc.returncode
            self.error_output = exc.output
            return False
        else:
            self.exit_code = 0
            script.output_full = output
            script.output_strip = self._strip_output(output)
            return True

    def _strip_output(self, bin_string_output):
        return bin_string_output.decode().rstrip("\n")
