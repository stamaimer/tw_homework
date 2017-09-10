# -*- coding: utf-8 -*-


import sys
import bisect
import sqlite3
import datetime
import traceback

from itertools import groupby

from dateutil.parser import parse


def is_valid_date(date):
    try:
        date = parse(date)
        if date.date() <= datetime.datetime.today().date():  #
            return 1
        else:
            return 1
    except ValueError:
        return 0


def is_valid_time(time):
    try:
        start_time, end_time = map(parse, time.split('~'))
        if start_time.time().hour in range(9, 23) and start_time.time().minute == 0 \
            and end_time.time().hour in range(9, 23) and end_time.time().minute == 0 \
                and start_time < end_time:
            return 1
        else:
            return 0
    except ValueError:
        return 0


def is_valid_site(site):
    return site in "ABCD"


def is_valid(user, date, time, site):
    if user and date and time and site:
        if is_valid_date(date) and is_valid_time(time) and is_valid_site(site):
            return 1
        else:
            return 0
    else:
        return 0


def get_input():

    input = sys.stdin.readline().strip()

    if input:

        try:
            user, date, time, site, *flag = input.split()
        except ValueError:
            print("Error: the booking is invalid!")
            return

        if flag:
            if flag == ['C']:  # cancel book
                if is_valid(user, date, time, site):
                    return ('C', user, date, time, site)
                else:
                    print("Error: the booking is invalid!")
            else:
                print("Error: the booking is invalid!")
        else:  # book site
            if is_valid(user, date, time, site):
                return ('B', user, date, time, site)
            else:
                print("Error: the booking is invalid!")
    else:  # get summary of income
        return ('S', 0, "1993-02-13", "00:00~00:00", 0)


def create_tables(cursor):

    try:

        sql = """
        CREATE TABLE IF NOT EXISTS {table_name} (id integer primary key autoincrement,
                                                 user text not null,
                                                 date text not null,
                                                 start_time text not null,
                                                 end_time text not null,
                                                 site text not null,
                                                 toll integer not null)"""

        cursor.execute(sql.format(table_name="book"))

        cursor.execute("""DELETE FROM book""")

        cursor.execute(sql.format(table_name="cancel"))

        cursor.execute("""DELETE FROM cancel""")

    except:

        print(traceback.format_exc())

        exit(1)


def main():

    connection = sqlite3.connect("bc2.db")

    cursor = connection.cursor()

    create_tables(cursor)

    while 1:

        input = get_input()

        if input:

            flag, user, date, time, site = input

            start_time, end_time = time.split('~')
            weekday = parse(date).date().weekday()

            if flag == 'B':

                sql = """
                SELECT EXISTS (SELECT 1 FROM book where date='{date}' AND start_time<'{end_time}' AND end_time>'{start_time}' AND site='{site}')
                """.format(date=date, start_time=start_time, end_time=end_time, site=site)

                # print(sql)

                exists = cursor.execute(sql).fetchone()[0]

                # print(exists)

                if exists:
                    print("Error: the booking conflicts with existing bookings!")
                else:

                    start_hour = parse(start_time).time().hour
                    end_hour = parse(end_time).time().hour

                    # print(start_hour, end_hour)

                    if weekday in range(5):  # weekdays

                        # print("weekdays")

                        tolldict = {0: 30, 1: 30, 2: 50, 3: 80, 4: 60}
                        timelist = [9, 12, 18, 20, 22]

                        start_index = bisect.bisect_left(timelist, start_hour)
                        end_index = bisect.bisect_left(timelist, end_hour)

                        # print(start_index, end_index)

                        if end_index - start_index == 0:
                            toll = (end_hour - start_hour) * \
                                tolldict[start_index]
                        elif end_index - start_index == 1:
                            toll = (timelist[start_index] - start_hour) * \
                                tolldict[start_index] + \
                                (end_hour -
                                 timelist[end_index - 1]) * tolldict[end_index]
                        elif end_index - start_index == 2:
                            if start_index == 1:
                                toll = (timelist[start_index] - start_hour) * tolldict[start_index] + 300 + (
                                    end_hour - timelist[end_index - 1]) * tolldict[end_index]
                            else:
                                toll = (timelist[start_index] - start_hour) * tolldict[start_index] + 160 + (
                                    end_hour - timelist[end_index - 1]) * tolldict[end_index]
                        elif end_index - start_index == 3:
                            toll = (timelist[start_index] - start_hour) * tolldict[start_index] + 460 + (
                                end_hour - timelist[end_index - 1]) * tolldict[end_index]

                        # print(toll)

                    else:  # weekends

                        # print("weekends")

                        tolldict = {0: 40, 1: 40, 2: 50, 3: 60}
                        timelist = [9, 12, 18, 22]

                        start_index = bisect.bisect_left(timelist, start_hour)
                        end_index = bisect.bisect_left(timelist, end_hour)

                        # print(start_index, end_index)

                        if end_index - start_index == 0:
                            toll = (end_hour - start_hour) * \
                                tolldict[start_index]
                        elif end_index - start_index == 1:
                            toll = (timelist[start_index] - start_hour) * tolldict[start_index] + (
                                end_hour - timelist[end_index - 1]) * tolldict[end_index]
                        elif end_index - start_index == 2:
                            toll = (timelist[start_index] - start_hour) * tolldict[start_index] + 300 + (
                                end_hour - timelist[end_index - 1]) * tolldict[end_index]

                        # print(toll)

                    sql = """
                    INSERT INTO book (user, date, start_time, end_time, site, toll) VALUES ('{user}', '{date}', '{start_time}', '{end_time}', '{site}', {toll})
                    """.format(user=user, date=date, start_time=start_time, end_time=end_time, site=site, toll=toll)

                    # print(sql)

                    cursor.execute(sql)
                    connection.commit()

                    print("Success: the booking is accepted!")

            if flag == 'C':

                sql = """
                SELECT id, toll FROM book where user='{user}' AND date='{date}' AND start_time='{start_time}' AND end_time='{end_time}' AND site='{site}'
                """.format(user=user, date=date, start_time=start_time, end_time=end_time, site=site)

                # print(sql)

                record = cursor.execute(sql).fetchone()

                # print(record)

                if record:

                    sql = """DELETE FROM book WHERE id={id}""".format(
                        id=record[0])

                    # print(sql)

                    cursor.execute(sql)
                    connection.commit()

                    if weekday in range(5):
                        toll = record[1] * 0.5
                    else:
                        toll = record[1] * 0.25

                    sql = """
                    INSERT INTO cancel (user, date, start_time, end_time, site, toll) VALUES ('{user}', '{date}', '{start_time}', '{end_time}', '{site}', {toll})
                    """.format(user=user, date=date, start_time=start_time, end_time=end_time, site=site, toll=toll)

                    # print(sql)

                    cursor.execute(sql)
                    connection.commit()

                    print("Success: the booking is accepted!")

                else:

                    print("Error: the booking being cancelled does not exist!")

            if flag == 'S':
                sql = """SELECT date, start_time, end_time, site, toll FROM book ORDER BY site, date, start_time"""
                book = list(groupby(cursor.execute(sql).fetchall(),
                                    key=lambda item: item[3]))
                print(book)
                sql = """SELECT date, start_time, end_time, site, toll FROM cancel ORDER BY site, date, start_time"""
                cancel = list(groupby(cursor.execute(
                    sql).fetchall(), key=lambda item: item[3]))
                print(cancel)
                print("收入汇总")
                sum = 0
                print("---")
                print("场地:A")
                total = 0
                for item in book[0][1]:
                    print(item[0], item[1] + '~' + item[2], str(item[4]) + "元")
                    total += item[4]
                for item in cancel[0][1]:
                    print(item[0], item[1] + '~' +
                          item[2], "违约金", str(item[4]) + "元")
                    total += item[4]
                print("小计：", total, "\n")
                sum += total
                print("场地:B")
                total = 0
                for item in book[1][1]:
                    print(item[0], item[1] + '~' + item[2], str(item[4]) + "元")
                    total += item[4]
                for item in cancel[1][1]:
                    print(item[0], item[1] + '~' +
                          item[2], "违约金", str(item[4]) + "元")
                    total += item[4]
                print("小计：", total, "\n")
                sum += total
                rint("场地:C")
                total = 0
                for item in book[2][1]:
                    print(item[0], item[1] + '~' + item[2], str(item[4]) + "元")
                    total += item[4]
                for item in cancel[2][1]:
                    print(item[0], item[1] + '~' +
                          item[2], "违约金", str(item[4]) + "元")
                    total += item[4]
                print("小计：", total, "\n")
                sum += total
                print("场地:D")
                total = 0
                for item in book[3][1]:
                    print(item[0], item[1] + '~' + item[2], str(item[4]) + "元")
                    total += item[4]
                for item in cancel[3][1]:
                    print(item[0], item[1] + '~' +
                          item[2], "违约金", str(item[4]) + "元")
                    total += item[4]
                print("小计：", total, "\n")
                sum += total
                print("---")
                print("总计：", sum)


if __name__ == '__main__':
    main()
