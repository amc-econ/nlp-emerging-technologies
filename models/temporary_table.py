from pandas.io.sql import SQLTable, pandasSQL_builder


class TemporaryTable(SQLTable):
    
    """
    Code snippet taken from https://gist.github.com/alecxe/44682f79b18f0c82a99c
    """
    
    """Overriding the _create_table_setup() method trying to make the table created temporary."""
    
    def _create_table_setup(self):
        from sqlalchemy import Table, Column, PrimaryKeyConstraint

        column_names_and_types = \
            self._get_column_names_and_types(self._sqlalchemy_type)

        columns = [Column(name, typ, index=is_index)
                   for name, typ, is_index in column_names_and_types]

        if self.keys is not None:
            if not com.is_list_like(self.keys):
                keys = [self.keys]
            else:
                keys = self.keys
            pkc = PrimaryKeyConstraint(*keys, name=self.name + '_pk')
            columns.append(pkc)

        schema = self.schema or self.pd_sql.meta.schema

        # At this point, attach to new metadata, only attach to self.meta
        # once table is created.
        from sqlalchemy.schema import MetaData
        meta = MetaData(self.pd_sql, schema=schema)