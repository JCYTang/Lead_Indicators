import win32com.client
import os

# Set file path and filename
FilePath1 = os.getcwd() + '\\returns.xlsm'

# Open new instance of Excel
Excel = win32com.client.Dispatch("Excel.Application")

# Open Workbooks
Workbook = Excel.Workbooks.open(FilePath1)
Excel.Run("'returns.xlsm'!update")
Workbook.Close(True)


