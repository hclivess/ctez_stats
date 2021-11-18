import json

with open("database.json", "r") as database_in:
    database = json.loads(database_in.read())
    
database["stats"]["last_block"] = 1793972

with open("database.json", "w") as database_out:
    database_out.write(json.dumps(database))

print("Rescan reset request saved to the database")