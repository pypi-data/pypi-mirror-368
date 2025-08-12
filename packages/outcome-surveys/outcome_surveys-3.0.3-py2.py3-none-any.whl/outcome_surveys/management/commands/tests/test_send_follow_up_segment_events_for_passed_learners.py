"""
Tests for `send_follow_up_segment_events_for_passed_learners` management command.
"""

from datetime import timedelta
from unittest import TestCase, mock
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.utils import timezone

from outcome_surveys.constants import (
    SEGMENT_LEARNER_PASSED_COURSE_FIRST_TIME_EVENT_TYPE,
    SEGMENT_LEARNER_PASSED_COURSE_FIRST_TIME_FOLLOW_UP_EVENT_TYPE,
)
from outcome_surveys.management.commands import send_follow_up_segment_events_for_passed_learners
from outcome_surveys.models import LearnerCourseEvent


@pytest.mark.django_db
class TestSendFollowupSegmentEventsForPassedLearnersCommand(TestCase):
    """
    Tests `send_follow_up_segment_events_for_passed_learners` management command.
    """

    def setUp(self):
        super().setUp()
        self.command = send_follow_up_segment_events_for_passed_learners.Command()
        self.course_id = 'course-v1:edX+DemoX+Demo_Course'

        self.today = timezone.now().date()
        self.yesterday = timezone.now().date() - timedelta(days=1)
        self.test_data = [
            {
                'user_id': 100,
                'course_id': self.course_id,
                'data': {
                    'LMS_ENROLLMENT_ID': 1001,
                    'COURSE_TITLE': 'An introduction to Calculus',
                    'COURSE_ORG_NAME': 'MathX',
                },
                'follow_up_date': self.today,
                'event_type': SEGMENT_LEARNER_PASSED_COURSE_FIRST_TIME_EVENT_TYPE,
            },
            {
                'user_id': 200,
                'course_id': self.course_id,
                'data': {
                    'LMS_ENROLLMENT_ID': 2001,
                    'COURSE_TITLE': 'An introduction to Python',
                    'COURSE_ORG_NAME': 'PythonX',
                },
                'follow_up_date': self.today,
                'event_type': SEGMENT_LEARNER_PASSED_COURSE_FIRST_TIME_EVENT_TYPE,
            },
            {
                'user_id': 222,
                'course_id': self.course_id,
                'data': {
                    'LMS_ENROLLMENT_ID': 2221,
                    'COURSE_TITLE': 'An introduction to Python',
                    'COURSE_ORG_NAME': 'PythonX',
                },
                'follow_up_date': self.today,
                'event_type': SEGMENT_LEARNER_PASSED_COURSE_FIRST_TIME_EVENT_TYPE,
                'already_sent': True,
            },
            {
                'user_id': 300,
                'course_id': self.course_id,
                'data': {
                    'LMS_ENROLLMENT_ID': 3001,
                    'COURSE_TITLE': 'An introduction to Databases',
                    'COURSE_ORG_NAME': 'DatabaseX',
                },
                'follow_up_date': self.yesterday,
                'event_type': SEGMENT_LEARNER_PASSED_COURSE_FIRST_TIME_EVENT_TYPE,
            },
        ]

        for item in self.test_data:
            LearnerCourseEvent.objects.create(**item)

    def construct_event_call_data(self):
        """
        Construct segment event call data for verification.
        """
        event_call_data = []
        for item in self.test_data:
            if item.get('follow_up_date') == self.today and item.get('already_sent', False) is False:
                event_call_data.append([
                    item.get('user_id'),
                    SEGMENT_LEARNER_PASSED_COURSE_FIRST_TIME_FOLLOW_UP_EVENT_TYPE,
                    item.get('data'),
                ])
        return event_call_data

    @patch('outcome_surveys.management.commands.send_follow_up_segment_events_for_passed_learners.track')
    def test_command_dry_run(self, segment_track_mock):
        """
        Verify that management command does not fire any segment event in dry run mode.
        """
        call_command(self.command, '--dry-run')
        segment_track_mock.assert_has_calls([])

    @patch('outcome_surveys.management.commands.send_follow_up_segment_events_for_passed_learners.track')
    def test_command(self, segment_track_mock):
        """
        Verify that management command fires segment events with correct data.

        * Event should be fired for records having follow_up_date set to today.
        """
        already_sent_records = LearnerCourseEvent.objects.filter(already_sent=True)
        assert already_sent_records.count() == 1
        assert already_sent_records.first().user_id == 222
        already_sent_records_ids = list(already_sent_records.values_list('id', flat=True))

        call_command(self.command)
        expected_segment_event_calls = [mock.call(*event_data) for event_data in self.construct_event_call_data()]
        segment_track_mock.assert_has_calls(expected_segment_event_calls)

        # verify that correct records were upddated in table
        already_sent_records = LearnerCourseEvent.objects.filter(already_sent=True)
        assert already_sent_records.count() == 3
        triggered_event_user_ids = already_sent_records.exclude(
            id__in=already_sent_records_ids
        ).values_list('user_id', flat=True)
        assert list(triggered_event_user_ids) == [100, 200]
