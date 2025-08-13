import logging
from typing import Any, List, Sequence

import pandas as pd
from sqlalchemy import Row, TextClause, create_engine, text
from sqlalchemy.orm import sessionmaker

from vlcishared.utils.interfaces import ConnectionInterface


class PostgresConnector(ConnectionInterface):
    _instance = None

    @classmethod
    def instance(cls):
        if not cls._instance:
            raise Exception("PostgresConnector no ha sido inicializado aún.")
        return cls._instance

    def __new__(cls, host, port, database, user, password):
        if cls._instance is None:
            cls._instance = super(PostgresConnector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, host: str, port: str, database: str, user: str, password: str):
        if self._initialized:
            return  # Ya fue inicializado, evitar reiniciar
        self.log = logging.getLogger()
        self.db_name = database
        self.connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.connect()
        self._initialized = True

    def connect(self):
        """Función que se conecta a la base de datos
        definida en el constructor"""
        self.engine = create_engine(self.connection_string)
        self.session_maker = sessionmaker(bind=self.engine)
        self.session = self.session_maker()
        self.log.info(f"Conectado a {self.db_name}")

    def close(self):
        """Cierra la conexión con la base de datos"""
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()
        self.log.info(f"Desconectado de {self.db_name}.")

    def call_procedure(self, procedure_name: str, *params: Any, is_function: bool = False) -> Sequence[Row[Any]]:
        """Llama a funciones o procedimientos almacenados en BD,
        recibe el nombre y los parámetros"""
        try:
            param_placeholders = ", ".join([f":p{i}" for i in range(len(params))])
            param_dict = {f"p{i}": params[i] for i in range(len(params))}
            if is_function:
                sql = text(f"SELECT {procedure_name}({param_placeholders})")
                result = self.session.execute(sql, param_dict)
                self.session.commit()
                return result.fetchall()
            else:
                sql = text(f"CALL {procedure_name}({param_placeholders})")
                self.session.execute(sql, param_dict)
                self.session.commit()
                return []
        except Exception as e:
            self.session.rollback()
            self.log.error(f"Fallo llamando a {procedure_name}: {e}")
            raise e

    def execute(self, query: TextClause, params: dict):
        with self.engine.connect() as conexion:
            result = conexion.execute(query, params)
            conexion.commit()
        return result
    
    def execute_query(self, query: str, params: dict = None) -> Any:
        try:
            with self.engine.connect() as conexion:
                result = conexion.execute(text(query), params or {})
            return result
        except Exception as e:
            self.log.error(f"Error al ejecutar la query: {e}")
            raise


        
    def execute_multiple_queries(self, queries_with_params):
        """
        Ejecuta múltiples queries dentro de una única transacción.
        
        Args:
            queries_with_params (List[Tuple[str, dict]]): 
                Lista de tuplas donde cada tupla contiene:
                - Una query SQL parametrizada.
                - Un diccionario con los valores de los parámetros.
        
        Si alguna query falla, se hace rollback de toda la transacción.
        """
        try:
            with self.engine.begin() as conexion:
                for query, params in queries_with_params:
                    conexion.execute(text(query), params)
            
            self.log.info("Todas las queries se ejecutaron correctamente y se hizo COMMIT.")
        
        except Exception as e:
            self.log.error(f"Error al ejecutar las queries. Se ha hecho rollback de la transacción: {e}")
            raise

    def insert_query_commit(self, sql_queries: List[str], table_name: str, schema_name: str, df: pd.DataFrame) -> None:
        """Insert multiple queries and optionally a DataFrame within a transaction.

        Args:
            sql_queries (List[str]): A list of SQL queries to be executed.
            table_name (str): The name of the table for inserting the DataFrame.
            schema_name (str): The schema name where the table exists.
            df (Optional[pd.DataFrame]): The DataFrame to be inserted, default is None,
            si reciven datos repetivos lanza error poruq no hace update, solo insert.
        """
        try:
            with self.engine.connect() as connection:
                for sql_query in sql_queries:
                    connection.execute(text(sql_query))
                if df is not None:
                    df.to_sql(name=table_name, schema=schema_name, con=connection, index=False, if_exists="append")
                connection.commit()

        except Exception as e:
            self.log.error(f"Failed to execute query: {e}")
            raise
