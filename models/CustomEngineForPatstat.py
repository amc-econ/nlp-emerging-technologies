"""
# Contains a custom Engine for querying the PATSTAT installation on the Server I am using
# You may want to define a different engine according to your installation
"""

# Required libraries
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import tempfile
import pandas.core.common as com
from pandas.io.sql import SQLTable, pandasSQL_builder
import warnings

# Loading model parameters
import Parameters as param





class CustomEngineForPATSTAT:
    
    """
    This class define an engine able to query PATSTAT and retrive the data via SQLalchemy
    """
    
    def __init__(self, engine):
        
        """
        Instantiation of the model
        """
        
        self.engine = engine
        print('---------------------------------------')
        print('CustomEngineForPATSTAT instanciated.')
        print('---------------------------------------')
        
        
    def _Run_Engine_step_1(self, technology_classes_list, start_date, end_date):
        
        """
        We retrieve the primary information about the patent, so as to filter them before querying again:
        # 1. IDs
        # 2. Technology class to select them (other technology classes will be with other queries)
        # 3. Family id
        # 4. Filling date
        # 5. Number of patent citations at the DOCDB family level
        """
        
        # Unpacking parameters
        eng = self.engine
        
        TABLE_PRIMARY_INFO = pd.DataFrame()
        for technology_class in technology_classes_list:
            print('-> Retrieving the patent ids corresponding to the technology class', technology_class,
          'filled between',start_date ,'and', end_date )
            t = self.read_sql_tmpfile(param.sql_query_PATENT_PRIMARY_INFO.format(technology_class, start_date, end_date), eng)
            TABLE_PRIMARY_INFO = pd.concat([TABLE_PRIMARY_INFO, t])
        
        return TABLE_PRIMARY_INFO
        
    
    def _Run_Engine_step_2(self,
                           list_patent_ids, 
                           technology_classes_list,
                           start_date,
                           end_date):
        
        """
        Running the engine to retrive all necessary data from the PATSTAT Postgress database
        """
        
        # Unpacking parameters
        eng = self.engine
        # Local variables
        temp_SQL_table_1 = 'temporary_table_patent_ids'
        temp_SQL_table_2 = 'docdb_family_ids'
        
        
        # (1) 
        print('-> Creating a temporary table in the SQL database contaning the patent ids')
        #t = tuple(TABLE_PATENT_IDS[param.VAR_APPLN_ID].unique().tolist())
        t = tuple(list_patent_ids)
        df = pd.DataFrame(t)
        df.columns = [param.VAR_APPLN_ID]
        self.create_temporary_table(df = df,
                       temporary_table_name = temp_SQL_table_1,
                       key = param.VAR_APPLN_ID,
                       engine = eng)
        
        # (2)
        print('-> Retrieving general information about the selected patents')
        TABLE_MAIN_PATENT_INFOS = self.read_sql_tmpfile(param.sql_query_PATENT_MAIN_INFO, eng)
        
        # (3)
        print('-> Retrieving CPC technology classes of the selected patents')
        TABLE_CPC = self.read_sql_tmpfile(param.sql_query_CPC_INFO, eng)
        
        # (4)
        print('-> Retrieving information about the patentees (individuals) of the selected patents')
        TABLE_PATENTEES_INFO = self.read_sql_tmpfile(param.sql_query_PATENTEES_INFO, eng)
        
        # (5)
        print('-> Creating a temporary table in the SQL database containing the docdb_family ids')
        df = TABLE_MAIN_PATENT_INFOS[[param.VAR_DOCDC_FAMILY_ID]]
        df.drop_duplicates(inplace = True)
        self.create_temporary_table(df = df,
                       temporary_table_name = temp_SQL_table_2,
                       key = param.VAR_DOCDC_FAMILY_ID,
                       engine = eng)
        
        
        # (6)
        print('-> Retrieving information about backward citations of the selected families')
        TABLE_DOCBD_backwards_citations = self.read_sql_tmpfile(param.sql_query_DOCBD_backwards_citations, eng)
        
        # (7)
        print('-> Retrieving information about forward citations of the selected families')
        TABLE_FORWARD_CITATIONS = self.read_sql_tmpfile(param.sql_query_FORWARD_CITATIONS, eng)
        
        
        # Regrouping a bit the tables to simplify the output
        TABLE_ALL_PATENTS_INFO = TABLE_MAIN_PATENT_INFOS.append([TABLE_CPC, TABLE_PATENTEES_INFO])
        TABLE_ALL_PATENTS_INFO = pd.merge(TABLE_ALL_PATENTS_INFO,
                                          TABLE_DOCBD_backwards_citations,
                                          how = 'left',
                                          left_on = param.VAR_DOCDC_FAMILY_ID,
                                          right_on = param.VAR_DOCDC_FAMILY_ID)
    
        return TABLE_ALL_PATENTS_INFO, TABLE_FORWARD_CITATIONS
            
            
            
    
    def create_temporary_table(self, df, temporary_table_name, key, engine):
        
        """
        Snippet to create a temporary table in the SQL database
        Inpired from https://stackoverflow.com/questions/30867390/python-pandas-to-sql-how-to-create-a-table-with-a-primary-key
        """
        # Local variables
        eng = self.engine

        with eng.connect() as conn, conn.begin():
            pandas_engine = pandasSQL_builder(conn)

            # creating a table
            table = TemporaryTable(temporary_table_name, pandas_engine, frame=df, if_exists="replace")
            table.create()

            # dumping to the existing table
            df.to_sql(temporary_table_name, conn, index = False, if_exists="replace")

        # Simply add the primary key after uploading the table with pandas.
        with eng.connect() as con:
            con.execute('ALTER TABLE ' + temporary_table_name  + ' ADD PRIMARY KEY ('+key+');')
            
            
            
    def read_sql_tmpfile(self, query, db_engine):
        
        """
        Snippet to speed up large SQL queries by loading them in a temporary file
        """
        
        with tempfile.TemporaryFile() as tmpfile:
            copy_sql = "COPY ({query}) TO STDOUT WITH CSV {head}".format(
               query=query, head="HEADER"
            )
            conn = db_engine.raw_connection()
            cur = conn.cursor()
            cur.copy_expert(copy_sql, tmpfile)
            tmpfile.seek(0)
            df = pd.read_csv(tmpfile, low_memory=False)
            return df
        
        
        
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

        #                                                                FIX HERE v
        return Table(self.name, meta, *columns, schema=schema, prefixes=['TEMPORARY'])