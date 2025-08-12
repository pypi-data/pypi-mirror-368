"""
Database models for outcome_surveys.
"""
import logging

from django.db import models
from django.db.utils import OperationalError
from jsonfield import JSONField
# from django.db import models
from model_utils.models import TimeStampedModel
from opaque_keys.edx.django.models import CourseKeyField

from outcome_surveys.constants import (
    ENROLLMENT_TYPE_B2C,
    SEGMENT_LEARNER_ACHIEVED_LEARNING_TIME_EVENT_TYPE,
    SEGMENT_LEARNER_PASSED_COURSE_FIRST_TIME_EVENT_TYPE,
)

LOGGER = logging.getLogger(__name__)


class LearnerCourseEvent(TimeStampedModel):
    """
    Learner Course Event model for tracking passed event sent to learners.

    .. no_pii:
    """

    user_id = models.IntegerField()
    course_id = CourseKeyField(blank=False, null=False, max_length=255)
    data = JSONField()
    follow_up_date = models.DateField()

    EVENT_CHOICES = [
        (SEGMENT_LEARNER_PASSED_COURSE_FIRST_TIME_EVENT_TYPE, SEGMENT_LEARNER_PASSED_COURSE_FIRST_TIME_EVENT_TYPE),
        (SEGMENT_LEARNER_ACHIEVED_LEARNING_TIME_EVENT_TYPE, SEGMENT_LEARNER_ACHIEVED_LEARNING_TIME_EVENT_TYPE),
    ]
    event_type = models.CharField(
        max_length=255,
        choices=EVENT_CHOICES,
        default=SEGMENT_LEARNER_PASSED_COURSE_FIRST_TIME_EVENT_TYPE,
    )
    already_sent = models.BooleanField(default=False)

    class Meta:
        """
        Meta class for LearnerCourseEvent.
        """

        app_label = "outcome_surveys"
        indexes = [
            models.Index(fields=['follow_up_date']),
            models.Index(fields=['created']),
        ]

    def __str__(self):
        """
        Get a string representation of this model instance.
        """
        # TODO: return a string appropriate for the data fields
        return '<LearnerCourseEvent, ID: {}>'.format(self.id)


class MultiChoiceResponse(TimeStampedModel):
    """
    Learner's survey response for multi choice questions.

    .. no_pii:
    """

    answer = models.TextField()

    @staticmethod
    def save_answers(parent, related_field_name, user_choices):
        """
        Store answers.
        """
        answers = []
        for user_choice in user_choices:
            try:
                answer = MultiChoiceResponse.objects.filter(answer=user_choice).first()
            except OperationalError:
                LOGGER.info(
                    "[OperationalError] Parent: [%s], Related Field: [%s], User Choice: [%s], User Choices: [%s]",
                    parent.__class__.__name__,
                    related_field_name,
                    user_choice,
                    user_choices
                )
                raise
            if answer is None:
                answer = MultiChoiceResponse.objects.create(answer=user_choice)
            answers.append(answer)

        instance_related_field = getattr(parent, related_field_name)
        instance_related_field.set(answers)

    class Meta:
        """
        Meta class for MultiChoiceResponse.
        """

        app_label = "outcome_surveys"

    def __str__(self):
        """
        Get a string representation of this model instance.
        """
        return f'<answer: {self.answer}>'


class CourseReflection(TimeStampedModel):
    """
    Learner's reflections about a Course.

    .. no_pii:
    """

    survey_id = models.IntegerField()
    survey_response_id = models.BigIntegerField()
    enrollment_type = models.CharField(
        max_length=16,
        default=ENROLLMENT_TYPE_B2C,
        help_text=("Enrollment type. B2C or B2B"),
    )
    lms_enrollment_id = models.IntegerField(
        null=True,
        help_text=("Learner's LMS course enrollment id."),
    )
    # multiple choice
    online_learning_goals = models.ManyToManyField(
        MultiChoiceResponse,
        related_name="+",
        help_text=("What is your goal with online learning?")
    )
    # multiple choice
    goal_decisions = models.ManyToManyField(
        MultiChoiceResponse,
        related_name="+",
        help_text=("How did you decide on that goal?")
    )
    help_reach_goal = models.CharField(
        max_length=256,
        default="",
        help_text=("How confident are you that the learning you did in this course will help you reach your goal?")
    )
    course_rating = models.IntegerField(
        null=True,
        help_text=("How would you rate the quality of this course?")
    )
    course_experience = models.TextField(
        default="",
        help_text=("Is there anything else you'd like to add about your experience in the course?")
    )
    open_to_outreach = models.BooleanField(
        null=True,
        help_text=("Would you be open to someone from edX reaching out to learn more about your experience?")
    )

    @classmethod
    def save_response(cls, response):
        """
        Save a survey response.
        """
        survey_response = response.copy()

        online_learning_goals = survey_response.pop("online_learning_goals") or []
        goal_decisions = survey_response.pop("goal_decisions") or []
        survey_id = survey_response.pop('survey_id')
        survey_response_id = survey_response.pop('survey_response_id')

        # None to "" conversion for char and text fields where default is set to ""
        empty_string_fields = ('help_reach_goal', 'course_experience')
        for field in empty_string_fields:
            survey_response[field] = survey_response[field] or ""

        course_reflection, __ = cls.objects.update_or_create(
            survey_id=survey_id,
            survey_response_id=survey_response_id,
            defaults=survey_response
        )

        MultiChoiceResponse.save_answers(course_reflection, 'online_learning_goals', online_learning_goals)
        MultiChoiceResponse.save_answers(course_reflection, 'goal_decisions', goal_decisions)

    class Meta:
        """
        Meta class for CourseReflection.
        """

        app_label = "outcome_surveys"
        unique_together = ("survey_id", "survey_response_id",)
        indexes = [
            models.Index(fields=['survey_id', 'survey_response_id']),
            models.Index(fields=['survey_response_id']),
            models.Index(fields=['lms_enrollment_id']),
        ]

    def __str__(self):
        """
        Get a string representation of this model instance.
        """
        return f'<SurveyId: [{self.survey_id}], ResponseId: [{self.survey_response_id}]>'


class CourseGoal(TimeStampedModel):
    """
    Learner's feedback about course goal.

    .. no_pii:
    """

    survey_id = models.IntegerField()
    survey_response_id = models.BigIntegerField()
    enrollment_type = models.CharField(
        max_length=16,
        default=ENROLLMENT_TYPE_B2C,
        help_text=("Enrollment type. B2C or B2B"),
    )
    lms_enrollment_id = models.IntegerField(
        null=True,
        help_text=("Learner's LMS course enrollment id."),
    )
    #  common fields
    # multiple choice
    online_learning_goals = models.ManyToManyField(
        MultiChoiceResponse,
        related_name="+",
        help_text=("What is your goal with online learning?")
    )
    goal_achieved = models.BooleanField(
        null=True,
        help_text=("Did you achieve that goal?")
    )
    online_learning_goal = models.TextField(
        default="",
        help_text=("In a few words, describe your goal for online learning.")
    )
    open_to_outreach = models.BooleanField(
        null=True,
        help_text=("Would you be open to someone from edX reaching out to learn more about your experience?")
    )

    # fields for passed learners
    salary_change = models.BooleanField(
        null=True,
        help_text=("Did you experience any salary changes as a result of meeting this goal?")
    )
    job_promotion = models.BooleanField(
        null=True,
        help_text=("Did you experience a job promotion or job change as a result of meeting this goal?")
    )
    learning_experience_importance = models.CharField(
        max_length=256,
        default="",
        help_text=("How important was the learning experience you had on edX for achieving that goal?")
    )
    experience_impacted_goals = models.TextField(
        default="",
        help_text=("Is there anything else you’d like to share about how your experience on edX impacted your goals?")
    )

    # fields for failed learners
    close_to_goal = models.CharField(
        max_length=256,
        default="",
        help_text=("How close are you from achieving your goal?")
    )
    factors_influenced_timeline = models.TextField(
        default="",
        help_text=("What factors influenced the timeline for your goal?")
    )
    achieve_goal_sooner = models.TextField(
        default="",
        help_text=("Is there anything that could have gone different with your experience on edX to help you achieve your goal sooner?")  # nopep8 pylint: disable=line-too-long, superfluous-parens
    )

    @classmethod
    def save_response(cls, response):
        """
        Save a survey response.
        """
        survey_response = response.copy()

        online_learning_goals = survey_response.pop("online_learning_goals") or []
        survey_id = survey_response.pop('survey_id')
        survey_response_id = survey_response.pop('survey_response_id')

        # None to "" conversion for char and text fields where default is set to ""
        empty_string_fields = (
            'close_to_goal',
            'achieve_goal_sooner',
            'online_learning_goal',
            'experience_impacted_goals',
            'factors_influenced_timeline',
            'learning_experience_importance',
        )
        for field in empty_string_fields:
            survey_response[field] = survey_response[field] or ""

        course_goal, __ = cls.objects.update_or_create(
            survey_id=survey_id,
            survey_response_id=survey_response_id,
            defaults=survey_response
        )

        MultiChoiceResponse.save_answers(course_goal, 'online_learning_goals', online_learning_goals)

    class Meta:
        """
        Meta class for CourseGoal.
        """

        app_label = "outcome_surveys"
        unique_together = ("survey_id", "survey_response_id",)
        indexes = [
            models.Index(fields=['survey_id', 'survey_response_id']),
            models.Index(fields=['survey_response_id']),
            models.Index(fields=['lms_enrollment_id']),
        ]

    def __str__(self):
        """
        Get a string representation of this model instance.
        """
        return f'<SurveyId: [{self.survey_id}], ResponseId: [{self.survey_response_id}]>'


class SurveyExport(TimeStampedModel):
    """
    Survey export metadata.

    .. no_pii:
    """

    survey_id = models.IntegerField(null=False)
    last_successfull_export_at = models.DateTimeField(null=False)

    @classmethod
    def save_export_timestamp(cls, survey_id, timestamp):
        """
        Save `last_successfull_export_at` for `survey_id`.
        """
        if timestamp:
            cls.objects.update_or_create(survey_id=survey_id, defaults={"last_successfull_export_at": timestamp})

    @classmethod
    def last_successfull_export_timestamp(cls, survey_id):
        """
        Return `last_successfull_export_at` in ISO format.
        """
        try:
            return cls.objects.get(survey_id=survey_id).last_successfull_export_at.isoformat()
        except SurveyExport.DoesNotExist:
            return None

    class Meta:
        """
        Meta class for SurveyExport.
        """

        app_label = "outcome_surveys"

    def __str__(self):
        """
        Get a string representation of this model instance.
        """
        last_export_ts = self.last_successfull_export_timestamp(self.survey_id)
        return f'<SurveyId: [{self.survey_id}], LastExportAt: [{last_export_ts}]>'
