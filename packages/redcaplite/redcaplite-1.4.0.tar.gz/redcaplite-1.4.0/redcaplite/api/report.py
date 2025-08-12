from .utils import optional_field, require_field


@optional_field('format', 'csv')
@require_field('report_id')
@optional_field('csvDelimiter', ',')
@optional_field('rawOrLabel', 'raw')
@optional_field('rawOrLabelHeaders', 'raw')
@optional_field('exportCheckboxLabel', 'false')
@optional_field('decimalCharacter')
def get_report(data):
    new_data = {
        'content': 'report',
    }
    return (new_data)
