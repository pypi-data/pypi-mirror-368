# db_client.py

import os

import pandas as pd
import psycopg2
import yaml
from pandas import PeriodDtype
from psycopg2 import sql, connect
from psycopg2.extras import execute_values

# import logging
from hmcis_packs.logger.logger_config import setup_logger

# ========== Конфигурация логирования ==========
# Папка для логов — создаём, если нет
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, 'database_client.log')

# # Настраиваем корневой логгер один раз при загрузке модуля
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s %(levelname)s: %(message)s',
#     handlers=[
#         logging.StreamHandler(sys.stdout),  # в консоль (stdout)
#         logging.FileHandler(LOG_FILE, encoding='utf-8')  # в файл
#     ]
# )

logger = setup_logger(__name__)


# ===============================================


class DatabaseClient:
    def __init__(self, config_path=None):
        if config_path is None:
            user_home = os.path.expanduser("~")
            config_path = os.path.join(user_home, "db_config.yaml")

        with open(config_path, 'r', encoding='utf-8') as f:
            self.db_config = yaml.safe_load(f)

    def _map_dtype(self, dtype):
        """
        Маппинг pandas dtype → PostgreSQL тип.
        Поддерживает PeriodDtype, float, int, bool, datetime, object и fallback BYTEA.
        """
        # Обработка периодов. Рекомендуем использовать isinstance с PeriodDtype
        if isinstance(dtype, PeriodDtype):
            # Сохраняем период как начало/конец периода в формате TIMESTAMP
            return 'TIMESTAMP'
        if pd.api.types.is_float_dtype(dtype):
            return 'NUMERIC'
        if pd.api.types.is_integer_dtype(dtype):
            return 'INTEGER'
        if pd.api.types.is_bool_dtype(dtype):
            return 'BOOLEAN'
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return 'TIMESTAMP'
        if dtype == 'object':
            return 'VARCHAR'
        return 'BYTEA'

    def save_df_to_db(self,
                      df: pd.DataFrame,
                      table_name: str,
                      schema: str = 'IFRS Reports',
                      binary_columns: list[str] = None):
        """
        Сохраняет DataFrame в PostgreSQL, создаёт схему/таблицу при необходимости,
        и производит пакетную вставку через execute_values.
        Разделено на 2 коммита: сначала схема, потом таблица + данные.
        """
        if binary_columns is None:
            binary_columns = []

        # Убираем столбцы с пустыми именами
        df = df.loc[:, df.columns.str.strip() != '']
        df = df.iloc[:, df.columns.notna()]
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()
        try:
            # 1) Создаём схему и коммитим сразу, чтобы не откатился вместе с ошибками ниже
            cursor.execute(
                sql.SQL("CREATE SCHEMA IF NOT EXISTS {}")
                .format(sql.Identifier(schema))
            )
            conn.commit()

            # 2) Готовим DDL для таблицы
            cols_ddl = []
            for col, dtype in zip(df.columns, df.dtypes):
                if col in binary_columns:
                    pg_type = 'BYTEA'
                else:
                    pg_type = self._map_dtype(dtype)
                cols_ddl.append(f"{sql.Identifier(col).as_string(conn)} {pg_type}")

            create_sql = sql.SQL(
                "CREATE TABLE IF NOT EXISTS {schema}.{table} ({fields})"
            ).format(
                schema=sql.Identifier(schema),
                table=sql.Identifier(table_name),
                fields=sql.SQL(", ").join(sql.SQL(c) for c in cols_ddl),
            )
            cursor.execute(create_sql)

            # 3) Очищаем таблицу перед вставкой
            truncate_sql = sql.SQL("TRUNCATE {schema}.{table}").format(
                schema=sql.Identifier(schema),
                table=sql.Identifier(table_name),
            )
            cursor.execute(truncate_sql)

            # 4) Готовим пакетную вставку
            insert_sql = sql.SQL(
                "INSERT INTO {schema}.{table} ({fields}) VALUES %s"
            ).format(
                schema=sql.Identifier(schema),
                table=sql.Identifier(table_name),
                fields=sql.SQL(', ').join(map(sql.Identifier, df.columns))
            )
            records = []
            for row in df.itertuples(index=False, name=None):
                rec = []
                for val, col in zip(row, df.columns):
                    if col in binary_columns:
                        rec.append(psycopg2.Binary(val))
                    else:
                        rec.append(val)
                records.append(tuple(rec))

            execute_values(cursor, insert_sql.as_string(conn), records, page_size=10000)

            # 5) Фиксируем создание таблицы и вставку данных
            conn.commit()
            logger.info(f"✅ Данные успешно загружены в '{schema}.{table_name}'")

        except Exception as e:
            conn.rollback()
            logger.error("💀 Ошибка при сохранении в БД: %s", e)
            raise
        finally:
            cursor.close()
            conn.close()

    def fetch_data(self, query: str, params: tuple = None, schema: str = None):
        """
        Подключается к БД по параметрам из конфига и выполняет запрос.

        :param query: SQL-запрос (строка или sql.SQL)
        :param params: параметры для подстановки в запрос
        :param schema: схема в бд, из которой читааем данные
        :return: список кортежей с результатами
        """
        conn = None
        try:
            conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config.get('port', 5432),
                dbname=self.db_config['dbname'],
                user=self.db_config['user'],
                password=self.db_config['password'],
            )
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()
        except Exception as e:
            print(f"Ошибка при работе с БД: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def execute_custom(self, raw_sql: str, schema: str, params: tuple = None):
        """
        Выполняет пользовательский SQL, подставляя имя схемы.

        :param raw_sql: SQL со вставкой {schema}, например
                        "SELECT * FROM {schema}.my_table WHERE x = %s"
        :param schema: имя схемы для подстановки
        :param params: кортеж параметров для %s-плейсхолдеров
        :return: результат fetchall()
        """
        # Собираем запрос, безопасно экранируя имя схемы
        query = sql.SQL(raw_sql).format(
            schema=sql.Identifier(schema)
        )

        conn = psycopg2.connect(**self.db_config)
        try:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                rows = cur.fetchall()
                # Получаем имена колонок
                columns = [desc[0] for desc in cur.description]
                return rows, columns
        finally:
            conn.close()

    def stream_data_with_timer(self,
                               raw_sql: str,
                               schema: str,
                               params: tuple = None,
                               chunk_size: int = 10_000):
        """
        Генератор: по порциям отдаёт (rows, columns).
        columns возвращается только при первой порции, далее None.
        """
        query = sql.SQL(raw_sql).format(schema=sql.Identifier(schema))
        conn = psycopg2.connect(**self.db_config)

        try:
            with conn.cursor(name="streaming_cursor") as cur:
                cur.itersize = chunk_size
                cur.execute(query, params or ())

                first_batch = True
                while True:
                    rows = cur.fetchmany(chunk_size)
                    if not rows:
                        break

                    if first_batch:
                        columns = [desc[0] for desc in cur.description]
                        yield rows, columns
                        first_batch = False
                    else:
                        yield rows, None
        finally:
            conn.close()

    def get_total_count(self, raw_sql: str, schema: str, params: tuple = None) -> int:
        """
        Возвращает общее число строк, которое выдаст raw_sql (без LIMIT).
        """
        count_sql = f"SELECT COUNT(*) FROM ({raw_sql}) AS subquery"
        query = sql.SQL(count_sql).format(schema=sql.Identifier(schema))
        with psycopg2.connect(**self.db_config) as conn, conn.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchone()[0]

    def extract_data_with_timer(self,
                                raw_sql: str,
                                schema: str,
                                params: tuple = None,
                                chunk_size: int = 10_000):
        total = self.get_total_count(raw_sql, schema, params)
        query = sql.SQL(raw_sql).format(schema=sql.Identifier(schema))

        conn = connect(**self.db_config)
        try:
            with conn.cursor(name="stream_cursor") as cur:
                cur.itersize = chunk_size
                cur.execute(query, params or ())

                first = True
                while True:
                    rows = cur.fetchmany(chunk_size)
                    if not rows:
                        break

                    if first:
                        columns = [desc[0] for desc in cur.description]
                        yield rows, columns, total
                        first = False
                    else:
                        yield rows, None, total
        finally:
            conn.close()


if __name__ == '__main__':
    dbclient = DatabaseClient()
    # language=SQL
    query = '''
WITH base AS
     (
             SELECT
                     a.*                                                                      ,
                     substring("Asset description" FROM '((LBE|XW|Z94|KM)[[:alnum:]_]*)') AS code,
                     regexp_replace("Asset description", '\s*(LBE|XW|Z94|KM)[[:alnum:]_]*$',
                     -- вырежем VIN + пробелы в конце
                     '' )                                                              AS element_left_part
             FROM
                     "Cars"."ANLA" AS a
             WHERE
                     "Deact.Date" = '' )
SELECT
        b."Asset description",
        b.code               ,
--        b.class               ,
        b.element_left_part  ,
        mp.model_norm,
        b."Class"
FROM
        base AS b
LEFT JOIN
        LATERAL
        (
                SELECT
                        model_norm
                FROM
                        "Cars".model_pattern
                WHERE
                        b.element_left_part ~* model_pattern.pattern
                ORDER BY
                        model_norm
                LIMIT 1 ) AS mp
ON
        true
--where b."Class" = 'HA01B08'
   '''

    rows, columns = dbclient.execute_custom(raw_sql=query, schema='Cars')
    df = pd.DataFrame(rows, columns=columns)

    pass
