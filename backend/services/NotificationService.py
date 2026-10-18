#Services - Notification Center sending Logic(Sarah)
#Only using Singleton Pattern(Setting are managed in NotificationContract)
#This file is simply decide whether to print the email/log message out, without Adapter wrapping to be simple
#This file has no real email/SMS sending logic, only for demostration
#Same as the course Measuable Success Criteria requirements: "email/SMS sending...only for demonstration"
#Use print() to simulate, and store each record in notification log list to test and verify

from datetime import datetime, timezone #import datatime, timezone in Python
from backend.config import db
from backend.services.NoficationContract import NotificationContract
#import NotificationContract Singleton setting category, for this category to read

notifications_collection = db["notifications"] 
#Simulate the notification record write into notification log database
#store the record in this database to check whether the notice has been sent and what it sent

class NotificationService:
    def __init__(self): #initialize
        self._config = NotificationContract() 
        #Because Singleton, get the only setting in whole system, store in self._config, every NotificationService seen the same setting

    def _send_email(self, booking, message): #Simulate sending email notification (internal use)
        entry = {
            "channel": "email", #Channel name is email
            "to": booking.get("guest_email"), #Receiver email address, get the order's guest email
            "subject": f"Booking BK-{booking.get('booking_no')}Update", #email subject, f-string will fill the booking_no into it
            "body": message, #email body
            "created_at": datetime.now(timezone.utc), #email sent time
        }
        notifications_collection.insert_one(dict(entry))
        print(f"[EMAIL] to={entry['to']}subject={entry['subject']}")
        return entry
        #Three parameters: email, to ,subject entry to the notification_log list
        #print to terminal, and return this record

    def _send_log(self, booking, message): #Simulate the notification record write into notification log list(internal use)
        entry = {
            "channel": "log", 
            "message": f"Booking BK-{booking.get('booking_no')}: {message}", 
            "created_at": datetime.now(timezone.utc),}
        #log channel, only need message
        notifications_collection.insert_one(dict(entry))
        print(f"[LOG] {entry['message']}")
        return entry
        #Two parameters: log, message entry to the notification_log list
        #print to terminal, and return this record

    #The only entry from external: According to Singleton's setting, decide using email or log channel to send 
    def status_change(self, booking: dict, new_status: str): #Notify when the status change, booking: dict, new_status: str is the reminder of category
        message = f"Your booking status changed to '{new_status}'."
        sent_via = [] #generate message, setting an empty list to record using what via
                                          
        if self._config.get_setting("email_enabled"):
            self._send_email(booking, message)
            sent_via.append("email") #If email is open, then send via email and record as email

        if self._config.get_setting("log_enabled"):
            self._send_log(booking, message)
            sent_via.append("log") #If log is open, then send via log and record as log

        return {
            "booking_no": booking.get("booking_no"),
            "new_status": new_status,
            "sent_via": sent_via,
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }
        #Return the order summary(booking_no, new_status, sent_via, sent_datetime)
        #isoformat() to format the datetime to string
        #This class always decide from Singleton current setting, So when admin click the save button, the setting will be updated

#Add a function for read recent notifications
def get_recent_notifications(limit=10):
    return list(notifications_collection.find().sort("created_at", -1).limit(limit))