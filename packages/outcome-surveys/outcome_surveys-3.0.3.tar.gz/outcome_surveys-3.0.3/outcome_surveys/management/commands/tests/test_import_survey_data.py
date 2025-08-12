"""
Tests for `import_survey_data` management command.
"""

import re
from unittest import TestCase
from unittest.mock import patch
from urllib.parse import urlparse

import pytest
from django.core.management import call_command

from outcome_surveys.management.commands import import_survey_data
from outcome_surveys.management.commands.import_survey_data import Command
from outcome_surveys.management.commands.tests.mock_responses import MOCK_API_RESPONSES, MOCK_RESPONSE_HEADERS
from outcome_surveys.models import CourseGoal, CourseReflection, MultiChoiceResponse, SurveyExport
from outcome_surveys.surveymonkey_client import Session


class MockResponse:
    """
    Mock API response class.
    """
    def __init__(self, survey_id, headers=None, status_code=200):
        self.status_code = status_code
        self.headers = headers or MOCK_RESPONSE_HEADERS
        self.survey_id = survey_id

    def raise_for_status(self):
        return True

    def json(self):
        return MOCK_API_RESPONSES[self.survey_id]


def mocked_get_function(*args, **kwargs):
    """
    Mock function for API HTTP GET.
    """
    pattern = "^/v3/surveys/(?P<survey_id>[0-9]+)/responses/bulk$"
    path = urlparse(args[0]).path
    match = re.search(pattern, path)
    groups = match.groupdict()
    survey_id = groups['survey_id']
    return MockResponse(survey_id)


def mocked_get_function_with_rate_limit_exception(*args, **kwargs):
    """
    Mock function for API HTTP GET with modified headers.
    """
    pattern = "^/v3/surveys/(?P<survey_id>[0-9]+)/responses/bulk$"
    path = urlparse(args[0]).path
    match = re.search(pattern, path)
    groups = match.groupdict()
    survey_id = groups['survey_id']
    headers = MOCK_RESPONSE_HEADERS.copy()
    headers['X-Ratelimit-App-Global-Day-Remaining'] = 0
    return MockResponse(survey_id, headers=headers)


@pytest.mark.django_db
class TestImportSurveyDataCommand(TestCase):
    """
    Tests `import_survey_data` management command.
    """

    def setUp(self):
        super().setUp()
        self.command = import_survey_data.Command()

    def verify_course_reflection_response(self):
        """
        Verify that `CourseReflection` surveys data has been correctly extracted and stored.
        """
        course_reflection = CourseReflection.objects.all()

        assert course_reflection[0].survey_id == 505286548
        assert course_reflection[0].survey_response_id == 118086896063
        assert course_reflection[0].lms_enrollment_id == 1
        online_learning_goals = list(course_reflection[0].online_learning_goals.all().values_list('answer', flat=True))
        assert online_learning_goals == ['Learn valuable skills']
        goal_decisions = list(course_reflection[0].goal_decisions.all().values_list('answer', flat=True))
        assert goal_decisions == ['I need more skills']
        assert course_reflection[0].help_reach_goal == 'Somewhat confident'
        assert course_reflection[0].course_rating == 5
        assert course_reflection[0].course_experience == 'Keep up the good work'
        assert course_reflection[0].open_to_outreach is False

        assert course_reflection[1].survey_id == 507302428
        assert course_reflection[1].survey_response_id == 118086896063
        assert course_reflection[1].lms_enrollment_id == 22
        online_learning_goals = list(course_reflection[1].online_learning_goals.all().values_list('answer', flat=True))
        assert online_learning_goals == ['Learn valuable skills', 'Learn for fun']
        goal_decisions = list(course_reflection[1].goal_decisions.all().values_list('answer', flat=True))
        assert goal_decisions == ['I am hungry to learn']
        assert course_reflection[1].help_reach_goal == 'Very confident'
        assert course_reflection[1].course_rating == 4
        assert course_reflection[1].course_experience == 'Course content needs to be updated'
        assert course_reflection[1].open_to_outreach is True

    def verify_course_goal_response(self):
        """
        Verify that `CourseGoal` surveys data has been correctly extracted and stored.
        """
        course_reflection = CourseGoal.objects.all()

        print(course_reflection[0].__dict__)
        print(course_reflection[1].__dict__)

        assert course_reflection[0].survey_id == 402311594
        assert course_reflection[0].survey_response_id == 114156931291
        assert course_reflection[0].lms_enrollment_id == 333

        online_learning_goals = list(course_reflection[0].online_learning_goals.all().values_list('answer', flat=True))
        assert online_learning_goals == ['Change careers', 'Learn, Learn and Learn']

        assert course_reflection[0].goal_achieved is False
        assert course_reflection[0].online_learning_goal == 'Get a deep experience', 'open_to_outreach'
        assert course_reflection[0].open_to_outreach is True

        assert course_reflection[0].salary_change is None
        assert course_reflection[0].job_promotion is None
        assert course_reflection[0].learning_experience_importance == ''
        assert course_reflection[0].experience_impacted_goals == ''

        assert course_reflection[0].close_to_goal == '6-12 months'
        assert course_reflection[0].factors_influenced_timeline == 'Quality of edX content'
        assert course_reflection[0].achieve_goal_sooner == 'Nothing, everything is OK'

        assert course_reflection[1].survey_id == 505288401
        assert course_reflection[1].survey_response_id == 505288401000
        assert course_reflection[1].lms_enrollment_id == 4444

        online_learning_goals = list(course_reflection[1].online_learning_goals.all().values_list('answer', flat=True))
        assert online_learning_goals == ['Learn for fun']

        assert course_reflection[1].goal_achieved is True
        assert course_reflection[1].online_learning_goal == 'become a super hero'
        assert course_reflection[1].open_to_outreach is True

        assert course_reflection[1].salary_change is True
        assert course_reflection[1].job_promotion is True
        assert course_reflection[1].learning_experience_importance == 'Extremely important'
        assert course_reflection[1].experience_impacted_goals == 'everything was well planned in the course.'

        assert course_reflection[1].close_to_goal == ''
        assert course_reflection[1].factors_influenced_timeline == ''
        assert course_reflection[1].achieve_goal_sooner == ''

    def verify_survey_export(self):
        """
        Verify that correct timestamp is stored for every survey in `SurveyExport` table.
        """
        for survey_id, survey in MOCK_API_RESPONSES.items():
            survey_date_modified = survey['data'][0]['date_modified']
            assert SurveyExport.last_successfull_export_timestamp(survey_id=survey_id) == survey_date_modified

    @patch('outcome_surveys.management.commands.import_survey_data.LOGGER')
    def test_command_with_ratelimit(self, mocked_logger):
        """
        Verify that management command works as expected in non-commit mode.
        """
        with patch.object(Session, 'get', side_effect=mocked_get_function_with_rate_limit_exception):
            call_command(self.command)
            mocked_logger.info.assert_called_with('Consumed daily api call limit. Can not make more calls.')

    def test_command_with_commit(self):
        """
        Verify that management command works as expected in commit mode.
        """
        assert CourseReflection.objects.count() == 0
        assert CourseGoal.objects.count() == 0
        assert MultiChoiceResponse.objects.count() == 0
        assert SurveyExport.objects.count() == 0

        with patch.object(Session, 'delete'):
            with patch.object(Session, 'get', side_effect=mocked_get_function):
                call_command(self.command, '--commit')

        assert CourseReflection.objects.count() == 2
        assert CourseGoal.objects.count() == 2
        assert MultiChoiceResponse.objects.count() == 6
        assert SurveyExport.objects.count() == 4

        self.verify_course_reflection_response()
        self.verify_course_goal_response()
        self.verify_survey_export()

    def test_command_with_no_lms_enrollment_id(self):
        """
        Verify `clean_lms_enrollment_id` command method returns correct value.
        """
        mock_survey_response = {
            'custom_variables': {}
        }
        assert Command().clean_lms_enrollment_id(mock_survey_response) is None

    def test_command_with_dry_run(self):
        """
        Verify that management command raises correct exception if daily max api call limit has been consumed.
        """
        assert CourseReflection.objects.count() == 0
        assert CourseGoal.objects.count() == 0
        assert MultiChoiceResponse.objects.count() == 0
        assert SurveyExport.objects.count() == 0

        with patch.object(Session, 'delete'):
            with patch.object(Session, 'get', side_effect=mocked_get_function):
                call_command(self.command)

        assert CourseReflection.objects.count() == 0
        assert CourseGoal.objects.count() == 0
        assert MultiChoiceResponse.objects.count() == 0
        assert SurveyExport.objects.count() == 0
