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

    _instance = None #store the only object, category variables, _ means not access from outside, None in start means have not setting yet

    #Singleton will decide whether create a new one or return the existing one
    def __new__(cls, *args, **kwargs): #_new_is the method of creating object in Python, will operate earlier than _init_, *args, **kwargs means accept any arguments
        if cls._instance is None:      #Check whether have set it or not, only the first time will run this line
           instance = super().__new__(cls) #call the parent class(object _new_)generate a real new object                       
           instance._settings = { #put the default setting(email, log, sender email) in here
               "email_enabled": True,
               "log_enabled": True,
               "sender_email": "no-reply@hotel-booking.com",
           }
           cls._instance = instance #store the object in category variable, can reuse
        return cls._instance #return the only object, the second time if will not run, and jump directly to this line
    
    def get_setting(self, key, default=None): #To read the setting, such as email_enabled
        return self._settings.get(key, default) #default=None means if the key can not find, will not seem as error, return None
    
    def set_setting(self, key, value): #To write the setting by value
        self._settings[key] = value #ex: email_enabled=True, will turn off the email notification, same object whole system effect immediate

    def dict(self): #To change the whole setting to dict, for display the page to use
        return dict(self._settings) #Return a copy, to avoid direct change the internal dict, which is the point of encapsulation

    @classmethod #First build object is parameter cls, no need to build object then can call
    def reset_testing(cls): #To reset the setting to default, only for testing, avoid pollute between testing
        cls._instance = None  #Instance reset to None, only for pytest use, to clear the Singleton, each test case is a new instance
    
        