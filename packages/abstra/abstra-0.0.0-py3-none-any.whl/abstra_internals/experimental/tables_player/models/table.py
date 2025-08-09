from dataclasses import dataclass
from typing import List, Union

from .column import ColumnModel


@dataclass
class TableModel:
    name: str
    columns: List[ColumnModel]
    referrers: List[Union["TableModel", ColumnModel]]
    rows: List[dict]

    @staticmethod
    def from_dto(dump: dict, name: str):
        for table in dump['tables']:
            if table['name'] == name:
                dto = table
                break
        else:
            raise ValueError(f"Table {name} not found in dump")
        columns = [ColumnModel.from_dto(dump, c['id']) for c in dto['columns']]

        referrers = []
        for table in dump['tables']:
            for column in table['columns']:
                col = ColumnModel.from_dto(dump, column['id'])
                if col.foreign_key and col.foreign_key.table_name == name:
                    referrers.append((
                        TableModel.from_dto(dump, table['name']),
                        ColumnModel.from_dto(dump, column['id'])
                    ))
        
        rows = dto['data']
        return TableModel(name=name, columns=columns, rows=rows, referrers=referrers)