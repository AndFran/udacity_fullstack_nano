#!/bin/env python3.6


class SQLDefinintions:
    check_schema_query = """
        SELECT EXISTS
        (
            SELECT * FROM information_schema.tables
            WHERE table_name = %s
        );
    """

    bad_requests_view = """
        CREATE VIEW badrequests AS
        SELECT time::date AS day, count(*) AS counter FROM log
        WHERE status LIKE '404%'
        GROUP BY time::date;
    """

    good_requests_view = """
        CREATE VIEW goodrequests AS
        SELECT time::date AS day, count(*) AS counter FROM log
        WHERE status LIKE '200%'
        GROUP BY time::date;
    """

    most_popular_3_articles = """
        SELECT a.title, count(*) FROM articles AS a
        JOIN log AS l ON
        l.path LIKE '%' || a.slug ||'%'
        --WHERE l.status like '200%'
        GROUP BY a.title
        ORDER BY count(*) DESC
        LIMIT 3;
    """

    most_popular_authors = """
        SELECT auth.name, count(*) FROM authors AS auth
        JOIN articles AS art ON
        auth.id = art.author
        JOIN log AS l ON
        l.path LIKE '%' || art.slug ||'%'
        WHERE l.status LIKE '%200%'
        GROUP BY auth.name
        ORDER BY count(*) DESC;
    """

    error_days = """
        SELECT bad.day, (bad.counter::float / good.counter::float)*100
              AS error_rate FROM
        BadRequests AS Bad
        JOIN GoodRequests AS Good
        ON bad.day = good.day
        WHERE (bad.counter::float / good.counter::float) > 0.01
    """
