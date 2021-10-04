import psycopg2
import psycopg2.extras


class PostgresAdapter:
    def __init__(self, db_url):
        self.db_url = db_url
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = psycopg2.connect(self.db_url)
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def close(self):
        self.cursor.close()
        self.conn.close()

    def create_crawler_table_if_not_exists(self):
        create_string = '''
        CREATE TABLE IF NOT EXISTS crawler 
        (
        id SERIAL PRIMARY KEY,
        source TEXT,
        domain TEXT,
        url TEXT,
        crawl_session_id TEXT,
        timestamp timestamp, 
        title TEXT,
        description TEXT,
        body TEXT
        )
        '''
        # For dateTime -> ISO8601 string format
        self.cursor.execute(create_string)
        self.conn.commit()


    def create_features_table_if_not_exist(self):
        create_string = '''
            CREATE TABLE IF NOT EXISTS features 
            (
            id INTEGER PRIMARY KEY,
            source TEXT,
            domain TEXT,
            url TEXT,
            crawl_session_id TEXT,
            timestamp timestamp, 
            title TEXT,
            description TEXT,
            body TEXT,
            title_tokens TEXT,
            description_tokens TEXT,
            body_tokens TEXT,
            all_tokens_count INTEGER,
            keywords TEXT,
            terms TEXT
            )
            '''
        # For dateTime -> ISO8601 string format
        self.cursor.execute(create_string)
        self.conn.commit()

    def copy_crawler_table_to_features_table(self):
        sql_string = """
        INSERT INTO features (id, source, domain,url,crawl_session_id,timestamp, title , description ,body)
        SELECT * FROM crawler
		WHERE crawler.id not in (select id from features)
        """

        self.cursor.execute(sql_string)
        self.conn.commit()

    def insert_to_crawler(self, source, domain, url, crawl_session_id, timestamp, title, description, body):
        insert_string = """
        INSERT INTO crawler (source, domain, url,crawl_session_id, timestamp, title, description, body)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        data_tuple = (source, domain, url,crawl_session_id, timestamp, title, description, body)
        self.cursor.execute(insert_string, data_tuple)
        self.conn.commit()

    def get_all_urls(self):
        sql_string = """
        SELECT distinct aliasname.url FROM 
        (
        select url from crawler
        UNION ALL
        select url from features
        ) as aliasname
        """

        self.cursor.execute(sql_string)
        results = self.cursor.fetchall()
        results = [res['url'] for res in results]
        return results

    def get_all_features(self):
        self.cursor.execute("SELECT * FROM features")
        results = self.cursor.fetchall()
        return results

    def update_features_keywords(self, article_id, keywords_dict):
        insert_string = """
        UPDATE features 
        set keywords = %(keywords)s
        WHERE id = %(id)s
        """

        data_dict = {
            'id': article_id,
            'keywords': str(keywords_dict)
        }

        self.cursor.execute(insert_string, data_dict)
        self.conn.commit()

    def update_features_tokens(self, article_id, title_tokens, description_tokens, body_tokens):
        insert_string = """
        UPDATE features 
        set 
            title_tokens= %(title_tokens)s,
            description_tokens = %(description_tokens)s,
            body_tokens = %(body_tokens)s,
            all_tokens_count = %(all_tokens_count)s
        WHERE id = %(id)s
        """

        data_dict = {
            'id': article_id,
            'title_tokens': " ".join(title_tokens),
            'description_tokens': " ".join(description_tokens),
            'body_tokens': " ".join(body_tokens),
            'all_tokens_count': len(title_tokens) + len(description_tokens) + len(body_tokens)
        }

        self.cursor.execute(insert_string, data_dict)
        self.conn.commit()

    def update_features_terms(self, article_id, terms_list):
        insert_string = """
        UPDATE features 
        set 
            terms = %(terms)s
        WHERE id = %(id)s 
        """

        data_dict = {
            'id': article_id,
            'terms': str(terms_list)
        }

        self.cursor.execute(insert_string, data_dict)
        self.conn.commit()

    def delete_duplicates_in_features(self):
        sql_string = """
        DELETE from features
        where id not in
         (
         select  min(id)
         from    features
         group by
                 title, description
         )
        """
        self.cursor.execute(sql_string)
        self.conn.commit()
    def drop_features_table(self):
        sql_string = """
        DROP TABLE IF EXISTS features;
        """
        self.cursor.execute(sql_string)
        self.conn.commit()

    def get_all_features_in_range(self, range_from, range_to):
        sql_string = """
        SELECT * FROM features
        WHERE timestamp BETWEEN %(range_from)s AND %(range_to)s
        """
        data_dict = {
            'range_from': range_from.isoformat(),
            'range_to': range_to.isoformat()
        }

        self.cursor.execute(sql_string, data_dict)
        results = self.cursor.fetchall()
        return results

    def delete_crawler_tail(self, min_datetime):
        sql_string = """
        DELETE FROM crawler
        WHERE timestamp < %(min_datetime)s
        """
        self.cursor.execute(sql_string, {'min_datetime':min_datetime})
        self.conn.commit()

    def delete_features_tail(self, min_datetime):
        sql_string = """
        DELETE FROM features
        WHERE timestamp < %(min_datetime)s
        """
        self.cursor.execute(sql_string, {'min_datetime':min_datetime})
        self.conn.commit()

    def delete_crawler_rows_that_in_features(self):
        sql_string = """
        DELETE FROM crawler
        WHERE crawler.url in (select url from features)
        """
        self.cursor.execute(sql_string)
        self.conn.commit()
