import argparse
import logging

from launchpad2 import cache
from launchpad2.csv import csvwriter
from launchpad2 import lp


LOG = logging.getLogger(__name__)

DATE_KEYS = [
    'date_assigned',
    'date_closed',
    'date_confirmed',
    'date_created',
    'date_fix_committed',
    'date_fix_released',
    'date_in_progress',
    'date_incomplete',
    'date_last_message',
    'date_last_updated',
    'date_left_closed',
    'date_left_new',
    'date_made_private',
    'date_triaged',
]


def normalize_datetime_values(bug):
    for key in DATE_KEYS:
        try:
            bug[key] = lp.parse_date(bug[key]).strftime('%m/%d/%Y')
        except (ValueError, TypeError):
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'launchpad_project',
        help='Your Launchpad project name.')
    parser.add_argument(
        '--debug', action='store_true',
        help='Enable debugging output.')
    parser.add_argument(
        '--purge-cache', action='store_true',
        help='Purge the local cache before running.')
    parser.add_argument(
        '--header-map', action='append',
        default=['ID:id',
                 'Link:web_link',
                 'Name:title',
                 'Backlog:date_created',
                 'Approved:',
                 'In Progress:date_assigned',
                 'Dev Done:date_fix_committed',
                 'Done:date_fix_released'],
        help='Mapping of header name to launchpad attribute, e.g., '
             '--header-map Approved:Triaged --header-map "Doing:In Progress"')
    parser.add_argument(
        '--output-file',
        help='Location to store the output of the csv conversion')

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    if args.purge_cache:
        cache.purge()

    header_map = [i.split(':', 1) for i in args.header_map]
    headers = [i[0] for i in header_map]
    attribute_names = [i[1] for i in header_map]

    lp_project = lp.get_project(args.launchpad_project)

    with csvwriter.CSVFormatterWriter(args.output_file, headers,
                                      attribute_names) as csvconverter:
        for bug in lp.list_bugs(lp_project):
            normalize_datetime_values(bug)
            csvconverter.record_bug(bug)


if __name__ == '__main__':
    main()
