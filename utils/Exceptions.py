class Abort(Exception):
    """ a signal to abort current action due to user's choice """
    pass

# class BadInput(Exception):
#     """ catches bad input """
#
#     def __init__(self, message):
#         self.message = message
#         super().__init__(self.message)