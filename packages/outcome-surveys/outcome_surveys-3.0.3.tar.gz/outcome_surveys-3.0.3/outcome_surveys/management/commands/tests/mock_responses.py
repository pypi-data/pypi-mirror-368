"""
Mock responses for testing.
"""


MOCK_API_RESPONSES = {
    "505286548": {
        "per_page": 100,
        "page": 1,
        "total": 222,
        "links": {
            "self": "https://api.surveymonkey.com/v3/surveys/505286548/responses/bulk?simple=True&sort_order=ASC&per_page=100&page=1",  # nopep8 pylint: disable=line-too-long
            "previous": "https://api.surveymonkey.com/v3/surveys/505286548/responses/bulk?simple=True&sort_order=ASC&per_page=100&page=2",  # nopep8 pylint: disable=line-too-long
            "last": "https://api.surveymonkey.com/v3/surveys/505286548/responses/bulk?simple=True&sort_order=ASC&per_page=100&page=63"  # nopep8 pylint: disable=line-too-long
        },
        "data": [{
            "id": "118086896063",
            "survey_id": "505286548",
            "custom_variables": {
                "e_id": "1"
            },
            "date_modified": "2022-07-26T10:56:10+00:00",
            "date_created": "2022-07-26T10:52:29+00:00",
            "pages": [
                {
                    "id": "30004913",
                    "questions": [
                        {
                            "id": "62507216",
                            "answers": [
                                {
                                    "choice_id": "645789037",
                                    "simple_text": "Learn valuable skills"
                                }
                            ],
                            "family": "multiple_choice",
                            "subtype": "vertical",
                            "heading": "What is your goal with online learning?"
                        },
                        {
                            "id": "62512578",
                            "answers": [
                                {
                                    "other_id": "645789046",
                                    "text": "I need more skills",
                                    "simple_text": "Other | I need more skills"
                                }
                            ],
                            "family": "multiple_choice",
                            "subtype": "vertical",
                            "heading": "How did you decide on that goal?"
                        },
                        {
                            "id": "62521325",
                            "answers": [
                                {
                                    "choice_id": "645789052",
                                    "simple_text": "Somewhat confident"
                                }
                            ],
                            "family": "single_choice",
                            "subtype": "vertical",
                            "heading": "How confident are you that the learning you did in this course will help you reach your goal?"  # nopep8 pylint: disable=line-too-long
                        },
                        {
                            "id": "62521622",
                            "answers": [
                                {
                                    "choice_id": "645789061",
                                    "row_id": "645789056",
                                    "choice_metadata": {
                                        "weight": "5"
                                    },
                                    "simple_text": "5"
                                }
                            ],
                            "family": "matrix",
                            "subtype": "rating",
                            "heading": "How would you rate the quality of this course?"
                        },
                        {
                            "id": "62522012",
                            "answers": [
                                {
                                    "tag_data": [],
                                    "text": "Keep up the good work",
                                    "simple_text": "Keep up the good work"
                                }
                            ],
                            "family": "open_ended",
                            "subtype": "essay",
                            "heading": "Is there anything else you'd like to add about your experience in the course?"
                        },
                        {
                            "id": "62528211",
                            "answers": [
                                {
                                    "choice_id": "645789065",
                                    "simple_text": "No"
                                }
                            ],
                            "family": "single_choice",
                            "subtype": "vertical",
                            "heading": "Would you be open to someone from edX reaching out to learn more about your experience?"  # nopep8 pylint: disable=line-too-long
                        }
                    ]
                }
            ]
        }]
    },
    "507302428": {
        "per_page": 100,
        "page": 1,
        "total": 222,
        "links": {
            "self": "https://api.surveymonkey.com/v3/surveys/507302428/responses/bulk?simple=True&sort_order=ASC&per_page=100&page=1",  # nopep8 pylint: disable=line-too-long
            "previous": "https://api.surveymonkey.com/v3/surveys/507302428/responses/bulk?simple=True&sort_order=ASC&per_page=100&page=2",  # nopep8 pylint: disable=line-too-long
            "last": "https://api.surveymonkey.com/v3/surveys/507302428/responses/bulk?simple=True&sort_order=ASC&per_page=100&page=63"  # nopep8 pylint: disable=line-too-long
        },
        "data": [{
            "id": "118086896063",
            "survey_id": "507302428",
            "custom_variables": {
                "e_id": "22"
            },
            "date_modified": "2022-07-26T10:56:10+00:00",
            "date_created": "2022-07-26T10:52:29+00:00",
            "pages": [
                {
                    "id": "30004913",
                    "questions": [
                        {
                            "id": "81620009",
                            "answers": [
                                {
                                    "choice_id": "645789037",
                                    "simple_text": "Learn for fun"
                                },
                                {
                                    "choice_id": "645789037",
                                    "simple_text": "Learn valuable skills"
                                }
                            ],
                            "family": "multiple_choice",
                            "subtype": "vertical",
                            "heading": "What is your goal with online learning?"
                        },
                        {
                            "id": "81620010",
                            "answers": [
                                {
                                    "other_id": "645789046",
                                    "text": "I am hungry to learn",
                                    "simple_text": "Other | I am hungry to learn"
                                }
                            ],
                            "family": "multiple_choice",
                            "subtype": "vertical",
                            "heading": "How did you decide on that goal?"
                        },
                        {
                            "id": "81620011",
                            "answers": [
                                {
                                    "choice_id": "645789052",
                                    "simple_text": "Very confident"
                                }
                            ],
                            "family": "single_choice",
                            "subtype": "vertical",
                            "heading": "How confident are you that the learning you did in this course will help you reach your goal?"  # nopep8 pylint: disable=line-too-long
                        },
                        {
                            "id": "81620012",
                            "answers": [
                                {
                                    "choice_id": "645789061",
                                    "row_id": "645789056",
                                    "choice_metadata": {
                                        "weight": "4"
                                    },
                                    "simple_text": "4"
                                }
                            ],
                            "family": "matrix",
                            "subtype": "rating",
                            "heading": "How would you rate the quality of this course?"
                        },
                        {
                            "id": "81620013",
                            "answers": [
                                {
                                    "tag_data": [],
                                    "text": "Course content needs to be updated",
                                    "simple_text": "Course content needs to be updated"
                                }
                            ],
                            "family": "open_ended",
                            "subtype": "essay",
                            "heading": "Is there anything else you'd like to add about your experience in the course?"
                        },
                        {
                            "id": "81620014",
                            "answers": [
                                {
                                    "choice_id": "645789065",
                                    "simple_text": "Yes"
                                }
                            ],
                            "family": "single_choice",
                            "subtype": "vertical",
                            "heading": "Would you be open to someone from edX reaching out to learn more about your experience?"  # nopep8 pylint: disable=line-too-long
                        }
                    ]
                }
            ]
        }]
    },
    "402311594": {
        "per_page": 100,
        "page": 1,
        "total": 222,
        "links": {
            "self": "https://api.surveymonkey.com/v3/surveys/402311594/responses/bulk?simple=True&sort_order=ASC&per_page=100&page=1",  # nopep8 pylint: disable=line-too-long
            "previous": "https://api.surveymonkey.com/v3/surveys/402311594/responses/bulk?simple=True&sort_order=ASC&per_page=100&page=2",  # nopep8 pylint: disable=line-too-long
            "last": "https://api.surveymonkey.com/v3/surveys/402311594/responses/bulk?simple=True&sort_order=ASC&per_page=100&page=63"  # nopep8 pylint: disable=line-too-long
        },
        "data": [{
            "id": "114156931291",
            "survey_id": "402311594",
            "custom_variables": {
                "e_id": "333"
            },
            "date_modified": "2022-10-27T01:57:11+00:00",
            "date_created": "2022-10-27T01:56:59+00:00",
            "pages": [
                {
                    "id": "30027973",
                    "questions": [
                        {
                            "id": "81737604",
                            "answers": [
                                {
                                    "choice_id": "645928779",
                                    "simple_text": "Change careers"
                                },
                                {
                                    "other_id": "645928783",
                                    "text": "Learn, Learn and Learn",
                                    "simple_text": "Other | Learn, Learn and Learn"
                                }
                            ],
                            "family": "multiple_choice",
                            "subtype": "vertical",
                            "heading": "What is your goal with online learning?"
                        },
                        {
                            "id": "81737605",
                            "answers": [
                                {
                                    "choice_id": "645928788",
                                    "simple_text": "No"
                                }
                            ],
                            "family": "single_choice",
                            "subtype": "vertical",
                            "heading": "Did you achieve that goal?"
                        }
                    ]
                },
                {
                    "id": "30027974",
                    "questions": []
                },
                {
                    "id": "30027975",
                    "questions": [
                        {
                            "id": "81737614",
                            "answers": [
                                {
                                    "tag_data": [],
                                    "text": "Get a deep experience",
                                    "simple_text": "Get a deep experience"
                                }
                            ],
                            "family": "open_ended",
                            "subtype": "essay",
                            "heading": "In a few words, describe your goal for online learning."
                        },
                        {
                            "id": "81737613",
                            "answers": [
                                {
                                    "choice_id": "645928806",
                                    "simple_text": "6-12 months"
                                }
                            ],
                            "family": "single_choice",
                            "subtype": "vertical",
                            "heading": "How close are you from achieving your goal?"
                        },
                        {
                            "id": "81737615",
                            "answers": [
                                {
                                    "choice_id": "645928812",
                                    "simple_text": "Quality of edX content"
                                }
                            ],
                            "family": "single_choice",
                            "subtype": "vertical",
                            "heading": "What factors influenced the timeline for your goal?"
                        },
                        {
                            "id": "81737616",
                            "answers": [
                                {
                                    "tag_data": [],
                                    "text": "Nothing, everything is OK",
                                    "simple_text": "Nothing, everything is OK"
                                }
                            ],
                            "family": "open_ended",
                            "subtype": "essay",
                            "heading": "Is there anything that could have gone different with your experience on edX to help you achieve your goal sooner?"  # nopep8 pylint: disable=line-too-long
                        },
                        {
                            "id": "81737617",
                            "answers": [
                                {
                                    "choice_id": "645928818",
                                    "simple_text": "Yes"
                                }
                            ],
                            "family": "single_choice",
                            "subtype": "vertical",
                            "heading": "Would you be open to someone from edX reaching out to learn more about your experience?"  # nopep8 pylint: disable=line-too-long
                        }
                    ]
                }
            ]
        }]
    },
    "505288401": {
        "per_page": 100,
        "page": 1,
        "total": 222,
        "links": {
            "self": "https://api.surveymonkey.com/v3/surveys/505288401/responses/bulk?simple=True&sort_order=ASC&per_page=100&page=1",  # nopep8 pylint: disable=line-too-long
            "previous": "https://api.surveymonkey.com/v3/surveys/505288401/responses/bulk?simple=True&sort_order=ASC&per_page=100&page=2",  # nopep8 pylint: disable=line-too-long
            "last": "https://api.surveymonkey.com/v3/surveys/505288401/responses/bulk?simple=True&sort_order=ASC&per_page=100&page=63"  # nopep8 pylint: disable=line-too-long
        },
        "data": [{
            "id": "505288401000",
            "survey_id": "505288401",
            "custom_variables": {
                "e_id": "4444"
            },
            "date_modified": "2022-10-27T01:57:11+00:00",
            "date_created": "2022-10-27T01:56:59+00:00",
            "pages": [
                {
                    "id": "25597930",
                    "questions": [
                        {
                            "id": "62523202",
                            "answers": [
                                {
                                    "choice_id": "517013293",
                                    "simple_text": "Learn for fun"
                                }
                            ],
                            "family": "multiple_choice",
                            "subtype": "vertical",
                            "heading": "What is your goal with online learning?"
                        },
                        {
                            "id": "62524373",
                            "answers": [
                                {
                                    "choice_id": "517021420",
                                    "simple_text": "Yes"
                                }
                            ],
                            "family": "single_choice",
                            "subtype": "vertical",
                            "heading": "Did you achieve that goal?"
                        }
                    ]
                },
                {
                    "id": "25598105",
                    "questions": [
                        {
                            "id": "62525140",
                            "answers": [
                                {
                                    "tag_data": [],
                                    "text": "become a super hero",
                                    "simple_text": "become a super hero"
                                }
                            ],
                            "family": "open_ended",
                            "subtype": "essay",
                            "heading": "In a few words, describe your goal for online learning."
                        },
                        {
                            "id": "62524671",
                            "answers": [
                                {
                                    "choice_id": "517023554",
                                    "simple_text": "Yes"
                                }
                            ],
                            "family": "single_choice",
                            "subtype": "vertical",
                            "heading": " Did you experience any salary changes as a result of meeting this goal?"
                        },
                        {
                            "id": "62524687",
                            "answers": [
                                {
                                    "choice_id": "517023620",
                                    "simple_text": "Yes"
                                }
                            ],
                            "family": "single_choice",
                            "subtype": "vertical",
                            "heading": "Did you experience a job promotion or job change as a result of meeting this goal?"  # nopep8 pylint: disable=line-too-long
                        },
                        {
                            "id": "62524917",
                            "answers": [
                                {
                                    "choice_id": "517024966",
                                    "simple_text": "Extremely important"
                                }
                            ],
                            "family": "single_choice",
                            "subtype": "vertical",
                            "heading": "How important was the learning experience you had on edX for achieving that goal?"  # nopep8 pylint: disable=line-too-long
                        },
                        {
                            "id": "62524993",
                            "answers": [
                                {
                                    "tag_data": [],
                                    "text": "everything was well planned in the course.",
                                    "simple_text": "everything was well planned in the course."
                                }
                            ],
                            "family": "open_ended",
                            "subtype": "essay",
                            "heading": "Is there anything else you’d like to share about how your experience on edX impacted your goals?"  # nopep8 pylint: disable=line-too-long
                        },
                        {
                            "id": "62527296",
                            "answers": [
                                {
                                    "choice_id": "517038686",
                                    "simple_text": "Yes"
                                }
                            ],
                            "family": "single_choice",
                            "subtype": "vertical",
                            "heading": "Would you be open to someone from edX reaching out to learn more about your experience?"  # nopep8 pylint: disable=line-too-long
                        }
                    ]
                },
                {
                    "id": "25598001",
                    "questions": []
                }
            ]
        }]
    },
}


MOCK_RESPONSE_HEADERS = {
    "X-Ratelimit-App-Global-Minute-Limit": 5,
    "X-Ratelimit-App-Global-Minute-Remaining": 3,
    "X-Ratelimit-App-Global-Minute-Reset": 20,
    "X-Ratelimit-App-Global-Day-Limit": 20,
    "X-Ratelimit-App-Global-Day-Remaining": 17,
    "X-Ratelimit-App-Global-Day-Reset": 120,
}


MOCK_QUERY_DATA = [
    {
        'USER_ID': 5000,
        'LEARNING_TIME_SECONDS': 2000,
        'COURSERUN_KEY': 'course-v1:UUX+ITAx+1T2022',
        'COURSE_KEY': 'UUX+ITAx',
        'COURSERUN_TITLE': 'Intro to Accounting'
    },
    {
        'USER_ID': 5001,
        'LEARNING_TIME_SECONDS': 2500,
        'COURSERUN_KEY': 'course-v1:BCC+ITC+1T2023',
        'COURSE_KEY': 'BCC+ITC',
        'COURSERUN_TITLE': 'Intro to Calculus'
    },
    {
        'USER_ID': 5002,
        'LEARNING_TIME_SECONDS': 1800,
        'COURSERUN_KEY': 'course-v1:ABC+CSA+1T2023',
        'COURSE_KEY': 'ABC+CSA',
        'COURSERUN_TITLE': 'Intro to Computer Architecture'
    },
    {
        'USER_ID': 5003,
        'LEARNING_TIME_SECONDS': 1990,
        'COURSERUN_KEY': 'course-v1:XYZ+IQC+2T2023',
        'COURSE_KEY': 'BCC+ITC',
        'COURSERUN_TITLE': 'Intro to Quantum Computing'
    }
]
