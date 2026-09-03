import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate(
    "credentials/umiid-2defd-firebase-adminsdk-fbsvc-967526325b.json"
)

firebase_admin.initialize_app(cred)

db = firestore.client()