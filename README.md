# coding-task-birthday-reminder
Coding task for a coding job

TASK:
We have found ourselves in need of a birthday reminder application.
We know that there are lots of existing applications for this purpose,
nevertheless we would like that you create a Python application which would to
the job.
We need a script that will run as a Cron job daily and send emails to everyone
from a given list of people (<= 100 people), except the person who will be
celebrating their birthday. The reminder email should be sent one week before
the person's birthday.
The script should have two commands/options:
1.validate the persons birthday data file, print errors (if found)
2.check for upcoming birthdays and send emails if there are any. Exit once emails are sent.
The list of people will be provided in a separate text file in CSV/JSON/YAML/Other
format (please state why you chose the other format). A person's entry in the
file will contain:
1.the person's name,
2.email,
3.birthdate (in YYYY-MM-DD or MM-DD format).
The data file is considered valid if:
•it can be successfully parsed,
•all people have a name set,
•all people have an email set (however, you don't need to check if the email addresses are
valid or not),
•each person's birthdate is a valid date (eg. no 02-30 or 01-32) in the PAST.
For the sake of simplicity let's assume that:
1.the emails can always be sent successfully in 3 retries,
2.emails are sent instantly (there is no need to send the emails asynchronously),
3.the email template is hardcoded.
The script's interface should preferably be CLI.
An example email template:
Subject: Birthday Reminder: %(name_of_birthday_person)s's birthday on %(date)s
Body:
Hi %(name)s,
This is a reminder that %(name_of_birthday_person)s will be celebrating their
birthday on %(date)s.
There are %(amount_of_days)s left to get a present!
It would be great if you would use git VCS for the development of this small project.

USAGE: 
python birthday_reminder.py -h  // for help

python birthday_reminder.py -action validate // for validation

python birthday_reminder.py -action checkbdays // for birthday calculations
