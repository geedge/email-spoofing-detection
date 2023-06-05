import pandas as pd
import shutil
from os import listdir, mkdir, path
from pathlib import Path
import sys
from email.parser import HeaderParser
import collections
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import time
from collections import Counter
import re

parser = HeaderParser()
columns = ['received1',
           'received2',
           'received3',
           'received4',
           'received5',
           'received6',
           'received7',
           'received8',
           'hops',
           'subject',
           'date',
           'message-id',
           'from',
           'return-path',
           'to',
           'content-type',
           'mime-version',
           'x-mailer',
           'content-transfer-encoding',
           'x-mimeole',
           'x-priority',
           'list-id',
           'lines',
           'x-virus-scanned',
           'status',
           'content-length',
           'precedence',
           'delivered-to',
           'list-unsubscribe',
           'list-subscribe',
           'list-post',
           'list-help',
           'x-msmail-priority',
           'x-spam-status',
           'sender',
           'errors-to',
           'x-beenthere',
           'list-archive',
           'reply-to',
           'x-mailman-version',
           'x-miltered',
           'x-uuid',
           'x-virus-status',
           'x-spam-level',
           'x-spam-checker-version',
           'references',
           'in-reply-to',
           'user-agent',
           'thread-index',
           'cc',
           'received-spf',
           'x-original-to',
           'content-disposition',
           'mailing-list',
           'x-spam-check-by',
           'domainkey-signature',
           'importance',
           'x-mailing-list',
           'label']

list_of_rows = []


def addEmailsToDict(email_list):
    global parser, list_of_rows

    # The label for phishing, set to '2'
    label = 2

    # Read the full email content
    for email in email_list:
        row_dict = {}

        # Parse the email content
        h = parser.parsestr(email)

        # Parse recieved field
        received_list = h.get_all('received')
        hops = 0
        if received_list is not None:
            hops = len(received_list)
            col_name_recieved = 'received'

            for inx, received_field in enumerate(received_list):
                col = col_name_recieved + str(inx + 1)
                row_dict[col] = received_field

        # Make everything lowercase to avoid issues
        features_lower_case = [x.lower() for x in h.keys()]

        # Parse everything else
        new_row = dict(zip(features_lower_case, h.values()))
        new_row['hops'] = hops

        for key, value in new_row.items():
            if key in columns:
                row_dict['label'] = label
                row_dict[key] = value

        list_of_rows.append(row_dict)


def main():
    global list_of_rows

    file_path = 'nazario_phishing_2015.txt'

    # Read the full email content
    emailStr = ''
    try:
        with open(file_path, encoding='latin_1') as emailFile:
            for line in emailFile:
                emailStr += line
    except UnicodeDecodeError:
        print('Unicode Error!')

    # email_list = re.split(r"\nFrom [a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+ ",emailStr)
    email_list=re.split(r"\nFrom .*\n",emailStr)
    # print(email_list[1])

    addEmailsToDict(email_list)

    # Create the dataframe
    df = pd.DataFrame(list_of_rows)

    final_columns = []
    for col in columns:
        if col in df.columns:
            final_columns.append(col)

    df = df[final_columns]

    # Output the dataframe to a .csv file
    df.to_csv('phishing_out_2015.csv', index=False)


if __name__ == '__main__':
    main()