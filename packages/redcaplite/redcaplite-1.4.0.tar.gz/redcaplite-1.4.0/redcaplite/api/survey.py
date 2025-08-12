from .utils import require_field, optional_field


@require_field('record')
@require_field('instrument')
@optional_field('event')
@optional_field('repeat_instance')
def get_survey_link(data):
    new_data = {
        'content': 'surveyLink'
    }
    return (new_data)


@require_field('instrument')
@optional_field('event')
@optional_field('format', 'csv')
def get_participant_list(data):
    new_data = {
        'content': 'participantList'
    }
    return (new_data)


@require_field('record')
def get_survey_queue_link(data):
    new_data = {
        'content': 'surveyQueueLink'
    }
    return (new_data)


@require_field('record')
@require_field('instrument')
@optional_field('event')
@optional_field('repeat_instance')
def get_survey_return_code(data):
    new_data = {
        'content': 'surveyReturnCode'
    }
    return (new_data)
