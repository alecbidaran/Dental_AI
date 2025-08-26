import firebase_admin
from firebase_admin import credentials
from firebase_admin import db,firestore
import uuid


if not firebase_admin._apps:
    cred = credentials.Certificate("streamlitapp-13c03-firebase-adminsdk-fbsvc-0a346d6d6b.json")
    firebase_admin.initialize_app(cred)
db=firestore.client()   

db_transaction=db.collection('test_transactions')

# db_transaction.set(
#     {
#         'id':str(uuid.uuid4()),
#         'app':'sparkAnime',
#         'transaction-id':'igjepgjagpwogj'
#     }
# )