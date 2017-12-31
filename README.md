# navps-ph

This command line tool scrapes the daily net asset value per share (NAVPS) data from the [Facts and Figures page](http://pifa.com.ph/factsfignavps.asp) of the Investment Companies Association of the Philippines's website.

The script lets you access NAVPS reports for a specific date or within a date range and saves each scraped report as a separate CSV file.

## Requirements and Installation

This tool runs on Python 3.6 and uses requests, lxml, BeautifulSoup, python-dateutil, and click (among other dependencies). To install the full list of requirements and to  run ph-navps as a command line tool, follow the below instructions:

1. Clone this repo into your local machine.
2. Create a fresh virtual environment.
3. cd to the project directory and enter:

```
$ pip install --editable .
```

Make sure to activate the virtual environment you created for this project each time you run the script.

## Usage

The basic syntax goes something like this:

```
$ navps -s REPORT_START_DATE -e REPORT_END_DATE
```

For instance, to scrape the daily NAVPS data for the entire year 2017, enter the following:

```
$ navps -s "Jan 1 2017" -e "Dec 31 2017"
```

Note that the script accepts a number of common date string formats, such as:

* "Jan 9 2017", "January 9, 2017", "9 Jan 2017", etc.
* "2017-01-09", "2017-1-9", "2017 1 9", etc.

Just be sure to enclose input dates in quotation marks.

## Specifying Report Dates

The script requires that you provide a valid date for at least one of the parameters. As shown above, entering both `-s` (start) and `-e` (end)dates tells the scraper to access all the daily NAVPS report that fall within the given interval.

To scrape all NAVPS reports starting from a given date up to the most recently available report, provide a value only to the `-s` parameter. The following command collects NAVPS from December 1, 2017 up to December 29, 2017 (the latest report at time of writing):

```
$ navps -s "2017-12-01"
```

To obtain the NAVPS data for exactly one date, pass the desired date to `-e` parameter without invoking `-s`. The below command scrapes the NAVPS data for November 27, 2017:

```
$ navps -e "Nov 27, 2017"
```

Please note that:

1. The earliest NAVPS report available on the site is dated Dec. 20, 2004.
2. In some instances, the current day's NAVPS data only becomes available on the following day.
3. The script skips holidays and non-trading days.

## Output

Each scraped NAVPS report is saved in its own CSV file and contains the following fields:

1. **Date**: The date of the NAVPS report
2. **Fund Name**: The name of the mutual fund or ETF
3. **Type**: Stock fund, balanced fund, bond fund, etc.
4. **NAV Per Share**: The day's closing NAVPS
5. **1 yr. Return (%)**: A fund's one-year return as of report date
6. **3 yr. Return (%)**: A fund's three-year return as of report date
7. **5 yr. Return (%)**: A fund's five-year return as of report date
8. **YTD Return (%)**: A fund's year-to-date return
9. **N.A.V. History**: An extra column (doesn't really contain anything except the word "History")

The tool saves the files in the `Reports` directory and organizes the output files by year  and then by month.

## License

[MIT License](https://opensource.org/licenses/MIT)

## Contributing

Please feel free to use or build this project further.