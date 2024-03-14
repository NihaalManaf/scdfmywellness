from pymongo import MongoClient
from config import *
import pandas
import openpyxl

mongo = MongoClient(Mongodb_url,
                     tls=True,
                     tlsCertificateKeyFile='smw.pem')

db = mongo['SCDFMyWellness']
end_of_course = db["end_of_course"]
def_pass = db["def_pass"]
temp = db["temp"]
user_accounts = db["user_accounts"]

documents = end_of_course.find()

#output all data from document into a excel file
df = pandas.DataFrame(list(end_of_course.find()))
df.to_excel("output.xlsx")
print(df)
print("")