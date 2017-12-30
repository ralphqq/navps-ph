import datetime
import os
import sys
import time
from collections import namedtuple

import click
from dateutil.parser import parse

from mutualfunds import DailyNAVPS

TIMEOUT = 5
OUTDIR = 'Reports'

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
    click.echo('Initializing')
    dates = set_date_range(start, end)
    if dates is None:
        click.echo('No dates specified.')
        sys.exit(1)
    
    curr_date = dates.start
    click.echo('From: {:%Y-%m-%d}'.format(curr_date))
    click.echo('To: {:%Y-%m-%d}'.format(dates.end))
    one_day = datetime.timedelta(1)
    while curr_date <= dates.end:
        if curr_date.weekday() <= 4: # weekdays only
            click.echo('Processing report {:%Y-%m-%d}'.format(curr_date),
                        nl=False)
            report = DailyNAVPS(curr_date)
            if not report.open:
                click.echo(' [No data. Date skipped]')
            else:
                if not report.data:
                    click.echo(' [Unable to obtain data]')
                else:
                    save_report(report)
                    click.echo(' [Saved output file]')
            time.sleep(TIMEOUT)
        
        curr_date += one_day
    
    click.echo('Done')
