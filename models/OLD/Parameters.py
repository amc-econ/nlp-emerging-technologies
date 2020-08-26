"""Parameters of the model"""



# Magic numbers
LAST_YEAR_TO_RECEIVE_CITAITONS = 2018

# PASTAT_variables 
VAR_APPLN_ID = 'appln_id'
VAR_DOCDC_FAMILY_ID = 'docdb_family_id'
VAR_CITED_DOCDB_FAM_ID = 'cited_docdb_family_id'
VAR_APPLN_FILLING_YEAR = 'appln_filing_year'
VAR_NB_CITING_DOCDB_FAM = 'nb_citing_docdb_fam'
VAR_EARLIEST_FILLING_DATE = 'earliest_filing_date'
VAR_EARLIEST_FILING_YEAR = 'earliest_filing_year'

# Computed variables
NEW_VAR_CITING_DOCDB_FAM_IDS = 'citing_docdb_families_ids'
NEW_VAR_NB_CITING_DOCDB_FAM_BY_YEAR = 'nb_citing_docdb_fam_by_year'

# Queries - Custom_Engine_For_PATSAT

sql_query_PATENT_IDS = """
            SELECT tls201_appln.appln_id, cpc_class_symbol
            FROM tls201_appln JOIN tls224_appln_cpc ON tls201_appln.appln_id = tls224_appln_cpc.appln_id
            WHERE cpc_class_symbol like '{}%%'
            AND appln_filing_year between {} and {}
            ORDER BY tls201_appln.appln_id
            """#.format(technology_class, start_date, end_date) to add in the code


sql_query_PATENT_PRIMARY_INFO = """
            SELECT tls201_appln.appln_id, tls201_appln.DOCDB_FAMILY_ID,tls201_appln.EARLIEST_FILING_DATE, tls201_appln.EARLIEST_FILING_YEAR, tls201_appln.NB_CITING_DOCDB_FAM, cpc_class_symbol
            FROM tls201_appln JOIN tls224_appln_cpc ON tls201_appln.appln_id = tls224_appln_cpc.appln_id
            WHERE cpc_class_symbol like '{}%%'
            AND appln_filing_year between {} and {}
            ORDER BY tls201_appln.appln_id
            """


sql_query_PATENT_MAIN_INFO = """
            SELECT * 
            FROM temporary_table_patent_ids
            LEFT JOIN tls201_appln ON temporary_table_patent_ids.appln_id = tls201_appln.appln_id
            LEFT JOIN TLS202_APPLN_TITLE ON temporary_table_patent_ids.appln_id = TLS202_APPLN_TITLE.appln_id
            LEFT JOIN TLS203_APPLN_ABSTR ON temporary_table_patent_ids.appln_id = TLS203_APPLN_ABSTR.appln_id
            LEFT JOIN TLS209_APPLN_IPC ON temporary_table_patent_ids.appln_id = TLS209_APPLN_IPC.appln_id
            LEFT JOIN TLS229_APPLN_NACE2 ON temporary_table_patent_ids.appln_id = TLS229_APPLN_NACE2.appln_id
            """


sql_query_CPC_INFO = """
            SELECT * 
            FROM temporary_table_patent_ids
            LEFT JOIN TLS224_APPLN_CPC ON temporary_table_patent_ids.appln_id = TLS224_APPLN_CPC.appln_id 
            """


sql_query_PATENTEES_INFO = """
            SELECT * 
            FROM temporary_table_patent_ids
            LEFT JOIN TLS207_PERS_APPLN ON temporary_table_patent_ids.appln_id = TLS207_PERS_APPLN.appln_id
            LEFT JOIN TLS206_PERSON ON TLS207_PERS_APPLN.PERSON_ID = TLS206_PERSON.PERSON_ID
            LEFT JOIN TLS226_PERSON_ORIG ON TLS206_PERSON.PERSON_ID = TLS226_PERSON_ORIG.PERSON_ID
            --LEFT JOIN TLS228_DOCDB_FAM_CITN ON tls201_appln.DOCDB_FAMILY_ID = TLS228_DOCDB_FAM_CITN.DOCDB_FAMILY_ID
            """


sql_query_DOCBD_backwards_citations = """
            SELECT * 
            FROM docdb_family_ids
            LEFT JOIN TLS228_DOCDB_FAM_CITN ON docdb_family_ids.docdb_family_id = TLS228_DOCDB_FAM_CITN.docdb_family_id
            """


sql_query_FORWARD_CITATIONS = """
            SELECT docdb_family_ids.DOCDB_FAMILY_ID, TLS228_DOCDB_FAM_CITN.DOCDB_FAMILY_ID,
            TLS228_DOCDB_FAM_CITN.CITED_DOCDB_FAMILY_ID
            FROM docdb_family_ids JOIN TLS228_DOCDB_FAM_CITN 
            ON docdb_family_ids.DOCDB_FAMILY_ID = TLS228_DOCDB_FAM_CITN.CITED_DOCDB_FAMILY_ID
            """