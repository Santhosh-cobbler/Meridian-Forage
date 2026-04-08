class DataBase:
    def __init__(self):
        pass

    def Master(self):
        self.Total_Database = {
            'Proj_id' : [],
            'proj_name':[],
            'description': [],
            'Type':[],
            'Status':[],
            'TOT_Module' :[],
            'Module_status':[]
        }

    def Module(self):
        self.Module_DataBASE = {
            'proj_id':[],
            'Module_id':[],
            'name':[],
            'description':[],
            'status':[]
        }