from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine, text

from vlcishared.env_variables.secrets import get_secret
from vlcishared.tests.fixtures.db.schema_utils import borrar_funciones_y_procedimientos, borrar_tablas, copiar_funciones_y_procedimientos, copiar_tablas


@pytest.fixture
def mock_postgres_patch(monkeypatch, db_transaction):
    """
    Fixture que mockea PostgresConnector para ejecutar queries sobre una base de datos real (SQLite/PostgreSQL de prueba).

    - Redirige métodos como connect, execute y execute_query al engine de pruebas.
    - Permite testear sin conectarse a una base de datos real de producción.
    - Requiere la ruta del import de PostgresConnector.

    Parámetros:
    - ruta_importacion (str): Ruta completa donde se importa `PostgresConnector` (ej. "mi_paquete.mi_modulo.PostgresConnector").
    - execute_side_effect (callable|None): Lógica personalizada a ejecutar cuando se llama `execute`.
    - execute_query_side_effect (callable|None): Lógica personalizada a ejecutar cuando se llama `execute_query`.
    - call_procedure_side_effect (callable|None): Lógica personalizada a ejecutar cuando se llama `call_procedure`.
    - execute_multiple_queries_side_effect (callable|None): Lógica personalizada a ejecutar cuando se llama `execute_multiple_queries`.
    - insert_query_commit_side_effect (callable|None): Lógica personalizada a ejecutar cuando se llama `insert_query_commit`.

    Uso:
        def test_xxx(mock_db_patch):
            mock_db = mock_db_patch("modulo.donde.importa.PostgresConnector")
            mock_db.execute.assert_called_once()
    """

    def _patch(
        target_path: str,
        execute_side_effect=None,
        execute_query_side_effect=None,
        call_procedure_side_effect=None,
        execute_multiple_queries_side_effect=None,
        insert_query_commit_side_effect=None,
    ):
        mock_connector = MagicMock()

        mock_connector.connect.return_value = db_transaction
        mock_connector.close.return_value = None

        mock_connector.execute.side_effect = execute_side_effect or execute_side_effect_default(db_transaction)
        mock_connector.execute_query.side_effect = execute_query_side_effect or execute_query_side_effect_default(db_transaction)
        mock_connector.call_procedure.side_effect = call_procedure_side_effect or call_procedure_side_effect_default(db_transaction)
        mock_connector.execute_multiple_queries.side_effect = execute_multiple_queries_side_effect or execute_multiple_queries_side_effect_default(
            db_transaction
        )
        mock_connector.insert_query_commit.side_effect = insert_query_commit_side_effect or insert_query_commit_side_effect_default(db_transaction)

        mock_connector.engine = db_transaction.engine
        monkeypatch.setattr(target_path, lambda *args, **kwargs: mock_connector)
        return mock_connector

    yield _patch


@pytest.fixture
def db_transaction(connection):
    transaction = connection.begin_nested()
    yield connection
    transaction.rollback()


@pytest.fixture(scope="session")
def connection():
    """
    Crea una conexión de SQLAlchemy contra una base de datos PostgreSQL de prueba.

    - Devuelve una conexión viva que se cierra al finalizar el test.
    - Usado por otros fixtures para ejecutar queries reales en un entorno aislado.
    """
    user = get_secret("GLOBAL_DATABASE_POSTGIS_LOGIN_TEST")
    password = get_secret("GLOBAL_DATABASE_POSTGIS_PASSWORD_TEST")
    port = get_secret("GLOBAL_DATABASE_POSTGIS_PORT_TEST")
    host = get_secret("GLOBAL_DATABASE_POSTGIS_HOST_TEST")
    database = get_secret("GLOBAL_DATABASE_POSTGIS_DATABASE_TEST")
    schema = get_secret("GLOBAL_DATABASE_POSTGIS_SCHEMA_TEST")
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(url)
    connection = engine.connect()
    connection.execute(text(f"SET search_path TO {schema}"))
    yield connection
    connection.close()
    engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def setup_esquema_test_desde_vlci2(connection):
    """
    Fixture que se ejecuta una vez por sesión de pytest (scope="session") y automáticamente en todas las pruebas (autouse=True).

    - Copia las tablas y funciones/procedimientos del esquema 'vlci2' al esquema de test.
    - Al finalizar la sesión, elimina las tablas y funciones/procedimientos del esquema de test.

    Si se necesita preparar el esquema de test a partir de un origen distinto, se puede definir un nuevo fixture personalizado en el módulo correspondiente:
    @pytest.fixture(scope="session", autouse=True)
        def setup_esquema_xxx_desde_yyy(connection):
            copiar_esquema(connection, esquema_yyy, esquema_xxx)
            yield
            limpiar_esquema(connection, esquema_xxx)
    """
    esquema_vlci2 = get_secret("GLOBAL_DATABASE_POSTGIS_SCHEMA_VLCI2")
    esquema_test = get_secret("GLOBAL_DATABASE_POSTGIS_SCHEMA_TEST")
    copiar_esquema(connection, esquema_vlci2, esquema_test)
    yield
    limpiar_esquema(connection, esquema_test)


def copiar_esquema(connection, esquema_origen, esquema_destino):
    """
    Copia tablas y funciones/procedimientos del esquema origen al destino usando la misma conexión.
    """
    copiar_tablas(connection, esquema_origen, esquema_destino)
    copiar_funciones_y_procedimientos(connection, esquema_origen, esquema_destino)


def limpiar_esquema(connection, esquema):
    """
    Borra tablas y funciones/procedimientos del esquema indicado usando la misma conexión.
    """
    borrar_tablas(connection, esquema)
    borrar_funciones_y_procedimientos(connection, esquema)


def execute_side_effect_default(transaction):
    def _execute(query, params=None):
        return transaction.execute(query, params or {})

    return with_rollback(transaction, _execute)


def execute_side_effect_reemplazo_esquema(transaction, esquema_original="vlci2", esquema_reemplazo="test_component"):  # noqa: F811
    def _execute(query, params=None):
        query_modificada = str(query).replace(esquema_original, esquema_reemplazo)
        return transaction.execute(text(query_modificada), params or {})

    return with_rollback(transaction, _execute)


def execute_query_side_effect_default(transaction):
    def _execute_query(query, params=None):
        return transaction.execute(text(query), params or {})

    return with_rollback(transaction, _execute_query)


def call_procedure_side_effect_default(transaction):
    def _call_procedure(procedure_name, *params, is_function=False):
        param_placeholders = ", ".join([f":p{i}" for i in range(len(params))])
        param_dict = {f"p{i}": params[i] for i in range(len(params))}
        if is_function:
            result = transaction.execute(text(f"SELECT {procedure_name}({param_placeholders})"), param_dict)
            return result.fetchall()
        else:
            transaction.execute(text(f"CALL {procedure_name}({param_placeholders})"), param_dict)
            return []

    return with_rollback(transaction, _call_procedure)


def execute_multiple_queries_side_effect_default(transaction):
    def _execute_multiple_queries(queries_with_params):
        for query, params in queries_with_params:
            transaction.execute(text(query), params)

    return with_rollback(transaction, _execute_multiple_queries)


def insert_query_commit_side_effect_default(transaction):
    def _insert_query_commit(sql_queries, table_name, schema_name, df):
        for query in sql_queries:
            transaction.execute(text(query))
        if df is not None:
            df.to_sql(name=table_name, schema=schema_name, con=transaction, index=False, if_exists="append")

    return with_rollback(transaction, _insert_query_commit)


def with_rollback(transaction, func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            transaction.rollback()
            raise

    return wrapped
