#!/bin/env python3.6

import psycopg2
from news_sql_definitions import SQLDefinintions as sql


def check_view(cursor, view_name):
    cursor.execute(sql.check_schema_query, (view_name,))
    exists, *_ = cursor.fetchone()
    return exists


def create_view(cursor, view_sql):
    cursor.execute(view_sql)


def perform_query(cursor, query, fmt_string):
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        print(fmt_string.format(row[0], row[1]))


def main():
    with psycopg2.connect("dbname=news", host="localhost",
                          user="vagrant", password="vagrant") as db:

        cursor = db.cursor()

        try:
            if not check_view(cursor, "goodrequests"):
                create_view(cursor, sql.good_requests_view)
            if not check_view(cursor, "badrequests"):
                create_view(cursor, sql.bad_requests_view)

            perform_query(cursor, sql.most_popular_3_articles,
                          "{} - {} views")
            print("\n")
            perform_query(cursor, sql.most_popular_authors,
                          "{} - {} views")
            print("\n")
            perform_query(cursor, sql.error_days, "{} - {:.2f}% errors")
            print("\n")
        except psycopg2.DatabaseError as e:
            print("An Error occured {}".format(e))
        finally:
            cursor.close()


if __name__ == '__main__':
    main()
