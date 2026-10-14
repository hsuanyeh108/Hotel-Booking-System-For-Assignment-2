from werkzeug.security import generate_password_hash, check_password_hash
#generate_password_hash: let the password become irreversible hash code
#check_password_hash: To verify the password
from config import db


class AdminManager:
    def __init__(self, db): #initialize
        self._admins = db["admins"] #put all data in "admins" object, the line in front of the name("_admins") is an encapsulation mechanism for internal use

    def create(self, username, password, email=None, name=None): #create Admin account, email and name are optional
        hashed_password = generate_password_hash(password) #The original password is converted to hash password
        admin_dictionary = {    #Create an admin dictionary to store the data
            "username": username,
            "password": hashed_password,
            "email": email,
            "name": name,
        }
        result = self._admins.insert_one(admin_dictionary) #Insert the data in admin dictionary to the MongoDB database
        return str(result.inserted_id) #Return the id number that MongoDB has generated, and convert it to string

    def verify_by_username(self, username, password): #Verify the account by username+password
        admin = self._admins.find_one({"username": username}) #Find the account that conform to the MongoDB data by username
        if admin and check_password_hash(admin["password"], password): #If the account exists and the password is correct, return True
            return admin #Return the complete account data
        return None #Otherwise, return None(failed)

    def verify_by_email(self, email, password): #Verify the account by email+password
        admin = self._admins.find_one({"email": email}) #Find the account that conform to the MongoDB data by email
        if admin and check_password_hash(admin["password"], password): #If the account exists and the password is correct, return True
            return admin #Return the complete account data
        return None #Otherwise, return None(failed)

    def get_by_email(self, email): #Check whether the account already existed by email is duplicate or not when register
        return self._admins.find_one({"email": email}) #Find the account that conform to the MongoDB data, and return the query result

    def get_by_id(self, admin_id): #Check the account by admin id, according to id to get data, using when verify API token  
        objectId = to_object_id(admin_id) #Convert admin id to MongoDB object id, and store it in objectId
        if objectId is None: #If the id is None, reprsent the ObjectId is invalid
            return None 
        return self._admins.find_one({"_id": objectId}) #Find the account that conform to the MongoDB _id data by objectId, and return the query result
    
#Build object for the whole system share(no need to rebuild the object every time)
admin_manager = AdminManager(db)


    
