"""
Management command to import survey data from SurveyMonkey.
"""

import logging

from django.core.management.base import BaseCommand

from outcome_surveys.constants import ENROLLMENT_TYPE_B2B, ENROLLMENT_TYPE_B2C
from outcome_surveys.models import CourseGoal, CourseReflection, SurveyExport
from outcome_surveys.surveymonkey_client import SurveyMonkeyApiClient, SurveyMonkeyDailyRateLimitConsumed

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Example usage:
        $ ./manage.py import_survey_data
    """

    help = 'Import survey data from SurveyMonkey'

    def add_arguments(self, parser):
        """
        Entry point to add arguments.
        """
        parser.add_argument(
            '--commit',
            action='store_true',
            dest='commit',
            default=False,
            help='Dry Run, print log messages without storing the survey data in DB.',
        )

    def surveys(self):
        return [
            {
                "id": 505286548,
                "title": "Course Reflections",
                "type": ENROLLMENT_TYPE_B2B,
                "question_to_field_map": {
                    "62507216": "online_learning_goals",
                    "62512578": "goal_decisions",
                    "62521325": "help_reach_goal",
                    "62521622": "course_rating",
                    "62522012": "course_experience",
                    "62528211": "open_to_outreach",
                }
            },
            {
                "id": 507302428,
                "title": "Course Reflections",
                "type": ENROLLMENT_TYPE_B2C,
                "question_to_field_map": {
                    "81620009": "online_learning_goals",
                    "81620010": "goal_decisions",
                    "81620011": "help_reach_goal",
                    "81620012": "course_rating",
                    "81620013": "course_experience",
                    "81620014": "open_to_outreach",
                }
            },
            {
                "id": 402311594,
                "title": "How are your goals going?",
                "type": ENROLLMENT_TYPE_B2C,
                "question_to_field_map": {
                    "81737604": "online_learning_goals",
                    "81737605": "goal_achieved",

                    # question id when learner selected `Yes` for goal achieved
                    "81737612": "online_learning_goal",
                    # question id when learner selected `No` for goal achieved
                    "81737614": "online_learning_goal",
                    # question id when learner selected `Yes` for goal achieved
                    "81737618": "open_to_outreach",
                    # question id when learner selected `No` for goal achieved
                    "81737617": "open_to_outreach",

                    # question ids when learner selected `Yes` for goal achieved
                    "81737608": "salary_change",
                    "81737609": "job_promotion",
                    "81737610": "learning_experience_importance",
                    "81737611": "experience_impacted_goals",

                    # question ids when learner selected `No` for goal achieved
                    "81737613": "close_to_goal",
                    "81737615": "factors_influenced_timeline",
                    "81737616": "achieve_goal_sooner",
                }
            },
            {
                "id": 505288401,
                "title": "How are your goals going?",
                "type": ENROLLMENT_TYPE_B2B,
                "question_to_field_map": {
                    "62523202": "online_learning_goals",
                    "62524373": "goal_achieved",

                    # question id when learner selected `Yes` for goal achieved
                    "62525140": "online_learning_goal",
                    # question id when learner selected `No` for goal achieved
                    "62525558": "online_learning_goal",
                    # question id when learner selected `Yes` for goal achieved
                    "62527296": "open_to_outreach",
                    # question id when learner selected `No` for goal achieved
                    "62526477": "open_to_outreach",

                    # question ids when learner selected `Yes` for goal achieved
                    "62524671": "salary_change",
                    "62524687": "job_promotion",
                    "62524917": "learning_experience_importance",
                    "62524993": "experience_impacted_goals",

                    # question ids when learner selected `No` for goal achieved
                    "62525469": "close_to_goal",
                    "62525923": "factors_influenced_timeline",
                    "62526270": "achieve_goal_sooner",
                }
            },
        ]

    def last_successfull_export_timestamp(self, survey_id):
        return SurveyExport.last_successfull_export_timestamp(survey_id)

    def transform_boolean_response(self, answer):
        """
        Transform a boolean response.
        """
        options = {"no": False, "yes": True}
        transformed = None

        if answer:
            transformed = options.get(answer[0].lower())

        return transformed

    def transform_single_choice_response(self, answer):
        """
        Transform a single choice text response.
        """
        transformed = None

        if answer:
            transformed = answer[0]

        return transformed

    def transform_online_learning_goals(self, answer):
        """
        Transform a multi choice text response for `online_learning_goals` field.
        """
        transformed = None

        if answer:
            transformed = answer

        return transformed

    def transform_goal_decisions(self, answer):
        """
        Transform a multi choice text response for `goal_decisions` field.
        """
        transformed = None

        if answer:
            transformed = answer

        return transformed

    def transform_course_rating(self, answer):
        """
        Transform for `course_rating` field.
        """
        transformed = None

        if answer:
            transformed = int(answer[0])

        return transformed

    def transform_help_reach_goal(self, answer):
        """
        Transform for `help_reach_goal` field.
        """
        return self.transform_single_choice_response(answer)

    def transform_course_experience(self, answer):
        """
        Transform for `course_experience` field.
        """
        return self.transform_single_choice_response(answer)

    def transform_open_to_outreach(self, answer):
        """
        Transform for `open_to_outreach` field.
        """
        return self.transform_boolean_response(answer)

    def transform_goal_achieved(self, answer):
        """
        Transform for `goal_achieved` field.
        """
        return self.transform_boolean_response(answer)

    def transform_online_learning_goal(self, answer):
        """
        Transform for `online_learning_goal` field.
        """
        return self.transform_single_choice_response(answer)

    def transform_salary_change(self, answer):
        """
        Transform for `salary_change` field.
        """
        return self.transform_boolean_response(answer)

    def transform_job_promotion(self, answer):
        """
        Transform for `job_promotion` field.
        """
        return self.transform_boolean_response(answer)

    def transform_learning_experience_importance(self, answer):
        """
        Transform for `learning_experience_importance` field.
        """
        return self.transform_single_choice_response(answer)

    def transform_experience_impacted_goals(self, answer):
        """
        Transform for `experience_impacted_goals` field.
        """
        return self.transform_single_choice_response(answer)

    def transform_close_to_goal(self, answer):
        """
        Transform for `close_to_goal` field.
        """
        return self.transform_single_choice_response(answer)

    def transform_factors_influenced_timeline(self, answer):
        """
        Transform for `factors_influenced_timeline` field.
        """
        return self.transform_single_choice_response(answer)

    def transform_achieve_goal_sooner(self, answer):
        """
        Transform for `achieve_goal_sooner` field.
        """
        return self.transform_single_choice_response(answer)

    def clean_lms_enrollment_id(self, survey_response):
        """
        Clean for `lms_enrollment_id` field.
        """
        try:
            lms_enrollment_id = int(survey_response["custom_variables"]["e_id"])
        except (ValueError, KeyError):
            lms_enrollment_id = None

        return lms_enrollment_id

    def clean_survey_response(self, survey_schema, survey_response):
        """
        Clean a complete single survey response.
        """
        cleaned = {}
        cleaned["enrollment_type"] = survey_schema["type"]
        cleaned["survey_id"] = int(survey_schema["id"])
        cleaned["survey_response_id"] = int(survey_response["id"])
        cleaned["lms_enrollment_id"] = self.clean_lms_enrollment_id(survey_response)

        question_to_field_map = survey_schema["question_to_field_map"]

        # Set defaults for all questions. This will handle the case where a question was not attempted.
        for field in question_to_field_map.values():
            cleaned[field] = None

        for page in survey_response["pages"]:
            for question in page["questions"]:

                field = question_to_field_map[question["id"]]

                learner_answers = []
                for answer in question["answers"]:
                    if "other_id" in answer:
                        raw_answer = answer["text"].strip()
                    else:
                        raw_answer = answer["simple_text"].strip()

                    learner_answers.append(raw_answer)

                # Perform field specific transformation
                cleaned[field] = getattr(self, f"transform_{field}")(learner_answers)

        return cleaned

    def store_survey_response(self, survey_id, cleaned_survey_response):
        """
        Store a single cleaned survey in database.
        """
        # Course Reflection surveys for B2B and B2C
        if survey_id in (505286548, 507302428):
            CourseReflection.save_response(cleaned_survey_response)

        # Learner Course Goal surveys for B2B and B2C
        if survey_id in (402311594, 505288401):
            CourseGoal.save_response(cleaned_survey_response)

    def handle(self, *args, **options):
        """
        Command's entry point.
        """
        try:
            self.start_command(options)
            self.delete_survey_responses()
        except SurveyMonkeyDailyRateLimitConsumed:
            LOGGER.info("Consumed daily api call limit. Can not make more calls.")

    def start_command(self, options):
        """
        Execute command.
        """
        commit_to_db = options['commit']

        log_prefix = '[IMPORT_SURVEY_DATA]'
        if not commit_to_db:
            log_prefix = '[DRY RUN]'

        LOGGER.info(f'{log_prefix} Command started.')

        for survey_schema in self.surveys():

            survey_id = survey_schema['id']
            last_successfull_export_timestamp = self.last_successfull_export_timestamp(survey_id)
            client = SurveyMonkeyApiClient(survey_id, last_successfull_export_timestamp)
            url = client.get_endpoint_url()

            while True:
                LOGGER.info(
                    "%s Fetching survey data. SurveyID: [%s], LastSuccessfullExportTimestamp: [%s], URL: [%s]",
                    log_prefix,
                    survey_id,
                    last_successfull_export_timestamp,
                    url
                )

                # fetch 100 responses at a time
                survey_responses = client.fetch_survey_responses(url)

                survey_responses = survey_responses.json()
                date_modified = None

                # for each response, clean and store the reponse in database
                for survey_response in survey_responses.get('data'):

                    cleaned_survey_response = self.clean_survey_response(survey_schema, survey_response)

                    if commit_to_db:
                        self.store_survey_response(survey_id, cleaned_survey_response)

                    LOGGER.info(
                        "%s Data exported for. Survey: [%s], SurveyResponseId: [%s], LMSEnrollmentId: [%s]",
                        log_prefix,
                        survey_id,
                        cleaned_survey_response["survey_response_id"],
                        cleaned_survey_response["lms_enrollment_id"],
                    )

                    date_modified = survey_response['date_modified']

                if commit_to_db:
                    SurveyExport.save_export_timestamp(survey_id, date_modified)

                LOGGER.info(
                    "%s Successfully exported data for survey [%s] till date [%s]",
                    log_prefix,
                    survey_id,
                    date_modified
                )

                # fetch more data if next url is present else break and move to next survey
                url = survey_responses.get('links').get('next')
                if url is None:
                    break

            LOGGER.info("%s Completed survey export for ID: [%s]", log_prefix, survey_id)

        LOGGER.info("%s Command completed. Completed export for all surveys.", log_prefix)

    def delete_survey_responses(self):
        """
        Delete as many as possible survey reponses.
        """
        for survey_schema in self.surveys():
            survey_id = survey_schema['id']
            last_successfull_export_timestamp = self.last_successfull_export_timestamp(survey_id)
            client = SurveyMonkeyApiClient(survey_id)
            # Delete all responses of a survey before `last_successfull_export_timestamp`
            client.delete_survey_responses(end_created_at=last_successfull_export_timestamp)
