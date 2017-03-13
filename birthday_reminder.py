

import logging
logger = logging.getLogger('logger')

import traceback
import argparse
import smtplib
import time
import datetime

import pandas as pd
from pandas import Series, DataFrame
from email.mime.text import MIMEText

TODAY = datetime.date.today()
DAYS_TO_BIRTHDAY = 7
EMAIL_SENDING_RETRIES = 3

dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d')

def main():
    employees = DataFrame(pd.read_csv('employees.csv', header=0, parse_dates = [2], engine='c', date_parser=dateparse, na_values=['',' '])) # pandas DataFrame object for easy data manipulation
    logger.debug('Employees list (first 5):\n {0}'.format(employees.head()))

    workplace_birthdays = employees.copy()
    workplace_birthdays['cy_celeb_date'] = employees['birth_date'].apply(find_curr_year_celeb_dates) # add an additional collumn with a closest valid non weekend celebratory date
                        # current_year_celebration_date
    logger.debug(workplace_birthdays['cy_celeb_date'])

    next_week_birthdays = workplace_birthdays[workplace_birthdays['cy_celeb_date'] - TODAY == datetime.timedelta(days = DAYS_TO_BIRTHDAY)] # new DataFrame with celebrants with a calculated birthday exactly 7 days from today

    if(len(next_week_birthdays.index) > 0):
        logging.info('Employees with a work day birthday next week:\n{0}'.format(next_week_birthdays))
        email_list = employees[~employees['email'].isin(next_week_birthdays['email'])] # group of coworkers NOT in celebrants list
        logger.debug('Emailing list:\n{0}'.format(email_list))
        send_emails(next_week_birthdays, email_list)
    else:
        logging.info('There are no birthdays exactly {0} days from now'.format(DAYS_TO_BIRTHDAY))

def validate():
    """ Validate remainder recipients file """
    try:
        dframe_test = DataFrame(pd.read_csv('employees.csv', header=0, parse_dates = [2], engine='c', date_parser=dateparse, na_values=['',' '])) # should recognize incomplete or invalid dates, empty strings are marked
        if dframe_test.isnull().values.any(): # raises an exception if any types are empty
            raise ValueError('Empty value')
        logging.debug(dframe_test)
    except BaseException as e:
        logging.error(e)


def find_curr_year_celeb_dates(birthdate):
    """ Find current year celebration dates: Find a closest valid workday date """
    month = birthdate.month
    day = birthdate.day

    year = TODAY.year if TODAY.month != 12 and month != 1 else TODAY.year + 1 # if it's the last week of the year we want to make sure we check validity of the next year's date
    curr_celeb_date = try_find_valid_celeb_date(year, month, day)
    return curr_celeb_date


def try_find_valid_celeb_date(year, month, day):
    try:
        curr_celeb_date = datetime.date(year, month, day) # raises an exception if the date is invalid (has no 31rd day or February shenanigans)
        weekday = curr_celeb_date.isoweekday()
        if weekday in [6,7]: # weekend check
            logger.debug('Valid celebration date was found on weekend: {0}'.format(curr_celeb_date.strftime('%Y-%m-%d, %A')))
            curr_celeb_date = curr_celeb_date - datetime.timedelta(days = weekday % 5) # successfuly rolls back (both month and year if needed) 1-2 days to the nearest working day (friday)
        return curr_celeb_date
    except ValueError:
        logger.debug('Failed to find a valid date: {0}-{1}-{2}'.format(year,month,day))
        return try_find_valid_celeb_date(year, month, day-1) # in case the day is out of month's range


def send_emails(celebrants, email_list):
    _celebrants = celebrants.copy()
    _celebrants['fullname'] = celebrants['first_name'] + ' ' + celebrants['last_name'] # new column for full name
    celebrants = _celebrants
    _celebrants = []

    fp = open('email', 'r+')
    str_format = {
        '%(name)': ', '.join(celebrants['fullname'].values),
        '%(date)': str(celebrants['cy_celeb_date'].unique()[0]),
        '%(real_date)': ', '.join(celebrants['birth_date']),
        '%(amount_of_days)': DAYS_TO_BIRTHDAY
    }
    text = fp.read().format(**str_format) # formats a single letter for all recipients
    fp.close()

    msg = MIMEText(text)
    msg['Subject'] = 'Birthday Reminder: %(name_of_birthday_person)\'s birthday on %(date)'.format(**str_format)
    msg['To'] = ','.join(email_list['email'].values)
    msg['From'] = 'remainder@bot.com'

    try_send_email('remainder@bot.com', email_list['email'].values, msg.as_string())


def try_send_email(me, to, message, retries=0): # untested
    try:
        s = smtplib.SMTP('localhost')
        s.sendmail(me, to, message)
        logger.info('Remainders successfuly sent to employees')
        s.quit()
    except:
        if (retries <= EMAIL_SENDING_RETRIES):
            logger.info('Emails failed to send. Retry: {0}'.format(retries))
            try_send_email(me,to,message,retries+1)
    finally:
        if (retries > EMAIL_SENDING_RETRIES):
            logger.info('For the sake of simplicity let\'s assume that the emails have been sent successfully in 3 retries')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Birthday reminder')

    parser.add_argument('--action', help='The action to take: validate, checkbdays')
    args = parser.parse_args()

    if args.action == 'checkbdays':
        main()
    if args.action == 'validate':
        validate()
