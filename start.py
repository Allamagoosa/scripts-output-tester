import csv
import json
import logging
import os

import deepdiff  # pip3 install deepdiff

from control.executor import ScriptExecutor

"""Execute bash script and analyse results

To run main logic:
    ./start.py
Check bash script results
    - check_full_match
    - check_substring_like
    - highlight_expected_with_student
    TODO
    - Preparations => Iterate through students dirs/zip ???
    - Generate full report to file + score
    - YAML config
    - Wide test set => config.yaml
    - test cases generator ???
    - true script comparator

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


class ResultCheckerCSV(object):
    def __init__(self, expected_csv, to_check_csv):
        self.expected_result_csv = expected_csv
        self.to_check_csv = to_check_csv
        self.content_expected, self.expected_fields = self._get_csv_content(self.expected_result_csv)
        self.content_to_check, self.to_check_fields = self._get_csv_content(self.to_check_csv)

    def _get_csv_content(self, csv_file_path):
        """Get list of CSV content
        return list [{row1}, {row2}, ...]

        """

        logger.info(f"Getting CSV content {csv_file_path}")
        output_list = []

        with open(csv_file_path, newline='') as csvfile:

            reader = csv.DictReader(csvfile)
            try:
                for row in reader:
                    output_list.append(row)
            except csv.Error as e:
                print("csv Reader error")
                print(e)
            else:
                return output_list, reader.fieldnames

    def compare_dictionaries(self):
        length1 = len(self.content_expected)
        length2 = len(self.content_expected)
        if self.expected_fields != self.to_check_fields:
            logger.info(f"{self.to_check_fields} != {self.expected_fields}")
            logger.info("Not matched fields")
            return False
        for i in range(length1):
            logger.debug("Comparing CSV content:")
            logger.debug(f'\t{self.content_expected[i]} \n\t<=> {self.content_to_check[i]}')
            result = self.content_expected[i] == self.content_to_check[i]
            # Deep diff
            if not result:
                logger.info("Not matched")
                diff = deepdiff.DeepDiff(self.content_expected[i], self.content_to_check[i])
                logger.info(json.dumps(diff, indent=4))
            return result

    def highlight_expected_with_student_results(self):
        pass


class ScriptSimpleOutput(object):
    # TODO Script basic Abstract class

    def __init__(self, command, exec_dir, testing_arg, result_expected):
        # TODO work with args set -> results set
        self.command = command
        self.exec_dir = exec_dir
        self.testing_arg = testing_arg
        self.command_with_arg = f'{command} {testing_arg}'
        self.result_expected = result_expected
        self.output_full = None
        self.output_strip = None
        self.passed = False
        # TODO score counter
        self.score = 0

    def check_full_match(self):
        logger.debug(f'Expected result: {self.result_expected}')
        logger.debug(f'Student  result: {self.output_strip}')
        self.passed = self.result_expected == self.output_strip
        logger.debug(f'Passed: {self.passed}')
        return self.passed

    def check_substring_like(self):
        logger.debug(f'Expected result: {self.result_expected}')
        logger.debug(f'Student  result: {self.output_strip}')
        self.passed = self.result_expected.upper() in self.output_strip.upper()
        logger.debug(f'Passed: {self.passed}')
        return self.passed

    def highlight_expected_with_student_results(self):
        return f"""==============Completed==============
                     To check: {self.command_with_arg}
                     Expected: {self.result_expected}
                     Result  : {self.output_strip}
                     Passed  : {self.passed} 
        ============================================"""


if __name__ == '__main__':
    DIR_PATH = os.path.dirname(os.path.abspath(__file__))

    # TODO read params from config files
    COMMAND = "./netcalc.sh"
    EXEC_DIR = os.path.join(DIR_PATH, "scripts")
    ARG = "--host 192.168.100.255/24"
    EXPECTED_RESULT = "Not Valid"

    # TODO - check script file existence before check
    script1 = ScriptSimpleOutput(COMMAND, EXEC_DIR, ARG, EXPECTED_RESULT)
    logger.info(f'Checking {script1.command_with_arg} \n\t\tExptected: {EXPECTED_RESULT}')

    executor = ScriptExecutor()
    if not executor.execute(script1):
        # TODO check exit_code errors and sort out issues: stud script failure OR this script failure
        logger.warning("Execute failed")
        exit(0)

    logger.info(f'Passed: {script1.check_substring_like()}')
    logger.info(script1.highlight_expected_with_student_results())

    logger.info("Checking csv results:")
    csv1 = os.path.join(DIR_PATH, "scripts/accounts.csv")
    csv2 = os.path.join(DIR_PATH, "scripts/accounts_new.csv")
    csv_checker = ResultCheckerCSV(csv1, csv2)
    csv_checker.compare_dictionaries()
