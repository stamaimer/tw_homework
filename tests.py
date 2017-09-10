# -*- coding: utf- 8 -*-

from bc2 import (main, create_tables,
                 get_input, is_valid, is_valid_date, is_valid_time, is_valid_site,
                 deal_with_book, cal_toll, deal_with_cancel, deal_with_income, gen_income_by_site)

from io import StringIO

import unittest
from unittest.mock import patch

from string import printable
from random import choice


class BC2TestCaseOne(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.connection, self.cursor = create_tables()

    def test_case(self):

        with patch("sys.stdin", StringIO("abcdefghijklmnopqrst1234567890")), patch("sys.stdout", new_callable=StringIO) as mocked_out:
            main(self.connection, self.cursor)
            self.assertEqual(mocked_out.getvalue(),
                             "> Error: the booking is invalid!\n")

        with patch("sys.stdin", StringIO("U001 2016-06-02 22:00~22:00 A")), patch("sys.stdout", new_callable=StringIO) as mocked_out:
            main(self.connection, self.cursor)
            self.assertEqual(mocked_out.getvalue(),
                             "> Error: the booking is invalid!\n")

        with patch("sys.stdin", StringIO("U002 2017-08-01 19:00~22:00 A")), patch("sys.stdout", new_callable=StringIO) as mocked_out:
            main(self.connection, self.cursor)
            self.assertEqual(mocked_out.getvalue(),
                             "> Success: the booking is accepted!\n")

        with patch("sys.stdin", StringIO("U003 2017-08-02 13:00~17:00 B")), patch("sys.stdout", new_callable=StringIO) as mocked_out:
            main(self.connection, self.cursor)
            self.assertEqual(mocked_out.getvalue(),
                             "> Success: the booking is accepted!\n")

        with patch("sys.stdin", StringIO("U004 2017-08-03 15:00~16:00 C")), patch("sys.stdout", new_callable=StringIO) as mocked_out:
            main(self.connection, self.cursor)
            self.assertEqual(mocked_out.getvalue(),
                             "> Success: the booking is accepted!\n")

        with patch("sys.stdin", StringIO("U005 2017-08-05 09:00~11:00 D")), patch("sys.stdout", new_callable=StringIO) as mocked_out:
            main(self.connection, self.cursor)
            self.assertEqual(mocked_out.getvalue(),
                             "> Success: the booking is accepted!\n")

        with patch("sys.stdin", StringIO("\n")), patch("sys.stdout", new_callable=StringIO) as mocked_out:
            main(self.connection, self.cursor)
            self.assertEqual(mocked_out.getvalue(),
                             """> 收入汇总
> ---
> 场地:A
> 2017-08-01 19:00~22:00 200元
> 小计：200元
>
> 场地:B
> 2017-08-02 13:00~17:00 200元
> 小计：200元
>
> 场地:C
> 2017-08-03 15:00~16:00 50元
> 小计：50元
>
> 场地:D
> 2017-08-05 09:00~11:00 80元
> 小计：80元
> ---
> 总计：530元\n""")


class BC2TestCaseTwo(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.connection, self.cursor = create_tables()

    def tearDown(self):
        self.cursor.close()
        self.connection.close()

    def test_case(self):
        with patch("sys.stdin", StringIO("U002 2017-08-01 19:00~22:00 A")), patch("sys.stdout", new_callable=StringIO) as mocked_out:
            main(self.connection, self.cursor)
            self.assertEqual(mocked_out.getvalue(),
                             "> Success: the booking is accepted!\n")

        with patch("sys.stdin", StringIO("U003 2017-08-01 18:00~20:00 A")), patch("sys.stdout", new_callable=StringIO) as mocked_out:
            main(self.connection, self.cursor)
            self.assertEqual(mocked_out.getvalue(),
                             "> Error: the booking conflicts with existing bookings!\n")

        with patch("sys.stdin", StringIO("U002 2017-08-01 19:00~22:00 A C")), patch("sys.stdout", new_callable=StringIO) as mocked_out:
            main(self.connection, self.cursor)
            self.assertEqual(mocked_out.getvalue(),
                             "> Success: the booking is accepted!\n")

        with patch("sys.stdin", StringIO("U002 2017-08-01 19:00~22:00 A C")), patch("sys.stdout", new_callable=StringIO) as mocked_out:
            main(self.connection, self.cursor)
            self.assertEqual(mocked_out.getvalue(),
                             "> Error: the booking being cancelled does not exist!\n")

        with patch("sys.stdin", StringIO("U003 2017-08-01 18:00~20:00 A")), patch("sys.stdout", new_callable=StringIO) as mocked_out:
            main(self.connection, self.cursor)
            self.assertEqual(mocked_out.getvalue(),
                             "> Success: the booking is accepted!\n")

        with patch("sys.stdin", StringIO("U003 2017-08-02 13:00~17:00 B")), patch("sys.stdout", new_callable=StringIO) as mocked_out:
            main(self.connection, self.cursor)
            self.assertEqual(mocked_out.getvalue(),
                             "> Success: the booking is accepted!\n")

        with patch("sys.stdin", StringIO("\n")), patch("sys.stdout", new_callable=StringIO) as mocked_out:
            main(self.connection, self.cursor)
            self.assertEqual(mocked_out.getvalue(),
                             """> 收入汇总
> ---
> 场地:A
> 2017-08-01 18:00~20:00 160元
> 2017-08-01 19:00~22:00 违约金 100元
> 小计：260元
>
> 场地:B
> 2017-08-02 13:00~17:00 200元
> 小计：200元
>
> 场地:C
> 小计：0元
>
> 场地:D
> 小计：0元
> ---
> 总计：460元\n""")


class BC2TestCase(unittest.TestCase):

    def setUp(self):
        self.connection, self.cursor = create_tables()

    def tearDown(self):
        self.cursor.close()
        self.connection.close()

    def test_tables(self):
        tables = self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()

        for table in [("book", ), ("cancel", )]:

            self.assertIn(table, tables)

            records = self.cursor.execute(
                "SELECT 1 FROM {table_name}".format(table_name=table[0])).fetchall()

            self.assertEqual([], records)

    def test_is_valid_date(self):

        self.assertTrue(is_valid_date("1993-02-13"))

        self.assertTrue(is_valid_date("1992-12-03"))

        self.assertFalse(is_valid_date("1993-13-02"))

        self.assertFalse(is_valid_date("1992-30-12"))

    def test_is_valid_time(self):

        self.assertTrue(is_valid_time("09:00~22:00"))

        self.assertFalse(is_valid_time("08:00~12:00"))

        self.assertFalse(is_valid_time("12:00~23:00"))

        self.assertFalse(is_valid_time("09:10~12:00"))

        self.assertFalse(is_valid_time("09:00~12:10"))

        self.assertFalse(is_valid_time("12:00~12:00"))

        self.assertFalse(is_valid_time("12:00~09:00"))

    def test_is_valid_site(self):

        for site in "ABCD":

            self.assertTrue(is_valid_site(site))

        self.assertFalse(is_valid_site(
            choice([item for item in printable if item not in "ABCD"])))

    def test_cal_toll(self):

        for weekday in range(5):
            self.assertEqual(cal_toll("09:00", "12:00", weekday), 90)
            self.assertEqual(cal_toll("12:00", "18:00", weekday), 300)
            self.assertEqual(cal_toll("18:00", "20:00", weekday), 160)
            self.assertEqual(cal_toll("20:00", "22:00", weekday), 120)

        for weekday in range(5, 7):
            self.assertEqual(cal_toll("09:00", "12:00", weekday), 120)
            self.assertEqual(cal_toll("12:00", "18:00", weekday), 300)
            self.assertEqual(cal_toll("18:00", "22:00", weekday), 240)

        self.assertEqual(cal_toll("10:00", "15:00", 0), 210)
        self.assertEqual(cal_toll("15:00", "19:00", 0), 230)
        self.assertEqual(cal_toll("19:00", "21:00", 0), 140)

        self.assertEqual(cal_toll("10:00", "19:00", 0), 440)
        self.assertEqual(cal_toll("15:00", "21:00", 0), 370)

        self.assertEqual(cal_toll("10:00", "21:00", 0), 580)

        self.assertEqual(cal_toll("10:00", "15:00", 5), 230)
        self.assertEqual(cal_toll("15:00", "20:00", 5), 270)

        self.assertEqual(cal_toll("10:00", "20:00", 5), 500)


if __name__ == '__main__':
    unittest.main()
