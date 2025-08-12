#!/usr/bin/env python
"""
Tests for the `outcome_surveys` signals module.
"""

from datetime import timedelta
from unittest import TestCase

import pytest
from django.utils import timezone

from outcome_surveys.constants import SEGMENT_LEARNER_PASSED_COURSE_FIRST_TIME_EVENT_TYPE
from outcome_surveys.models import LearnerCourseEvent
from outcome_surveys.signals import schedule_course_passed_first_time_follow_up_segment_event


@pytest.mark.django_db
class TestSignals(TestCase):
    """
    Tests class for outcome_surveys signals.
    """

    def setUp(self):
        super().setUp()

        self.user_id = 1222
        self.course_id = 'course-v1:edX+DemoX+Demo_Course'
        self.event_properties = {
            'LMS_ENROLLMENT_ID': 2221,
            'COURSE_TITLE': 'edX Demo Course',
            'COURSE_ORG_NAME': 'edX',
        }
        self.ninety_day_follow_up_date = timezone.now().date() + timedelta(days=90)

    def test_handle_segment_event_fired_for_learner_passed_course_first_time(self):
        """
        Verify that `schedule_course_passed_first_time_follow_up_segment_event` signal handler work as expected.
        """
        schedule_course_passed_first_time_follow_up_segment_event(
            None,
            self.user_id,
            self.course_id,
            self.event_properties
        )

        assert LearnerCourseEvent.objects.count() == 1

        learner_course_event = LearnerCourseEvent.objects.get(
            user_id=self.user_id,
            course_id=self.course_id,
            follow_up_date=self.ninety_day_follow_up_date,
            event_type=SEGMENT_LEARNER_PASSED_COURSE_FIRST_TIME_EVENT_TYPE
        )

        assert learner_course_event.data == self.event_properties
