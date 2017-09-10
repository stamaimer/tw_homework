# -*- coding: utf- 8 -*-

from bc2 import (main, create_tables,
                 get_input, is_valid, is_valid_date, is_valid_time, is_valid_site,
                 deal_with_book, cal_toll, deal_with_cancel, deal_with_income, gen_income_by_site)

from io import StringIO

import unittest
from unittest.mock import patch


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

    def test_tables(self):
        tables = self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()

        for table in [("book", ), ("cancel", )]:

            self.assertIn(table, tables)

            records = self.cursor.execute(
                "SELECT 1 FROM {table_name}".format(table_name=table[0])).fetchall()

            self.assertEqual([], records)

    def


if __name__ == '__main__':
    unittest.main()
