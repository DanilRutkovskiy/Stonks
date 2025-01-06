import psycopg2
from psycopg2 import sql, OperationalError
from psycopg2.extras import DictCursor
import pandas
from Structs.network import network

class StockMarketDb(object):
    def __init__(self):
        self.conn = 0
        self._connect_to_db()

    def import_coin(self, coin:{}, stock_name):
        sql_to_add = ""
        for k, v in coin.items():
            sql_to_add = f"""
                SELECT id INTO coinId
                FROM coins
                WHERE name = '{k}';
                IF coinId IS NULL THEN
                    INSERT INTO coins(name)
                    VALUES('{k}') ON CONFLICT (name) DO NOTHING
                    RETURNING id INTO coinId; 
                END IF;
            """

            for network in v:
                sql_to_add += f"""
                             SELECT id INTO networkId
                             FROM networks
                             WHERE name = '{network["chain"]}';
                             IF networkId IS NULL THEN
                                 INSERT INTO networks(name)
                                 VALUES ('{network["chain"]}') ON CONFLICT (name) DO NOTHING
                                 RETURNING id INTO networkId; 
                             END IF;
                            """

                sql_to_add += f""" INSERT INTO coin_network_for_stock(coin_id, network_id, stock_id, withdraw_fee, deposit_min, withdraw_min)
                                  VALUES(coinId, networkId, stockId, '{network["withdrawFee"]}', '{network["depositMin"]}', '{network["withdrawMin"]}') 
                                  ON CONFLICT(coin_id, network_id, stock_id) DO
                                  UPDATE 
                                  SET withdraw_fee = '{network["withdrawFee"]}', deposit_min = '{network["depositMin"]}', withdraw_min = '{network["withdrawMin"]}'; 
                              """

        my_sql = f"""DO
                    $$
                    DECLARE
                        stockId BIGINT;
                        coinId BIGINT;
                        networkId BIGINT;
                    BEGIN
                         SELECT id INTO stockId 
                         FROM stock 
                         WHERE name = '{stock_name}';

                         {sql_to_add}
                         

                    END;
                    $$;"""

        cursor = self.conn.cursor()

        cursor.execute(my_sql)


    def get_best_network_for_coin(self, coin_name, stock_name):
        my_sql = f"""SELECT cnfs.deposit_min, cnfs.withdraw_min, cnfs.withdraw_fee, n.name
                     FROM coin_network_for_stock AS cnfs
                     JOIN stock AS s ON cnfs.stock_id = s.id
                     JOIN coins As c ON cnfs.coin_id = c.id
                     JOIN networks AS n ON cnfs.network_id = n.id
                     WHERE c.name = '{coin_name}' AND s.name = '{stock_name}'
                     ORDER BY withdraw_fee::FLOAT
                     LIMIT 1"""

        cursor = self.conn.cursor(cursor_factory=DictCursor)
        cursor.execute(my_sql)
        record = cursor.fetchone()

        if record:
            to_return = network(deposit_min = record["deposit_min"],
                                withdraw_min = record["withdraw_min"],
                                withdraw_fee = record["withdraw_fee"],
                                name = record["name"])
            return to_return
        else:
            print(f'function get_best_network_for_coin {coin_name} can not get data')


    def get_coin_list_for_stock(self, stock):

        my_sql = f"""SELECT DISTINCT(c.name) FROM coin_network_for_stock as cnfs
                    JOIN stock AS s ON cnfs.stock_id = s.id
                    JOIN coins AS c ON cnfs.coin_id = c.id
                    WHERE s.name = '{stock}'"""

        df = pandas.read_sql(my_sql, self.conn)

        return df['name'].values.tolist()

    def get_common_coin_list(self):

        my_sql = f"""with bingx_coins as (
                     select distinct(c.name) from coin_network_for_stock as cnfs
                     join stock as s on cnfs.stock_id = s.id
                     join coins as c on cnfs.coin_id = c.id
                     where s.name = 'BINGX'), 
                     bybit_coins as (
                     select distinct(c.name) from coin_network_for_stock as cnfs
                     join stock as s on cnfs.stock_id = s.id
                     join coins as c on cnfs.coin_id = c.id
                     where s.name = 'BYBIT')
                     select bic.name
                     from bybit_coins as byc
                     join bingx_coins as bic on byc.name = bic.name"""

        df = pandas.read_sql(my_sql, self.conn)

        return df['name'].values.tolist()

    def init_local_db(self, recreate = False):
        try:
            cursor = self.conn.cursor()
            if recreate:
                self._drop()

            my_sql= """
            CREATE TABLE IF NOT EXISTS coins
            (
                id SERIAL PRIMARY KEY,
                name VARCHAR UNIQUE
            )
            """
            cursor.execute(my_sql)

            my_sql = """
            CREATE TABLE IF NOT EXISTS networks
            (
                id SERIAL PRIMARY KEY,
	            name VARCHAR UNIQUE
            )"""
            cursor.execute(my_sql)

            my_sql = """
            CREATE TABLE IF NOT EXISTS stock
            (
            	id SERIAL PRIMARY KEY,
	            name VARCHAR UNIQUE
            )"""
            cursor.execute(my_sql)

            my_sql = """
            CREATE TABLE IF NOT EXISTS coin_network_for_stock
            (
                id SERIAL PRIMARY KEY,
	            coin_id BIGINT,
	            network_id BIGINT,
	            stock_id BIGINT,
	            withdraw_fee VARCHAR,
	            deposit_min VARCHAR,
	            withdraw_min VARCHAR,
	            FOREIGN KEY (coin_id) REFERENCES coins(id) ON DELETE CASCADE,
	            FOREIGN KEY (network_id) REFERENCES networks(id) ON DELETE CASCADE,
	            FOREIGN KEY (stock_id) REFERENCES stock(id) ON DELETE CASCADE,
	            UNIQUE(coin_id, network_id, stock_id)
            )"""
            cursor.execute(my_sql)

            cursor.execute(psycopg2.sql.SQL(f"INSERT INTO stock(name) VALUES('BINGX')"))
            cursor.execute(psycopg2.sql.SQL(f"INSERT INTO stock(name) VALUES('BYBIT')"))

            self._create_balance_table()
            self._create_transaction_info_table()


        except psycopg2.OperationalError as e:
            print(f"Error: {e}")


    def _connect_to_db(self):
        conn_params = {
            "dbname": "stockBot",
            "user": "postgres",
            "password": "secret",
            "host": "localhost",
            "port": 5432
        }
        try:
            self.conn = psycopg2.connect(**conn_params)
            self.conn.autocommit = True
        except psycopg2.OperationalError as e:
            print(f"Error: {e}")

    def _drop(self):
        cursor = self.conn.cursor()
        cursor.execute(psycopg2.sql.SQL("""DO
                                        $$
                                        DECLARE
                                            obj_name text;
                                        BEGIN
                                            FOR obj_name IN
                                                SELECT tablename FROM pg_tables
                                                WHERE schemaname = 'public'
                                            LOOP
                                                EXECUTE format('DROP TABLE IF EXISTS %I CASCADE', obj_name);
                                            END LOOP;

                                            FOR obj_name IN
                                                SELECT sequencename FROM pg_sequences
                                                WHERE schemaname = 'public'
                                            LOOP
                                                EXECUTE format('DROP SEQUENCE IF EXISTS %I CASCADE', obj_name);
                                            END LOOP;

                                            FOR obj_name IN
                                                SELECT viewname FROM pg_views
                                                WHERE schemaname = 'public'
                                            LOOP
                                                EXECUTE format('DROP VIEW IF EXISTS %I CASCADE', obj_name);
                                            END LOOP;
                                        END;
                                        $$;
                                        """))


    def get_common_networks(self):

        my_sql = f"""SELECT * FROM public.coin_network_for_stock"""

        df = pandas.read_sql(my_sql, self.conn)

        return df

    def _create_balance_table(self):
        cursor = self.conn.cursor()
        cursor.execute(psycopg2.sql.SQL("""
            DO $$
            BEGIN
                CREATE TABLE IF NOT EXISTS balance
                (
                    id BIGSERIAL PRIMARY KEY,
	                current_balance NUMERIC,
	                date TIMESTAMP
                );
            END;
            $$;
        """))

    def _create_transaction_info_table(self):
        cursor = self.conn.cursor()
        cursor.execute(psycopg2.sql.SQL("""
                    DO $$
                    BEGIN
                        CREATE TABLE IF NOT EXISTS transaction_info
                        (
                            id SERIAL PRIMARY KEY,
                            balance_id BIGINT NOT NULL,
                            from_stock_id BIGINT NOT NULL,
                            to_stock_id BIGINT NOT NULL,
                            network_id BIGINT NOT NULL,
                            coin_id BIGINT NOT NULL,
        	                FOREIGN KEY (balance_id) REFERENCES balance(id) ON DELETE CASCADE,
        	                FOREIGN KEY (from_stock_id) REFERENCES stock(id) ON DELETE CASCADE,
        	                FOREIGN KEY (to_stock_id) REFERENCES stock(id) ON DELETE CASCADE,
        	                FOREIGN KEY (network_id) REFERENCES networks(id) ON DELETE CASCADE,
        	                FOREIGN KEY (coin_id) REFERENCES coins(id) ON DELETE CASCADE
                        );
                    END;
                    $$;
                """))

    def _write_sucseeded_transation(self, cur_balance, from_stock, to_stock, network, coin):
        cursor = self.conn.cursor()
        cursor.execute(psycopg2.sql.SQL(f"""
                    DO $$
                    DECLARE
                        new_balance_id BIGINT;
                        new_from_stock_id BIGINT;
                        new_to_stock_id BIGINT;
                        new_network_id BIGINT;
                        new_coin_id BIGINT;
                    BEGIN
                        INSERT INTO balance(current_balance, date)
                        VALUES ({cur_balance}, (SELECT NOW())) INTO new_balance_id;
                        
                        SELECT id INTO new_from_stock_id
                        FROM stock
                        WHERE name = '{from_stock}';
                        
                        SELECT id INTO new_to_stock_id
                        FROM stock
                        WHERE name = '{to_stock}';
                        
                        SELECT id INTO new_network_id
                        FROM networks
                        WHERE name = '{network}';
                        
                        SELECT id INTO new_coin_id
                        FROM coins
                        WHERE name = '{coin}';
                        
                        INSERT INTO transaction_info(balance_id, from_stock_id, to_stock_id, network_id, coin_id)
                        VALUES (new_balance_id, new_from_stock_id, new_to_stock_id, new_network_id, new_coin_id);
                    END;
                    $$;
                """))