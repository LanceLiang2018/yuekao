import pymongo


client = pymongo.MongoClient("mongodb+srv://lanceliang:1352040930database@lanceliang-9kkx3.azure.mongodb.net/"
                             "test?retryWrites=true&w=majority")
db = client.sample_mflix
col = db.movies

print(db.list_collection_names(session=None))
print(client.list_database_names())
for x in col.find():
    print(x)