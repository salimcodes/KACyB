import mindsdb_sdk
import pandas as pd

# Connecting to MindsDB
server = mindsdb_sdk.connect('https://cloud.mindsdb.com', login='salimonyinlola@outlook.com', password='Qwerty12345')
project = server.get_project("mindsdb")
model = project.list_models()[0] #Selecting the model to use. The index 0 is used because this is the first model in the list of models on the account

text = input("Enter a text: ")
if model.predict(text)["oh_label"].loc[0] == 1:
    print("Yes, this is cyberbullying") 
else:
    print("No, this is not cyberbullying")