# TODO We might rename it to GenericCrud

from abc import ABC, abstractmethod
# from logger_local.MetaLogger import MetaLogger


class GenericCrudAbstract(ABC):  # , metaclass=MetaLogger):
    # or  class MetaLogger(ABCMeta):
    # def __init_subclass__(cls, **kwargs):
    #     super().__init_subclass__(**kwargs)
    # Your logging setup here

    # @property
    # @abstractmethod
    # def version(self):
    #     pass  # Abstract property, must be implemented by subclasses

    @abstractmethod
    def insert(self, *, schema_name: str = None, table_name: str = None,
               data_dict: dict = None,
               ignore_duplicate: bool = False, commit_changes: bool = True
               ) -> int:
        pass

    # TODO We should add all the GenericCrudMysql methods here
