# from typing_extensions import Self
# import config.sqlalchemy_config as sqlalchemy_config

# from sqlalchemy import Engine, create_engine

# from loguru import logger

# class SqlalchcemyEngine:

#     __slots__ = ('engine',)
#     __instance = None
#     def __new__(cls, *args, **kwargs):
#         if cls.__instance is None:
#             cls.__instance = super().__new__(cls, *args, **kwargs)
#         return cls.__instance

#     def __init__(self) -> None:
#         if not hasattr(self, 'engine'):
#             logger.info(f'DBAPI: {sqlalchemy_config.SqlalchemyConfig.DBAPI}, Start create engine...')
#             self.engine = self.__create_engine()

#     # def create_session(self) -> Self:
#     #     pass


#     def __create_engine(self) -> Engine:
#         return create_engine(sqlalchemy_config.SqlalchemyConfig.DBAPI, echo=sqlalchemy_config.SqlalchemyConfig.ECHO)