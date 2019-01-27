import datetime
import logging
import os
import sys
import time
from collections import namedtuple

import click
from dateutil.parser import parse
import requests

from mutualfunds import DailyNAVPS

LOGFILE = 'runtime.log'
TIMEOUT = 5
OUTDIR = 'Reports'

def stringify_date(date):
    """Convert datetime object into human-readable string"""
    return date.strftime('%Y-%m-%d')

def save_report(report):
    """Create the directory structure where output is saved"""
    rdate = report.date
    fname = 'mf-navps-report-{:%Y-%m-%d}.csv'.format(rdate)
    fpath = '{},{:%Y,%m-%B}'.format(OUTDIR, rdate).split(',')
    spath = os.path.join(*fpath)
    if not os.path.exists(spath):
        os.makedirs(spath, exist_ok=True)
    report.to_csv(os.path.join(spath, fname))

def set_date_range(start, end):
    """Handle the date parameters properly"""
    DateRange = namedtuple('DateRange', 'start end')
    dates = None
    if end:
        end = parse(end)
        start = parse(start) if start else end
        dates = DateRange(start=start, end=end)
    else:
        if start:
            start = parse(start)
            end = datetime.datetime.now()
            dates = DateRange(start=start, end=end)
    return dates

@click.command()
@click.option('-s', '--start',
              help='Starting date (not earlier than Dec. 20, 2004)')
@click.option('-e', '--end',
              help='Ending date (up to most recent trading day)')
def run(start, end):
    logging.basicConfig(format='%(asctime)s %(message)s',
                        filename=LOGFILE,
                        level=logging.INFO)
    logging.info('[INFO] Started')
    click.echo('Initializing')
    dates = set_date_range(start, end)
    if dates is None:
        msg = 'No dates specified. Exited'
        click.echo(msg)
        logging.info('[INFO] {}'.format(msg))
        sys.exit(1)
    
    curr_date = dates.start
    from_str = stringify_date(curr_date)
    to_str = stringify_date(dates.end)
    msg = 'Set range from {} to {}'.format(from_str, to_str)
    click.echo(msg)
    logging.info('[INFO] {}'.format(msg))
    one_day = datetime.timedelta(1)

    with requests.Session() as session:
        logging.info('Session established.')
        click.echo('Session started')
        while curr_date <= dates.end:
            if curr_date.weekday() <= 4: # weekdays only
                click.echo('Processing report {}'.format(from_str),
                           nl=False)
                try:
                    report = DailyNAVPS(
                        session=session,
                        date=curr_date
                    )
                except Exception as e:
                    click.echo(' [Error: {}]'.format(e))
                    logging.error('[ERROR] {} at {}'.format(e, from_str))
                else:
                    if not report.open:
                        click.echo(' [No data. Date skipped]')
                        logging.info(
                            '[INFO] Report {} skipped'.format(from_str)
                        )
                    else:
                        if not report.data:
                            click.echo(' [Unable to obtain data]')
                            logging.warning(
                                '[WARNING] {} is empty'.format(from_str)
                            )
                        else:
                            save_report(report)
                            click.echo(' [Saved output file]')
                finally:
                    time.sleep(TIMEOUT)
            curr_date += one_day
            from_str = stringify_date(curr_date)

    click.echo('Done')
    logging.info('[INFO] Finished')
