import sys
import traceback

class DocumentQueryingPortalException(Exception):
    """
    Custom Exception for Document querying portal
    """
    def __init__(self, err_msg:str, err_details:sys):
        _,_,exc_information = err_details.exc_info()
        self.file_name = exc_information.tb_frame.f_code.co_filename
        self.line_no = exc_information.tb_lineno
        self.error_message = err_msg
        self.traceback_str = ''.join(traceback.format_exception(*err_details.exc_info()))

    def __str__(self):
       return f""" Error Occrued in {self.file_name} at line [{self.line_no}] Message: {self.error_message}, traceback: {self.traceback_str}"""

# if __name__ == "__main__":
#     try:
#         a  = 1/0
#         print(a)
#     except Exception as e:
#         raise DocumentQueryingPortalException(e, sys) 