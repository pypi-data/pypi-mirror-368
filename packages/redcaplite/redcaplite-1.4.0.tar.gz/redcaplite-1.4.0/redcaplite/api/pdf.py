from .utils import optional_field


@optional_field('record')
@optional_field('event')
@optional_field('instrument')
@optional_field('repeat_instance')
@optional_field('allRecords')
@optional_field('compactDisplay')
def export_pdf(data):
    new_data = {
        'content': 'pdf'
    }
    return (new_data)
