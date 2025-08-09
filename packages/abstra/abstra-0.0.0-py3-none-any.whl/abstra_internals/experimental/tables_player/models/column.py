from dataclasses import dataclass
from typing import Optional


def find_table_column_by_id(dump: dict, column_id: str):
    for table in dump['tables']:
        for column in table['columns']:
            if column['id'] == column_id:
                return table, column
    raise ValueError(f"Column {column_id} not found in dump")


@dataclass
class ForeignKeyModel:
    table_name: str
    column_name: str

@dataclass
class ColumnModel:
    primary_key: bool
    name: str
    type: str
    foreign_key: Optional[ForeignKeyModel]

    @staticmethod
    def from_dto(dump: dict, id: str):
        dump_column = find_table_column_by_id(dump, id)[1]
        foreign_key = None
        if 'foreignKey' in dump_column:
            reference_table, reference_column = find_table_column_by_id(dump, dump_column['foreignKey']['columnId'])
            foreign_key = ForeignKeyModel(
                table_name=reference_table['name'],
                column_name=reference_column['name']
            )
        return ColumnModel(
            primary_key=dump_column['primaryKey'],
            name=dump_column['name'],
            type=dump_column['type'],
            foreign_key=foreign_key
        )