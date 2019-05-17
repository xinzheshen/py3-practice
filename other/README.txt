env: python3
dependency: xlrd   (execute 'pip install xlrd' to install xlrd)
usage:
    python xls2xml.py -i ./Audio_App_properties_Details.xlsx -o ./output -s 1 -v 1.0.0.0
    -i : The path of input xls file.
    -s : The index of sheet to process in xls file (start from 0), default is 1.
    -o : The path of output folder.
    -v : The build version of CSM.