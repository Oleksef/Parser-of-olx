from settings import *


def add_to_database(data: list):
    conn = psycopg2.connect(dbname='olxpostdb', user='olxpars', password='olxpass', host='localhost')
    with conn.cursor() as cur:
        conn.autocommit = True
        cur.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS olx.{} (name varchar(500), category varchar(60), price integer,
                                               currency varchar(5), view integer, date varchar(70),
                                               district varchar(50), url varchar(500));
                            """).format(sql.Identifier(data[1])))

        cur.execute(sql.SQL("""
            INSERT INTO olx.{} (name, category, price, currency, view, date, district, url)
            SELECT %s, %s, %s, %s, %s, %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM olx.{}
                WHERE name = %s AND category = %s AND price = %s AND currency = %s AND view = %s 
                AND date = %s AND district = %s AND url = %s
            );
            """).format(sql.Identifier(data[1]), sql.Identifier(data[1])),
                    (
                        data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7],
                        data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7])
                    )
