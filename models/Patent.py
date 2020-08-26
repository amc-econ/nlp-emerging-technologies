import Parameters as param


class Patent:
    
    
    def __init__(self, appln_id):
        
        # Parameters set when instantiating the patent
        self.patent_attributes = {}
        self.patent_attributes.update({param.VAR_APPLN_ID :  appln_id})
        self.appln_id = appln_id # As a shortcut we  store the main patent key as an attribute
        
        # Parameters determined after fitting the Model
        self.patent_text = ''
        self.smallest_index = () # = static network index corresponding to the earliest_date in which the patent appears 
        self.centrality_over_time = {} # = {(index1, centr1), (index2, centr2), etc.}
        self.betweeness_over_time = {}
        self.community_over_time = {}