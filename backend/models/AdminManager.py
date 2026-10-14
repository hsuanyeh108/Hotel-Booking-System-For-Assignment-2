class AdminManager:
    def __init__(self): #initialize
        pass

    def create(self, username, password, email, name): #create Admin account
        pass

    def verify_by_username(self, username, password): #Verify the account by username+password
        pass

    def verify_by_email(self, email, password): #Verify the account by email+password
        pass

    def get_by_email(self, email): #Check whether the account already existed by email is duplicate or not when register
        pass

    def get_by_id(self, admin_id): #Check the account by admin id, using when verify API token  
        pass


    