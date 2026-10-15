#To protect the Admin web routes: check whether session has login records
#Session Authentication Decorator
#Design Pattern: Decorator Pattern, add a Layer of Protection to the original function, like the checker(To not change the original function situation)
#Using Class (LoginDecorator and TokenDecorator), store to view function(_call_), for this object to call

import functools 
#Let decorator keep the original Flask view function name, document and information

from flask import session, flash, redirect, url_for
#import flask tools, session for each user information, flask will use SECRET_KEY signature to store in browser cookie
#flash for message, will show on the next page
#redirect reponse browser to another page
#url_for use route name to check the link

class LoginDecorator:#Protect web routes that require an active login session
    def __init__(self, view_func): #initialize
        self.view_func = view_func
        functools.update_wrapper(self, view_func)
    #Save the route in view_func
    #update_wrapper copy the view_func name, document, information
    #If no copy, flask will use the route name to be the endpoint, all protect pages will be same name, and flask will show endpoint duplicate error

    #_call_let object be call, every time anyone get in this page will be here
    #*args, **kwds are the parameters copy for the original function
    def __call__(self, *args, **kwds): #Check whether session has login, if no then direct to login page, if yes then pass the original view
        if not session.get("admin_logged_in"):
            flash("Please log in first.", "error")
            return redirect(url_for("admin.login"))
        #check session admin login status, use get(), if no return None
        #So did not login before or log out will get in if statement
        #store a message in flash, please log in first and category is error
        #Redirect to login page, find the login route in admin blueprint

        return self.view_func(*args, **kwds)
        #All pass, then real run the route
        