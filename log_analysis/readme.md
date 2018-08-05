# Logs Analysis

This is an internal reporting tool for a newspaper site. The tool can be used
to analyse the various logs, authors and articles that are stored in the database.

The reporting tool generates 3 reports:


1. What are the most popular three articles of all time?
The tool will show in plain text on the console which top 3 articles have been
accessed the most in the format:

"Article Title" - Number of views



2. Who are the most popular article authors of all time?
This will show in plain text in descending order the most popular authors in
the format:

"Author name" - Total views


3. On which days did more than 1% of requests lead to errors?
This will show the on which days more than 1% of all the requests lead to errors.
The format of the report is:

"Date" - % errors



## Setup

1 - Have postgres installed
    A - Create a new database called: "news"
    B - Create a new role called "vagrant" and password "vagrant" or change the
        connection string in app.py
    C - Run the sql script:
            https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip
    D - Install the database with:
            psql -d news -f newsdata.sql

            The database has 3 tables:
            1 - authors
            2 - articles
            3 - log

2 - In your virtual environment install psycopg2

3 - Run:
        python app.py


## Additional Information

All the SQL for the reporting tool is contained in:

news_sql_definitions.py

The reporting tool automatically generates 2 views if not already present on
the database server:

- goodrequests
- badrequests

This is done in the main() when running the app.py file:

            if not check_view(cursor, "goodrequests"):
                create_view(cursor, sql.good_requests_view)
            if not check_view(cursor, "badrequests"):
                create_view(cursor, sql.bad_requests_view)


So there is no need to manually create any








