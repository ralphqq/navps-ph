import csv
import datetime
import os

import requests
from bs4 import BeautifulSoup
from dateutil import parser

URL = "http://pifa.com.ph/factsfignavps.asp?D1={:%m%%2F%d%%2F%Y}&txtNoRecs=False"

TD_MF_VALUES = 'tr.icap_DataText021 td'
TR_MF_VALUES = 'tr.icap_DataText021'
TH_TD_VALUES = 'tr.icap_HederText03 td'

COLS = [
    'Date',
    'Fund Name',
    'Type',
    'NAV Per Share',
    '1 yr. Return (%)',
    '3 yr. Return (%)',
    '5 yr. Return (%)',
    'YTD Return (%)',
    'N.A.V. History'
]

FUND_TYPES = [
    'Stock Funds',
    'Balanced Funds',
    'Bond Funds',
    'Money Market Funds'
]

class DailyNAVPS(object):
    """
    Represents the daily NAVPS report object
    """
    def __init__(self, date=None):
        """Initializes the object"""
        self.date = self._set_date(date)
        self.link = URL.format(self.date)
        self.soup = None
        self.open = False
        self.cols = []
        self.data = []
        self._all_td = []
        self._type_index = {}  # index/slices for fund type rows
        self._run()
    
    def _run(self):
        """Control the internal flow of script"""
        self.soup = self._get_soup()
        self.open = self._is_open()
        if self.open:
            self.cols = self._set_cols()
            self._get_all_td_index()
            self.data = self._parse_data()
    
    def _set_date(self, date):
        """Convert input date into datetime object if not yet one"""
        report_date = None
        if date is None:
            report_date = datetime.datetime.now()
        else:
            if type(date) is not datetime.datetime:
                report_date = parser.parse(date)
            else:
                report_date = date
        
        return report_date
    
    def _get_soup(self):
        """Read and parse the given webpage"""
        soup = None
        try:
            page = requests.get(self.link)
            soup = BeautifulSoup(page.text, 'lxml')
        except requests.exceptions.RequestException as e:
            print(e)
        else:
            return soup
        
    def _is_open(self):
        """
        Check if market is open on given date.
        Count how many td tags with 'N.S.'.
        
        Return:
            False: If count exceeds number of tr.icap_DataText021 rows
        """
        td_values = [td.get_text().strip()
                     for td in self.soup.select(TD_MF_VALUES)]
        tr_counts = len(self.soup.select(TR_MF_VALUES))
        return tr_counts >= td_values.count('N.S.')
    
    def _set_cols(self):
        """Set the column/field labels"""
        header = [th.get_text().strip()
                  for th in self.soup.select(TH_TD_VALUES)]
        return header
    
    def _get_all_td_index(self):
        """Define td list ranges where types start and end"""
        self._all_td = [td.get_text().strip()
                        for td in self.soup.select('td')]
        beg_idx = [self._all_td.index(p) for p in FUND_TYPES]
        end_idx = beg_idx[1:] + [len(self._all_td)]
        self._type_index = {(beg, end): self._all_td[beg]
                            for beg, end in zip(beg_idx, end_idx)}

    def _identify_type(self, fund_name):
        """Determine what type of mutual fund a given fund is"""
        idx = self._all_td.index(fund_name)
        sec = 'Unknown'
        for k, v in self._type_index.items():
            if k[0] < idx < k[1]:
                sec = v
        return sec

    def _parse_data(self):
        """Parse BeautifulSoup object into rows"""
        data = []
        for tr in self.soup.select(TR_MF_VALUES):
            fund = {}
            fund['Date'] = '{:%Y-%m-%d}'.format(self.date)
            for colnum, val in enumerate(tr.select('td')):
                fund[self.cols[colnum]] = val.get_text().strip()
            fund['Type'] = self._identify_type(fund.get('Fund Name'))
            data.append(fund)
        
        return data

    def to_csv(self, fpath):
        """Write the data into an output CSV file"""
        with open(fpath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=COLS)
            writer.writeheader()
            for row in self.data:
                writer.writerow(row)

