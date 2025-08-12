Change Log
----------

..
   All enhancements and patches to outcome_surveys will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
~~~~~~~~~~

[3.0.3]- 2025-08-11
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* temp: add logs to debug issue with `OperationalError` in `MultiChoiceResponse.save_answers`

[3.0.2]- 2025-07-29
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* fix: use latest version of setuptools

[3.0.1]- 2025-07-08
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* fix: publish to pypi github action

[3.0.0]- 2025-07-07
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* feat: upgrade python version to 3.11

[2.6.0]- 2024-11-06
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Deprecated edx-sphinx-theme and replaced it with sphinx-book-theme

[2.5.1] - 2024-02-22
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Update prepared learners query

[2.5.0] - 2023-11-02
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add management command to trigger segment events for learners who have achieved 30 minutes of learning

[2.4.0] - 2023-03-13
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add support to delete survey responses

[2.3.1] - 2023-03-01
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Remove broad exception

[2.3.0] - 2023-02-27
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Remove null=True from char and text model fields

[2.1.0] - 2023-02-03
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add uniqe constraints on table fields
* Replace `get_or_create`` with custom implementation
* Gracefully exit command upon `SurveyMonkeyDailyRateLimitConsumed` exception

[2.0.0] - 2023-02-01
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Django management command to import data from SurveyMonkey

[1.1.1] - 2022-09-06
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Add `already_sent` boolean field in `LearnerCourseEvent` model to store the state for sent events.
* Set `already_sent`` to `True` in `LearnerCourseEvent` model for each triggered event.

[1.1.0] - 2022-07-14
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Make follow up days configurable


[0.1.0] - 2022-07-06
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Added
_____

* First release on PyPI.
