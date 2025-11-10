#Review: This module provides functions to interact with Firebase Firestore for saving, retrieving, updating, and deleting analysis records. The code is well-structured and includes error handling. I assume this part is still pending of integration in the full application, but it looks good overall. Please ensure to add proper code documentation for the functions. Also, don't forget to provide the credentials file or set up the environment variables as needed.
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os

def init_firebase():
    try:
        if not firebase_admin._apps:
            project_id = os.getenv('FIREBASE_PROJECT_ID', 'milo-4a15b')
            
            if os.path.exists('firebase-service-account.json'):
                cred = credentials.Certificate('firebase-service-account.json')
                firebase_admin.initialize_app(cred, {'projectId': project_id})
            else:
                firebase_admin.initialize_app(options={'projectId': project_id})
        
        return firestore.client()
    except Exception as e:
        print(f"Firebase init failed: {e}")
        return None

db = init_firebase()

def save_analysis(analysis_type: str, filename: str, data: dict, prompt: str = None):
    if not db:
        return {"error": "Firebase not initialized"}
    
    try:
        doc_data = {
            "analysis_type": analysis_type,
            "filename": filename,
            "data": data,
            "prompt": prompt,
            "timestamp": datetime.now().isoformat(),
            "created_at": firestore.SERVER_TIMESTAMP
        }
        doc_ref = db.collection('analyses').add(doc_data)
        return {"id": doc_ref[1].id, "status": "saved"}
    except Exception as e:
        return {"error": str(e)}

def get_analysis(analysis_id: str):
    if not db:
        return {"error": "Firebase not initialized"}
    
    try:
        doc_ref = db.collection('analyses').document(analysis_id)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        else:
            return {"error": "Analysis not found"}
    except Exception as e:
        return {"error": str(e)}

def get_all_analyses():
    if not db:
        return {"analyses": [], "message": "Firebase not configured - running in demo mode"}
    
    try:
        docs = db.collection('analyses').order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        analyses = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            analyses.append(data)
        return {"analyses": analyses}
    except Exception as e:
        return {"analyses": [], "error": str(e)}

def update_analysis(analysis_id: str, update_data: dict):
    if not db:
        return {"error": "Firebase not initialized"}
    
    try:
        doc_ref = db.collection('analyses').document(analysis_id)
        update_data['updated_at'] = firestore.SERVER_TIMESTAMP
        doc_ref.update(update_data)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        else:
            return {"error": "Analysis not found after update"}
    except Exception as e:
        return {"error": str(e)}

def delete_analysis(analysis_id: str):
    if not db:
        return {"error": "Firebase not initialized"}
    
    try:
        doc_ref = db.collection('analyses').document(analysis_id)
        doc = doc_ref.get()
        
        if doc.exists:
            doc_ref.delete()
            return {"status": "deleted", "id": analysis_id}
        else:
            return {"error": "Analysis not found"}
    except Exception as e:
        return {"error": str(e)}

def get_analyses_by_type(analysis_type: str):
    if not db:
        return {"error": "Firebase not initialized"}
    
    try:
        docs = db.collection('analyses').where('analysis_type', '==', analysis_type).order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        analyses = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            analyses.append(data)
        return {"analyses": analyses}
    except Exception as e:
        return {"error": str(e)}
