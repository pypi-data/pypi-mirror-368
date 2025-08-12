"""
Send segment events for passed learners so that Braze can send 90 day follow up email.
"""

import logging

import snowflake.connector
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from snowflake.connector import DictCursor

from outcome_surveys.constants import SEGMENT_LEARNER_ACHIEVED_LEARNING_TIME_EVENT_TYPE
from outcome_surveys.models import LearnerCourseEvent

try:
    from common.djangoapps.track.segment import track
except ImportError:
    track = None

log = logging.getLogger(__name__)

ENTERPRISE = settings.ENTERPRISE_VSF_UUID
QUERY = f'''
WITH prepared_learners AS (
    SELECT
        lms_user_id as user_id
    FROM
        prod.enterprise.verizon_internal_reporting
    WHERE
        is_prepared_learner=TRUE
    AND
        lms_user_id NOT IN (
            -- filter learners who already emitted this event
            SELECT
                user_id
            FROM
                PROD.LMS.OUTCOME_SURVEYS_LEARNERCOURSEEVENT
            WHERE
                event_type = 'edx.course.learner.achieved.learning.time'
            AND
                already_sent = TRUE
        )
),

last_course as (
-- Get the last courserun the user interacted with.
-- Since it is captured at the date levels, ties will be common
-- in the dataset. Break the ties by getting the course run
-- with the most engagement on the last day of engagement.

select
    user_id,
    courserun_key
FROM
    PROD.BUSINESS_INTELLIGENCE.LEARNING_TIME
WHERE
    enterprise_customer_uuid='{ENTERPRISE}'
QUALIFY
    -- get latest date, highest learning on date, per learner.
    ROW_NUMBER() OVER (PARTITION by user_id ORDER BY date DESC, learning_time_seconds DESC) = 1
)

-- join it all together.
select
    pl.user_id,
    runs.courserun_key,
    runs.course_key,
    runs.courserun_title
from
    prepared_learners pl
inner join
    last_course lc
on
    pl.user_id = lc.user_id
left join
    prod.core.dim_courseruns runs
on
    lc.courserun_key = runs.courserun_key
'''
NUM_ROWS_TO_FETCH = 5000
BULK_CREATE_BATCH_SIZE = 500


class Command(BaseCommand):
    """
    Example usage:
        $ ./manage.py send_learning_time_achieved_segment_events
    """

    help = 'Send follow up segment events for passed learners.'

    def add_arguments(self, parser):
        """
        Entry point to add arguments.
        """
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Dry Run, print log messages without firing the segment event.',
        )

    def fetch_data_from_snowflake(self, log_prefix):
        """
        Get query results from Snowflake and yield each row.
        """
        connection = snowflake.connector.connect(
            user=settings.SNOWFLAKE_SERVICE_USER,
            password=settings.SNOWFLAKE_SERVICE_USER_PASSWORD,
            account='edx.us-east-1',
            database='prod'
        )
        cursor = connection.cursor(DictCursor)
        try:
            log.info('%s Executing query', log_prefix)
            cursor.execute(QUERY)
            while True:
                log.info('%s Fetching results', log_prefix)
                rows = cursor.fetchmany(NUM_ROWS_TO_FETCH)
                log.info('%s Rows Fetched: [%s]', log_prefix, len(rows))
                if len(rows) == 0:
                    break

                yield rows
        finally:
            log.info('%s Closing cursor', log_prefix)
            cursor.close()
            log.info('%s Closing connection', log_prefix)
            connection.close()

    def handle(self, *args, **options):
        """
        Command's entry point.
        """
        fire_event = not options['dry_run']

        log_prefix = '[SEND_LEARNING_TIME_ACHIEVED_SEGMENT_EVENTS]'
        if not fire_event:
            log_prefix = '[DRY RUN]'

        log.info('%s Command started.', log_prefix)

        user_ids = []
        for rows_chunk in self.fetch_data_from_snowflake(log_prefix):
            log.info('%s Processing [%s] rows', log_prefix, len(rows_chunk))

            triggered_event_records = []
            for row in rows_chunk:
                log.info('%s Processing %s', log_prefix, row)

                user_id = row['USER_ID']
                course_key = row['COURSE_KEY']
                courserun_key = row['COURSERUN_KEY']
                course_title = row['COURSERUN_TITLE']
                event_properties = {
                    'course_key': course_key,
                    'course_title': course_title,
                }
                user_ids.append(user_id)

                if fire_event:
                    track(
                        user_id,
                        SEGMENT_LEARNER_ACHIEVED_LEARNING_TIME_EVENT_TYPE,
                        event_properties
                    )
                    triggered_event_records.append(
                        LearnerCourseEvent(
                            user_id=user_id,
                            course_id=courserun_key,
                            data=event_properties,
                            follow_up_date=timezone.now().date(),
                            event_type=SEGMENT_LEARNER_ACHIEVED_LEARNING_TIME_EVENT_TYPE,
                            already_sent=True,
                        )
                    )
                    log.info(
                        "%s Segment event triggered. Event: [%s], Properties: [%s]",
                        log_prefix,
                        SEGMENT_LEARNER_ACHIEVED_LEARNING_TIME_EVENT_TYPE,
                        event_properties
                    )

            if triggered_event_records:
                LearnerCourseEvent.objects.bulk_create(triggered_event_records, batch_size=BULK_CREATE_BATCH_SIZE)

            log.info('%s Processing completed of [%s] rows', log_prefix, len(rows_chunk))

        log.info("%s Command completed. Segment events triggered for user ids: %s", log_prefix, user_ids)
