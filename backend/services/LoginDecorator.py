#To protect the Admin web routes: check whether session has login records

class LoginDecorator:
    def __init__(self): #initialize
        pass

    def __call__(self, *args, **kwds): #Check whether session has login, if no then direct to login page, if yes then pass the original view
        pass
        