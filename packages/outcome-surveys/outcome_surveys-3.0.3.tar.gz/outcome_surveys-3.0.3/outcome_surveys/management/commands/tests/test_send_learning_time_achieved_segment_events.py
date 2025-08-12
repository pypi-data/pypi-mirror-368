"""
Tests for `send_learning_time_achieved_segment_events` management command.
"""

from unittest import TestCase, mock
from unittest.mock import call, patch

import pytest
from django.core.management import call_command
from django.utils import timezone

from outcome_surveys.constants import SEGMENT_LEARNER_ACHIEVED_LEARNING_TIME_EVENT_TYPE
from outcome_surveys.management.commands import send_learning_time_achieved_segment_events
from outcome_surveys.management.commands.tests.mock_responses import MOCK_QUERY_DATA
from outcome_surveys.models import LearnerCourseEvent


@pytest.mark.django_db
class TestSendSegmentEventsForPreparedLearnersCommand(TestCase):
    """
    Tests `send_learning_time_achieved_segment_events` management command.
    """

    def setUp(self):
        super().setUp()
        self.command = send_learning_time_achieved_segment_events.Command()

    @staticmethod
    def generate_query_data(size=2):
        """
        Generator to return records for processing.
        """
        for i in range(0, len(MOCK_QUERY_DATA), size):
            yield MOCK_QUERY_DATA[i:i + size]

    @patch('outcome_surveys.management.commands.send_learning_time_achieved_segment_events.track')
    @mock.patch(
        'outcome_surveys.management.commands.send_learning_time_achieved_segment_events.Command.fetch_data_from_snowflake'  # nopep8 pylint: disable=line-too-long
    )
    def test_command_dry_run(self, mock_fetch_data_from_snowflake, segment_track_mock):
        """
        Verify that management command does not fire any segment event in dry run mode.
        """
        mock_fetch_data_from_snowflake.return_value = self.generate_query_data()
        mock_path = 'outcome_surveys.management.commands.send_learning_time_achieved_segment_events.log.info'

        with mock.patch(mock_path) as mock_logger:
            call_command(self.command, '--dry-run')
            segment_track_mock.assert_has_calls([])
            assert LearnerCourseEvent.objects.count() == 0

            user_ids = [record['USER_ID'] for record in MOCK_QUERY_DATA]
            mock_logger.assert_has_calls(
                [
                    call('%s Command started.', '[DRY RUN]'),
                    call('%s Processing [%s] rows', '[DRY RUN]', 2),
                    call('%s Processing %s', '[DRY RUN]', MOCK_QUERY_DATA[0]),
                    call('%s Processing %s', '[DRY RUN]', MOCK_QUERY_DATA[1]),
                    call('%s Processing completed of [%s] rows', '[DRY RUN]', 2),
                    call('%s Processing [%s] rows', '[DRY RUN]', 2),
                    call('%s Processing %s', '[DRY RUN]', MOCK_QUERY_DATA[2]),
                    call('%s Processing %s', '[DRY RUN]', MOCK_QUERY_DATA[3]),
                    call('%s Processing completed of [%s] rows', '[DRY RUN]', 2),
                    call('%s Command completed. Segment events triggered for user ids: %s', '[DRY RUN]', user_ids)
                ]
            )

    @patch('outcome_surveys.management.commands.send_learning_time_achieved_segment_events.track')
    @mock.patch(
        'outcome_surveys.management.commands.send_learning_time_achieved_segment_events.Command.fetch_data_from_snowflake'  # nopep8 pylint: disable=line-too-long
    )
    def test_command(self, mock_fetch_data_from_snowflake, segment_track_mock):
        """
        Verify that management command fires segment events with correct data.
        """
        mock_fetch_data_from_snowflake.return_value = self.generate_query_data()

        call_command(self.command)

        expected_segment_calls = [
            call(
                5000,
                SEGMENT_LEARNER_ACHIEVED_LEARNING_TIME_EVENT_TYPE,
                {'course_key': 'UUX+ITAx', 'course_title': 'Intro to Accounting'}
            ),
            call(
                5001,
                SEGMENT_LEARNER_ACHIEVED_LEARNING_TIME_EVENT_TYPE,
                {'course_key': 'BCC+ITC', 'course_title': 'Intro to Calculus'}
            ),
            call(
                5002,
                SEGMENT_LEARNER_ACHIEVED_LEARNING_TIME_EVENT_TYPE,
                {'course_key': 'ABC+CSA', 'course_title': 'Intro to Computer Architecture'}
            ),
            call(
                5003,
                SEGMENT_LEARNER_ACHIEVED_LEARNING_TIME_EVENT_TYPE,
                {'course_key': 'BCC+ITC', 'course_title': 'Intro to Quantum Computing'}
            )
        ]
        segment_track_mock.assert_has_calls(expected_segment_calls)

        sent_events = LearnerCourseEvent.objects.all()
        assert sent_events.count() == len(MOCK_QUERY_DATA)
        for record in MOCK_QUERY_DATA:
            tracked_event = LearnerCourseEvent.objects.get(user_id=record['USER_ID'])
            assert tracked_event.already_sent
            assert str(tracked_event.course_id) == record['COURSERUN_KEY']
            assert tracked_event.data == {
                'course_key': record['COURSE_KEY'],
                'course_title': record['COURSERUN_TITLE']
            }
            assert tracked_event.follow_up_date == timezone.now().date()
            assert tracked_event.event_type == SEGMENT_LEARNER_ACHIEVED_LEARNING_TIME_EVENT_TYPE
