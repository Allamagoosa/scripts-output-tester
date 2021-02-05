import logging
import os

from control.executor import Executor

"""Execute bash script and analyse results

To run main logic:
    ./start.py
Check bash script results
    - check_full_match
    - check_substring_like
    - highlight_expected_with_student
    TODO
    - Working with students dirs/zip ???
    - Generate full report to file + score
    - YAML config
    - Wide test set => config.yaml

"""

###########
# logging #
###########
logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)

handler_console = logging.StreamHandler()
handler_console.setLevel(logging.INFO)  # Put INFO here for normal work

formatter_console = logging.Formatter('[%(levelname)s] %(message)s')
handler_console.setFormatter(formatter_console)
logger.addHandler(handler_console)

logger.debug("Running {0}".format(__file__))


class Script(object):

    def __init__(self, command, testing_arg, result_expected):
        # TODO work with bunch of args set -> results set
        self.command = command
        self.testing_arg = testing_arg
        self.command_with_arg = f'{command} {testing_arg}'
        self.result_expected = result_expected
        self.result = ""
        self.passed = False
        # TODO score counter
        self.score = 0

    def check_full_match(self):
        logger.debug(f'Expected result: {self.result_expected}')
        logger.debug(f'Student  result: {self.result}')
        self.passed = self.result_expected == self.result
        logger.debug(f'Passed: {self.passed}')
        return self.passed

    def check_substring_like(self):
        logger.debug(f'Expected result: {self.result_expected}')
        logger.debug(f'Student  result: {self.result}')
        self.passed = self.result_expected.upper() in self.result.upper()
        logger.debug(f'Passed: {self.passed}')
        return self.passed

    def highlight_expected_with_student_results(self):
        return f"""==============Completed==============
                     Expected: {self.result_expected}
                     Result: {self.result}
                     Passed: {self.passed} 
        ============================================"""


if __name__ == '__main__':
    executor = Executor()

    # TODO read params from config files
    COMMAND = "./netcalc.sh"

    FROM_DIR = f'{os.path.dirname(os.path.realpath(__file__))}/scripts/'
    ARG = "--host 192.168.100.255/24"
    EXPECTED_RESULT = "Not Valid"

    # TODO - check script file existence before check
    script1 = Script(COMMAND, ARG, EXPECTED_RESULT)
    logger.info(f'Checking {script1.command_with_arg} for getting [{EXPECTED_RESULT}]')
    if not executor.execute(script1.command_with_arg, FROM_DIR):
        # TODO check exit_code errors and sort out issues: stud script failure OR this script failure
        logger.warning("Execute failed")
        exit(0)
    script1.result = executor.stripped_output

    logger.info(f'Passed: {script1.check_substring_like()}')
    logger.info(script1.highlight_expected_with_student_results())
