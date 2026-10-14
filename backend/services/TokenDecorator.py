#To protect the Admin API routes: Check Authorization(Bearer) token

class TokenDecorator:
    def __init__(self): #initialize
        pass

    def __call__(self, *args, **kwds): #To check and decrypt Authorization JWT, if verify success save admin in request.current_admin
        pass