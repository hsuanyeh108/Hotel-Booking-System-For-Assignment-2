#Services - Notification Center Setting Management(Sarah)
#Design Pattern: Using Singleton Pattern
#Notification setting(email, log) should only be one in the whole app(unless the manage page, API or order situation change will send the notice, they should read the same file)
#Whole Flask app will call NotificationContract() serveral times, only get one instance(same object, same settings), will not read the default value every time

#OOP Principle: Encapsulation
#_settings is private abtribute, are not accessible from outside
#Only accessible through get_setting(), set_setting(), dict() returns copy, to avoid direct change the situation of internal
#need to add the validation rule, ex: email format authorization, only change this class, will not affect the caller

#Advance: save resource, only one connection, the whole system only one situation, will not happen some link to A, some link to B
#Disadvantage: Whole system let the testing become more complex, Python are not a strictly Singleton, but reserve the flexibility

#Whole system only have one instance, all the functions related to notification will use the same settings
class NotificationContract:
    def __init__(self): #initialize
        pass

    def get_setting(self, key): #To read the setting, such as email_enabled
        pass

    def set_setting(self, key, value): #To write the setting by value
        pass

    def dict(self): #To change the whole setting to dict, for display the page to use
        pass        #Return a copy, to avoid direct change the internal dict, which is the point of encapsulation

    def reset_testing(self): #To reset the setting to default, only for testing, avoid pollute between testing
        pass                 #Instance reset to None, only for pytest use, to clear the Singleton, each test case is a new instance
    
        