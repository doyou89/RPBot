#  Copyright 2013-2014 Nokia Solutions and Networks
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import logging
from robot.api import ExecutionResult


logging.basicConfig()


class RobotResultsParser(object):

    def __init__(self, reporter, verbose):
        self._logger = logging.getLogger('Parser')
        if verbose:
            self._logger.setLevel(verbose)
        self.reporter = reporter

    def xml_to_db(self, xml_file):
        self._logger.info('- Parsing %s' % xml_file)
        test_run = ExecutionResult(xml_file, include_keywords=True)

        self._parse_suite(test_run.suite)

    def _parse_suite(self, suite, parent_suite_id=None):
        self._logger.info('`--> Parsing suite: %s' % suite.name)

        attributes = {
            'id': suite.id,
            'longname': suite.longname,
            'doc': suite.doc,
            'metadata': suite.metadata,
            'source': suite.source,
            'suites': suite.suites,
            'tests': suite.tests,
            'totaltests': suite.test_count,
            'starttime': suite.starttime,
            'endtime': suite.endtime,
            'elapsedtime': suite.elapsedtime,
            'status': suite.status,
            'statistics': suite.statistics,
            'message': suite.message,
        }

        self.reporter.start_suite(suite.name, attributes)

        self._parse_suites(suite, suite.id)
        self._parse_tests(suite.tests, suite.id)
        self._parse_keywords(suite.keywords, suite.id, None)

        self.reporter.end_suite(suite.name, attributes)
        if suite.id == 's1' and not suite.suites:
            attributes['id'] = suite.id
            self.reporter.end_suite(suite.name, attributes)

    def _parse_suites(self, suite, parent_suite_id):
        [self._parse_suite(subsuite, parent_suite_id) for subsuite in suite.suites]

    def _parse_tests(self, tests, suite_id):
        [self._parse_test(test, suite_id) for test in tests]

    def _parse_test(self, test, suite_id):
        self._logger.info('  `--> Parsing test: %s' % test.name)

        attributes = {
            'id': test.id,
            'longname': test.longname,
            'doc': test.doc,
            'tags': [tag for tag in test.tags],
            'critical': test.critical,
            'template': '',
            'starttime': test.starttime,
            'endtime': test.endtime,
            'elapsedtime': test.elapsedtime,
            'status': test.status,
            'message': test.message
        }

        self.reporter.start_test(test.name, attributes)

        self._parse_keywords(test.keywords, None, test.id)

        self.reporter.end_test(test.name, attributes)

    def _parse_keywords(self, keywords, suite_id, test_id, keyword_id=None):
        [self._parse_keyword(keyword, suite_id, test_id, keyword_id) for keyword in keywords]

    def _parse_keyword(self, keyword, suite_id, test_id, keyword_id):

        attributes = {
            'type': keyword.type,
            'kwname': keyword.kwname,
            'libname': keyword.libname,
            'doc': keyword.doc,
            'args': keyword.args,
            'assign': keyword.assign,
            'tags': keyword.tags,
            'starttime': keyword.starttime,
            'endtime': keyword.endtime,
            'elapsedtime': keyword.elapsedtime,
            'status': keyword.status
        }

        self.reporter.start_keyword(keyword.name, attributes)

        self._parse_messages(keyword.messages, keyword_id)
        self._parse_keywords(keyword.keywords, None, None, keyword_id)

        self.reporter.end_keyword(keyword.name, attributes)

    def _parse_messages(self, messages, keyword_id):
        for message in messages:
            self.reporter.log_message({'message': message.message, 'level': message.level,
                                       'timestamp': message.timestamp, 'html': message.html})
