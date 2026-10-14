#Services - Notification Center sending Logic(Sarah)
#Only using Singleton Pattern(Setting are managed in NotificationContract)
#This file is simply decide whether to print the email/log message out, without Adapter wrapping to be simple
#This file has no real email/SMS sending logic, only for demostration
#Same as the course Measuable Success Criteria requirements: "email/SMS sending...only for demonstration"
#Use print() to simulate, and store each record in notification log list to test and verify

class NotificationService:
    def __init__(self): #initialize
        pass

    def _send_email(self, booking, status): #Simulate sending email notification (internal use)
        pass

    def _send_log(self, booking, status): #Simulate the notification record write into notification log list(internal use)
        pass

    def status_change(self, booking, status): #Notify when the status change
        pass                                  #The only entry from external: According to Singleton's setting, decide using email or log channel to send 
    
    