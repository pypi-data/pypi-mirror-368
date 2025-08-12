from .utils import optional_field


@optional_field('logtype')
@optional_field('user')
@optional_field('record')
@optional_field('dag')
@optional_field('beginTime')
@optional_field('endTime')
@optional_field('format', 'csv')
def get_logs(data):
    new_data = {
        'content': 'log'
    }
    return (new_data)
