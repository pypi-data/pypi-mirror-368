import traceback
from contextlib import contextmanager
from typing import Union, List, Any, Generator, Optional
from urllib import parse

import pandas as pd
import geopandas as gpd

from pydantic import BaseModel
from shapely import wkb, wkt
from sqlalchemy import (
    Engine, create_engine, Select, text, MetaData, Table, Column, Integer, String,
    inspect, func, select
)
from sqlalchemy.exc import SQLAlchemyError, NoSuchTableError
from sqlalchemy.orm import sessionmaker, Session, joinedload
from geoalchemy2 import WKBElement


from digitalarzengine.utils.crypto import CryptoUtils
from digitalarzengine.utils.singletons import da_logger

# from dotenv import load_dotenv
# load_dotenv()




class DBString(BaseModel):
    """Database connection details"""
    host: str
    user: str
    password: str
    name: str
    port: str


class DBParams:
    """Encapsulates DB engine and connection string"""

    def __init__(self,  con_str: Union[dict, DBString], engine_name: str=None):
        self.engine_name= con_str["engine"] if engine_name is None else engine_name
        self.con_str = con_str.get("file_path") if engine_name == "sqlite" and isinstance(con_str, dict) else (
            DBString(**con_str) if isinstance(con_str, dict) else con_str
        )

    def __eq__(self, other):
        if not isinstance(other, DBParams):
            return False
        return isinstance(self.con_str, DBString) and self.con_str == other.con_str


class DBManager:
    """General database operations manager"""

    def __init__(self, db_info: Union[DBParams, Engine]):
        self.engine = db_info if isinstance(db_info, Engine) else self.create_sql_alchemy_engine(db_info)
        self.db_name = self.engine.url.database
        if self.engine is None:
            raise Exception("Failed to create SQL Alchemy engine")

    @staticmethod
    def from_setting(db_config, is_encrypted= False, is_spatial_manager=True):
        """
        "default": {
            "engine": "postgresql",
            "host": os.environ.get("DB_HOST") if not IS_LOCAL else "localhost",
            "name": os.environ.get("DB_PDMA"),
            "port": os.environ.get("DB_PORT"),
            "user": os.environ.get("DB_USER"),
            "password": os.environ.get("DB_PASSWORD")
        },
        """
        db_config["engine_name"] = db_config["engine"]
        db_config["password"] = CryptoUtils().decrypt_txt(db_config['password']) if is_encrypted else db_config['password']
        params = DBParams(db_config)
        return GeoDBManager(params) if is_spatial_manager else  DBManager(params)

    # @staticmethod
    # def from_config(db_key: str):
    #     """
    #         Create a DBManager instance using the `DATABASES` dictionary from a settings module.
    #         :param db_key: Key in the DATABASES dictionary (e.g., "drm")
    #         :return: DBManager instance
    #    """
    #     db_config = DATABASES[db_key]
    #     password = CryptoUtils().decrypt_txt(db_config['PASSWORD'])
    #     return DBManager(
    #         user=db_config["USER"],
    #         password=password,
    #         host=db_config["HOST"],
    #         port=int(db_config["PORT"]),
    #         dbname=db_config["NAME"],
    #         driver=f"{db_config.get('ENGINE', 'postgresql+psycopg2')}"
    #     )

    def create_sql_alchemy_engine(self, config: DBParams) -> Engine:
        """Create engine using SQLAlchemy"""
        try:
            if config.engine_name == "sqlite":
                db_string = f"{config.engine_name}:///{config.con_str}"
            else:
                params = config.con_str
                db_string = f"{config.engine_name}://{params.user}:{parse.quote(params.password)}@{params.host}:{params.port}/{params.name}"

            return create_engine(
                db_string,
                echo=False,
                pool_size=10,
                max_overflow=5,
                pool_timeout=30,
                pool_recycle=1200,
                pool_pre_ping=True
            )
        except Exception as e:
            da_logger.exception(f"Error creating SQLAlchemy engine: {e}")
            raise

    def get_engine(self) -> Engine:
        """Get active SQLAlchemy engine"""
        return self.engine

    def get_session(self) -> Session:
        """Get a new DB session"""
        return sessionmaker(bind=self.engine, autocommit=False, autoflush=False)()

    @contextmanager
    def managed_session(self, session: Optional[Session] = None) -> Generator[Session, None, None]:
        """Context manager for session lifecycle"""
        if session:
            yield session
        else:
            new_session = self.get_session()
            try:
                yield new_session
                new_session.commit()
            except Exception as e:
                new_session.rollback()
                da_logger.warning(f"Session rollback due to: {e}")
                traceback.print_exc()
                raise
            finally:
                new_session.close()

    def get_sqlalchemy_table(self, table_name: str, schema_name: str = 'public') -> Optional[Table]:
        """Load a table with schema info"""
        try:
            if '.' in table_name:
                schema_name, table_name = table_name.split('.')
            metadata = MetaData()
            return Table(table_name, metadata, autoload_with=self.engine, schema=schema_name)
        except NoSuchTableError:
            da_logger.warning(f"Table not found: {schema_name}.{table_name}")
            return None
        except Exception:
            traceback.print_exc()
            return None

    def execute_stmt_as_df(self, stmt: Union[str, Select, Table], session: Optional[Session] = None,
                           enum_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Run query and return results as DataFrame"""
        try:
            with self.managed_session(session) as sess:
                if isinstance(stmt, Select):
                    rs = sess.execute(stmt)
                elif isinstance(stmt, Table):
                    rs = sess.execute(select(stmt))
                else:
                    rs = sess.execute(text(stmt))
                df = pd.DataFrame(rs.fetchall())
                if not df.empty:
                    df.columns = rs.keys()
                    if enum_columns:
                        for col in enum_columns:
                            if col in df.columns:
                                df[col] = df[col].apply(lambda x: x.value if hasattr(x, "value") else x)
                return df
        except SQLAlchemyError as e:
            da_logger.error(f"Error executing query: {e}")
            return pd.DataFrame()

    def get_query_data(self, query: Union[Table, Select, str], external_session: Optional[Session] = None) -> Any:
        """Execute query and return raw results"""
        try:
            with self.managed_session(external_session) as session:
                if isinstance(query, Table):
                    return session.query(query).all()
                elif isinstance(query, Select):
                    return session.execute(query).fetchall()
                else:
                    return session.execute(text(query)).fetchall()
        except SQLAlchemyError as e:
            da_logger.error(f"Error executing query: {e}")
            return []

    def execute_query_as_dict(self, query: Union[str, Select], session: Optional[Session] = None) -> List[dict]:
        """Return query results as list of dicts"""
        df = self.execute_stmt_as_df(query, session=session)
        return df.to_dict(orient='records')

    def execute_dml(self, stmt: Union[str, Select], session: Optional[Session] = None) -> bool:
        """Execute insert/update/delete"""
        try:
            with self.managed_session(session) as sess:
                sess.execute(text(stmt) if isinstance(stmt, str) else stmt)
                sess.commit()
            return True
        except SQLAlchemyError as e:
            da_logger.error(f"Error executing DML: {e}")
            traceback.print_exc()
            return False

    def execute_ddl(self, stmt: str) -> bool:
        """Execute create/alter/drop"""
        try:
            with self.managed_session() as session:
                session.execute(text(stmt))
                session.commit()
                da_logger.info("DDL executed successfully")
            return True
        except SQLAlchemyError as e:
            da_logger.error(f"Error executing DDL: {e}")
            traceback.print_exc()
            return False

    def is_table(self, table_name):
        """
        Check if a table exists.
        """
        inspector = inspect(self.engine)
        return table_name in inspector.get_table_names()

    def get_tables(self) -> List[Table]:
        """Return all tables as SQLAlchemy Table objects"""
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        return list(metadata.tables.values())

    def get_tables_names(self) -> List[str]:
        """Return all table names"""
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        return list(metadata.tables.keys())

    def table_to_df(self, tbl: Union[Table, str, Select]):
        """
        Convert a table or SELECT statement results to a Pandas DataFrame.
        """
        if isinstance(tbl, str):
            tbl = self.get_sqlalchemy_table(tbl)
        data = self.get_query_data(tbl)
        return pd.DataFrame(data)

    def terminate_idle_connections(self, idle_cutoff_minutes: int = 1, session: Session = None) -> int:
        """
        Terminates idle PostgreSQL connections idle for more than the specified number of minutes.
        """
        external_session = session is not None
        if not external_session:
            session = self.get_session()

        try:
            if self.engine.url.drivername.startswith("postgresql"):
                kill_stmt = text("""
                                 SELECT pg_terminate_backend(pid)
                                 FROM pg_stat_activity
                                 WHERE state = 'idle'
                                   AND state_change < now() - (:minutes || ' minutes')::interval
                                   AND pid <> pg_backend_pid()
                                   AND datname = :db_name;
                                 """)
                result = session.execute(kill_stmt, {'minutes': str(idle_cutoff_minutes), 'db_name': self.db_name})
                if not external_session:
                    session.commit()
                return result.rowcount
            return 0
        finally:
            if not external_session:
                session.close()

    def execute_query_as_one(self, query: Union[str, Select], session: Optional[Session] = None) -> Any:
        """
        Execute a query and return a single row.
        """
        try:
            with self.managed_session(session=session) as session:
                if isinstance(query, str):
                    query_obj = text(query)
                    row = session.execute(query_obj).mappings().first()
                    result = dict(row) if row else None
                else:
                    query_obj = query.options(joinedload('*'))
                    obj = session.execute(query_obj).scalars().first()
                    result = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')} if obj else None
                return result
        except SQLAlchemyError as e:
            print(f"Error executing query: {e}")
            traceback.print_exc()
            return None

    def exists(self, stmt: Select):
        """
        Check if a row exists based on the given SELECT statement.
        """
        with self.managed_session() as session:
            return session.execute(stmt).first() is not None


class GeoDBManager(DBManager):
    """Geo-enabled database manager"""

    @staticmethod
    def get_geometry_cols(table: Table) -> list:
        """Return all geometry columns from a table"""
        return [col for col in table.columns if 'geometry' in str(col.type)]

    def get_geom_col_srid(self, tbl: Table, geom_col: Column) -> int:
        """Get SRID from geometry column"""
        try:
            with self.managed_session() as session:
                res = session.query(func.ST_SRID(tbl.c[geom_col.name])).first()
                return res[0] if res and res[0] else geom_col.type.srid or 0
        except Exception:
            return geom_col.type.srid or 0

    @staticmethod
    def data_to_gdf(data, geom_col: str, srid=0, is_wkb=True) -> gpd.GeoDataFrame:
        """Convert query results to GeoDataFrame"""
        if not data:
            return gpd.GeoDataFrame()

        gdf = gpd.GeoDataFrame(data)
        try:
            if is_wkb:
                gdf["geom"] = gdf[geom_col].apply(
                    lambda x: wkb.loads(bytes(x.data)) if isinstance(x, WKBElement) else wkb.loads(x, hex=True)
                )
            else:
                gdf["geom"] = gdf[geom_col].apply(lambda x: wkt.loads(str(x)))
            if geom_col != "geom":
                gdf.drop(columns=[geom_col], inplace=True)
            gdf.set_geometry("geom", inplace=True)
            if srid:
                gdf.set_crs(srid, inplace=True)
        except Exception as e:
            da_logger.warning(f"Error converting to GeoDataFrame: {e}")
            return gpd.GeoDataFrame()
        return gdf

    def table_to_gdf(self, tbl: Union[Table, str], geom_col_name="geom") -> gpd.GeoDataFrame:
        """Convert spatial table to GeoDataFrame"""
        if isinstance(tbl, str):
            tbl = self.get_sqlalchemy_table(tbl)
        if tbl is None:
            return gpd.GeoDataFrame()

        geom_cols = self.get_geometry_cols(tbl)
        if not geom_cols:
            return gpd.GeoDataFrame()

        data = self.get_query_data(select(tbl))
        srid = self.get_geom_col_srid(tbl, geom_cols[0])
        return self.data_to_gdf(data, geom_col_name, srid)

    def execute_stmt_as_gdf(
            self,
            stmt: Union[str, Select, Table],
            geom_col: str = 'geom',
            srid: int = 0,
            is_wkb: bool = True,
            session: Optional[Session] = None
    ) -> gpd.GeoDataFrame:
        """
        Executes a query and returns the result as a GeoDataFrame.

        :param stmt: SQL statement (str, Select, or Table).
        :param geom_col: Name of the geometry column.
        :param srid: EPSG code for coordinate reference system.
        :param is_wkb: Whether the geometry is in WKB format.
        :param session: Optional SQLAlchemy session.
        :return: GeoDataFrame with geometry column.
        """
        try:
            data = self.get_query_data(stmt, session)
            return self.data_to_gdf(data, geom_col, srid, is_wkb)
        except Exception as e:
            da_logger.warning(f"Error executing stmt as GDF: {e}")
            traceback.print_exc()
            return gpd.GeoDataFrame()

    def get_spatial_table_names(self, schema: Optional[str] = None) -> List[str]:
        """List all tables containing geometry columns"""
        inspector = inspect(self.engine)
        spatial_tables = []
        for tbl_name in inspector.get_table_names(schema=schema):
            table = self.get_sqlalchemy_table(tbl_name)
            if table is not None and self.get_geometry_cols(table):
                spatial_tables.append(tbl_name)
        return spatial_tables

    def create_xyz_cache_table(self, table_name: str):
        """
        Create a table for XYZ cache data.
        """
        meta_data = MetaData()
        xyz_table = Table(table_name, meta_data,
                          Column('id', Integer, primary_key=True, autoincrement=True),
                          Column('x', Integer),
                          Column('y', Integer),
                          Column('z', Integer),
                          Column('mvt', String))
        meta_data.create_all(self.engine)
        print(f"Table '{table_name}' created.")
        return xyz_table

    def delete_xyz_cache_table(self, table_name: str):
        """
        Drop the specified XYZ cache table.
        """
        meta_data = MetaData()
        xyz_table = Table(table_name, meta_data, autoload_with=self.engine)
        xyz_table.drop(self.engine, checkfirst=True)
        print(f"Table '{table_name}' deleted.")
