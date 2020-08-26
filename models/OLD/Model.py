# Standard libraries
import pandas as pd
import numpy as np
import networkx as nx
import math

# Custom modules
import Parameters as param
from Patent import *
#from StaticNetworkState import *
#from Community import *
from CustomEngineForPatstat import *



class Model:
    
    
    def __init__(self,
                 custom_engine_for_PATSTAT,
                 technology_classes,
                 start_date,
                 end_date,
                 percentage_top_patents):
        """
        Initialisation of the model:
        # 1. Parameters set when instantiating the model
        # 2. Parameters determined after fitting the model
        # 3. The data retrieved from Patstat is stored in 3 Pandas dataframes
        """
        
        print('----------------------------')
        print('Initialisation of the model.')
        print('----------------------------')
        
        # (1) 
        self.technology_classes = technology_classes
        self.start_date = start_date
        self.end_date = end_date
        self.percentage_top_patents = percentage_top_patents
        self.custom_engine_for_PATSTAT = custom_engine_for_PATSTAT
        
        # (2) 
        self.patent_list = []
        self.patent_ids = []
        self.direct_citations = [] # contain the direct citations (family level)
        self.CC = [] # cocitation
        self.BC = [] # bibliographic coupling
        self.LC = [] # longitudinal coupling
        self.associated_dynamic_graph = nx.DiGraph() # Directed graph
        self.list_network_states = []
        self.list_communities = []
        
        # (3) 
        self.TABLE_PRIMARY_INFO = pd.DataFrame() # df that will contain primary info about the patent after filtering
        self.TABLE_ALL_PATENTS_INFO = pd.DataFrame() # df that will contain all info about the patent
        self.TABLE_FORWARD_CITES = pd.DataFrame() # Special df for forward cites
        
    
    def _fit(self):
        """
        Fitting the model with data retrieved from PATSTAT via the CustomEngine
        """
        print('---------------------------------------')
        print('Fitting the model to the data available')
        print('---------------------------------------')
        
        self._get_PASTAT_primary_data()
        self._select_breakthrough_patents()
        self._get_all_patent_data()
        self._compute_new_variables()
        self._create_patent_objects()
        self._assign_data_to_patent_obj()
        self._compute_direct_patent_citations()
        self._compute_indirect_patent_citations()
        
        # [TO DO] Create network
        # [TO DO] Retrieve patent text data
        # [TO DO] Community tracking over time (iterative algorithm)
    
        print('Model fitted')
        print('---------------------------------------')
        self._print_model_properties()
    
    
    def _get_PASTAT_primary_data(self):
        """
        Method to retrieve data from the PASTAT PosgreSQL database
        # Retriving PATSTAT data with the custom Engine and the query specified in the Parameters module
        """
        
        # Printing info
        print('-> Retriving primary data about the patents linked to the selected technologies')
        
        # Querying the PATSTAT database with the custom engine
        query = self.custom_engine_for_PATSTAT._Run_Engine_step_1(self.technology_classes,
                                                                  self.start_date,
                                                                  self.end_date)
        # Assigning the result table to the model
        self.TABLE_PRIMARY_INFO = query
        
    
    def _compute_new_variables(self):
        """
        Method to compute new useful variables
        # (1) Adding a variable to keep track of yearly citations by patent family
        """
        
        # (1)
        
        # Printing info
        print('-> Computing new variables')
        
        # Unpacking some variables for clarity
        df = self.TABLE_ALL_PATENTS_INFO
        citations_by_year = param.NEW_VAR_NB_CITING_DOCDB_FAM_BY_YEAR
        citations_docdb_fam = param.VAR_NB_CITING_DOCDB_FAM
        year = param.VAR_APPLN_FILLING_YEAR
        ref_year = param.LAST_YEAR_TO_RECEIVE_CITAITONS
        
        # Computing the new variable
        ## Number of patent family citations received by year
        print('-> Adding the number of patent family citations received by year')
        df[citations_by_year] = df[citations_docdb_fam]/(ref_year-df[year]) 
        
        # Updating the table
        self.TABLE_ALL_PATENTS_INFO = df
    
    
    def _select_breakthrough_patents(self):
        """
        In order to select only patent of interest, as well as saving computationnal power, we select only the
        earliest patent by family and the top X% of patents in terms of family citations received. 
        
        To avoid distortions due to the time lag of forward citations as well as changes in citing behaviour
        over time, we select the top patents for each year separately. 
        
        # 1. Selection of the earliest patent for each patent family
        # 2. Selection of the top X% most cited patent (by year)
        
        ## ROBUSTNESS CHECK: We have checked that the number of family citation is the same for all patents
        belonging to the same family.
        ## CAREFUL: because of rounding up, breakthrough patents in low patenting years will be overrepresented
        in proportion (10% of 1 patents round up = 1 patent selected)
        """
        # Printing info
        print('=> Number of patents linked to selected technologies:',
              len(self.TABLE_PRIMARY_INFO[param.VAR_APPLN_ID].unique().tolist()))
        print('-> Selection of the earliest patent for each patent family')
        print('-> Selection of the top X% most cited patent (by year)')
        
        # Unpacking some variables
        X = self.percentage_top_patents
        df = self.TABLE_PRIMARY_INFO
        
        # (1)
        # Sorting the table by earliest filling date
        df.sort_values(by = param.VAR_EARLIEST_FILLING_DATE, inplace = True)
        # Keeping only the oldest patent by family
        df.drop_duplicates(subset = [param.VAR_DOCDC_FAMILY_ID], keep = 'first', inplace = True)
        
        # (2)
        filtered_df = pd.DataFrame()
        for year in df[param.VAR_EARLIEST_FILING_YEAR].unique().tolist():
            df_year = df[df[param.VAR_EARLIEST_FILING_YEAR] == year]
            df_year.sort_values(by = param.VAR_NB_CITING_DOCDB_FAM, ascending = False, inplace = True)
            nb_top_patent_given_year = int(math.ceil(X*len(df_year))) # Needs rounding up
            df_year = df_year.head(nb_top_patent_given_year)
            filtered_df = pd.concat([filtered_df, df_year])
            
        # Update the table and the list of patent ids
        self.TABLE_PRIMARY_INFO = filtered_df
        self.patent_ids = self.TABLE_PRIMARY_INFO[param.VAR_APPLN_ID].unique().tolist()
        
        # Print info
        print('=> Number of breakthrough patents selected:', len(self.patent_ids))
            
        
    def _get_all_patent_data(self):
        """
        Once the primary selection of breakthrough data has been done, we retrieve more 
        information about these patents.
        """
    
        print('-> Retrieving PATSTAT data using the CustomEngineForPatstat')
        a, b = self.custom_engine_for_PATSTAT._Run_Engine_step_2(list_patent_ids = self.patent_ids, 
                                                                 technology_classes_list = self.technology_classes,
                                                                 start_date = self.start_date,
                                                                 end_date = self.end_date) # random table names
        
        print('-> Removing duplicated columns (if any)')  
        
        def snippet_remove_duplicated_cols(df):
            df = df.loc[:,~df.columns.duplicated()]
            cols = [x for x in list(df) if '.' not in x]
            df = df[cols]
            return df
            
        a = snippet_remove_duplicated_cols(a)
        #b = snippet_remove_duplicated_cols(b)

        # Update the tables
        self.TABLE_ALL_PATENTS_INFO = a
        self.TABLE_FORWARD_CITES = b
            
    
    def _data_cleaning(self):
        pass
    
    
    def _compute_direct_patent_citations(self):
        """
        Computing direct backwards citations (at the level of the family level)
        """
        
        print('-> Computing direct citations (at the family level)')
            
        # (1) If a patent cites only one family
        list1 = [(x,y) for x in self.patent_list for y in self.patent_list if y.patent_attributes[param.VAR_DOCDC_FAMILY_ID] == x.patent_attributes[param.VAR_CITED_DOCDB_FAM_ID]]
        # (2) If the patent cites several families (then stored as list)
        list2 = [(x,y) for x in self.patent_list for y in self.patent_list if type(x.patent_attributes[param.VAR_CITED_DOCDB_FAM_ID]) ==list if y.patent_attributes[param.VAR_DOCDC_FAMILY_ID] in x.patent_attributes[param.VAR_CITED_DOCDB_FAM_ID]]
        
        # Concatenating the two lists to have the direct citations
        self.direct_citations = list1 + list2
            
    
    def _compute_indirect_patent_citations(self):
        """
        Computing indirect backwards citations (at the level of the family level)
        # 1. CC (co-citations)
        # 2. BC (bibliographic coupling) 
        # 3. LC (longitudinal coupling)
        """
        
        def _compute_cc(patent_list):
            """
            # (1) Co-citation is defined as the frequency with which two documents are cited together
            by other documents. If at least one other document cites two documents in common these documents
            are said to be co-cited.
            # The produced list is non directed.
            
            ## Too slow...
            """
            print('-> Computing co-citations (cc)')
            
            # Definiton of variables
            CC = []
            
            a = patent_list
            all_patent_pairs = [(a[p1], a[p2]) for p1 in range(len(a)) for p2 in range(p1+1,len(a))]
            
            # Definition of the search algorithm
            for patent in patent_list:
                a = patent.patent_attributes[param.VAR_CITED_DOCDB_FAM_ID]
                if type(a)==list:
                    if len(a)>1:
                        all_cited_patent_pairs = [(a[p1], a[p2]) for p1 in range(len(a)) for p2 in range(p1+1,len(a))]
                        for pair in all_cited_patent_pairs:
                            CC.append(pair)
                        
                        # Computing CC by looping over all pairs of patents
                        #for patent_1, patent_2 in all_patent_pairs:
                        #    if (patent_1.patent_attributes[param.VAR_DOCDC_FAMILY_ID],
                        #        patent_2.patent_attributes[param.VAR_DOCDC_FAMILY_ID]) in all_cited_patent_pairs:
                         #       CC.append((patent_1, patent_2))
                    
            
            
                            
            
                            
            #CC2 = []
            #for pair in CC:
            #    patent1 = [patent for patent in self.patent_list if patent.patent_attributes[param.VAR_DOCDC_FAMILY_ID] == pair[0]]
             #   patent2 = [patent for patent in self.patent_list if patent.patent_attributes[param.VAR_DOCDC_FAMILY_ID] == pair[1]]
              #  if len(patent1)>0:
              #      patent1 = patent1[0]
              #  else: patent1=np.nan

               # if len(patent2)>0:
                #    patent2 = patent2[0]
                #else: patent2=np.nan
                #pair = (patent1, patent2)
                #CC2.append(pair)

                #CC = [pair for pair in CC2 if (pair[0]==pair[0]) & (pair[1] == pair[1])]
                            
                
            # Removing duplicated items in the list
            pairs = list(set(CC)) 
            
            CC = []
            for pair in pairs:
                patent1 = [patent for patent in self.patent_list if patent.patent_attributes[param.VAR_DOCDC_FAMILY_ID] == pair[0]]
                patent2 = [patent for patent in self.patent_list if patent.patent_attributes[param.VAR_DOCDC_FAMILY_ID] == pair[1]]

                if len(patent1)>0:
                    patent1 = patent1[0]
                else: patent1=np.nan

                if len(patent2)>0:
                    patent2 = patent2[0]
                else: patent2=np.nan

                pair = (patent1, patent2)
                CC.append(pair)

                CC = [pair for pair in CC if (pair[0]==pair[0]) & (pair[1] == pair[1])]
                    
            return CC
        
        
        def _compute_bc(patent_list):
            """
            # (2) Bibliographic coupling occurs when two works reference a common third work in their bibliographies
            # The produced list is non directed.
            
            # Can be optimised
            """
            print('-> Computing bibliographic coupling (bc)')
            
            # Definition of variables
            BC = []
            a = patent_list
            all_patent_pairs = [(a[p1], a[p2]) for p1 in range(len(a)) for p2 in range(p1+1,len(a))]

            # Computing BC by looping over all pairs of patents
            for patent_1, patent_2 in all_patent_pairs:
                list_citing_1 = patent_1.patent_attributes[param.NEW_VAR_CITING_DOCDB_FAM_IDS]
                list_citing_2 = patent_2.patent_attributes[param.NEW_VAR_CITING_DOCDB_FAM_IDS]
                common_elements = [x for x in list_citing_1 if x in list_citing_2]
                if len(common_elements)>0:
                    BC.append((patent_1, patent_2))
            
            # Removing duplicated items in the list
            BC = list(set(BC)) 
            return BC
        
        
        def _compute_lc(patent_list):
            """
            # (3) LC (longitudinal coupling). A cites a document that cites B.
            # The produced list IS directed.
            
            # Can be optimised
            """
            print('-> Computing longitudinal coupling (lc)')
            
            LC = []
            
            # Identifying all patents cited by a given patent A
            for patent_A in patent_list:
                cited_fam = patent_A.patent_attributes[param.VAR_CITED_DOCDB_FAM_ID]
                if type(cited_fam)==float:
                        cited_fam = []
                        cited_fam.append(patent_A.patent_attributes[param.VAR_CITED_DOCDB_FAM_ID])
                cited_patents = [patent for patent in patent_list if \
                                 patent.patent_attributes[param.VAR_DOCDC_FAMILY_ID] in cited_fam]
                
                # Identifying all patents cited by a patent cited by patent A
                for cited_patent in cited_patents:
                    cited_fam = cited_patent.patent_attributes[param.VAR_CITED_DOCDB_FAM_ID]
                    if type(cited_fam)==float:
                        cited_fam = []
                        cited_fam.append(cited_patent.patent_attributes[param.VAR_CITED_DOCDB_FAM_ID])
                    cited_cited_patents = [patent for patent in patent_list if \
                                 patent.patent_attributes[param.VAR_DOCDC_FAMILY_ID] in cited_fam]
                    
                    # Adding the pairs in the LC list
                    for patent_B in cited_cited_patents:
                        LC.append((patent_A, patent_B))
                    
            # Removing duplicated items in the LC list
            LC = list(set(LC)) 
            return LC
                
        # Computing the measures defined
        self.CC = _compute_cc(patent_list = self.patent_list)
        self.BC = _compute_bc(patent_list = self.patent_list)
        self.LC = _compute_lc(patent_list = self.patent_list)
    
    
    def filter_patent_list(self):
        pass
    
    
    def _create_patent_objects(self):
        """
        Create a Patent object for each patent id and store them in a list
        """
        print('Creation of the patent Python objects')
        self.patent_list = []
        for patent_id in list(self.patent_ids):
            a = Patent(patent_id) # updated
            self.patent_list.append(a) # updated
            
            
    def _assign_data_to_patent_obj(self):
        """
        Once the data has been retrieved from PATSTAT and the patent objects have been created,
        we assign the data to the Patent objects
        """
        
        # Unpacking some variables
        df_all = self.TABLE_ALL_PATENTS_INFO
        df_fwd = self.TABLE_FORWARD_CITES
        
        # (1) Assigning the data contained in the main table to the patent
        print('Giving the attributes to the patents')
        i = 1
        j = 1
        for patent in self.patent_list:
            nb = round(i/len(self.patent_list)*100,2)
            if j%1000==0:
                print('...',nb,"%")
            patent_table = df_all[df_all[param.VAR_APPLN_ID]==patent.appln_id]
            d = self.snippet_store_patent_attributes(table = patent_table)
            patent.patent_attributes.update(d)
            i+=1
            j+=1
        
        # (2) Assigning forward citations to the patents
        print('Assigning forward citations to the patents')
        df_fwd.columns = ['A','B','C'] # Random column names
        i = 1
        j = 1
        for patent in self.patent_list:
            nb = round(i/len(self.patent_list)*100,2)
            if j%1000==0:
                print('...',nb,"%")
            patent_fam_table = df_fwd[df_fwd['A']==patent.patent_attributes[param.VAR_DOCDC_FAMILY_ID]]
            citing_fam = patent_fam_table['B'].unique().tolist()
            patent.patent_attributes.update({param.NEW_VAR_CITING_DOCDB_FAM_IDS :citing_fam})
            i+=1
            j+=1
            
    
    def snippet_store_patent_attributes(self, table):
        """
        Code snippet to dynamically store attributes 
        from a Pandas table in a dictionnary
        # If a value has several values, then ts stored in a list
        """
        a = {}
        for col in list(table):
            key = col
            value = table[col].unique().tolist()#[0]
            value = [x for x in value if (x == x)!=False]  # new line
            if len(value) == 1:
                value = value[0]
            a[key] = value
        return a
    
    
    def _get_EP_full_text_data(self):
        pass
    
    
    def _text_data_processing(self):
        pass
    
    
    def _compute_LSA(self):
        pass
    
    
    def _compute_similiary_measure(self):
        pass
    
    
    def _create_network(self):
        pass
    
    
    def _create_static_network_over_time(self):
        pass
    
    
    def _detect_communities_static_network(self):
        pass
    
    
    def _trace_communities_dynamic_network(self):
        pass
    
    
    def _print_model_properties(self):
        """
        Displays the main properties of the model
        """
        print('Technological classes: ', self.technology_classes)
        print('Number of patents in the model: ', len(self.patent_ids))
        print('Threshold to select top patent:', self.percentage_top_patents*100,'%')
        print('Start date: ', self.start_date)
        print('End date: ', self.end_date)
        print('---------------------------------------')
        