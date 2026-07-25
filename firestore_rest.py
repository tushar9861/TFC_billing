import requests
import json
import threading
import time

API_KEY = "AIzaSyCu9Vx5hJ59tHYys8Zu1CZ3H120JBiTAuQ"
PROJECT_ID = "tiwarisfriedchicken"

class FirestoreClient:
    def __init__(self, api_key=API_KEY, project_id=PROJECT_ID):
        self.api_key = api_key
        self.project_id = project_id
        self.id_token = None
        self.refresh_token = None
        self.base_url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents"
        self.auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.api_key}"
        self.signup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}"
        self.refresh_url = f"https://securetoken.googleapis.com/v1/token?key={self.api_key}"

    def signup(self, email, password):
        payload = {"email": email, "password": password, "returnSecureToken": True}
        r = requests.post(self.signup_url, json=payload)
        r.raise_for_status()
        data = r.json()
        self.id_token = data['idToken']
        self.refresh_token = data['refreshToken']
        return data

    def login(self, email, password):
        payload = {"email": email, "password": password, "returnSecureToken": True}
        r = requests.post(self.auth_url, json=payload)
        r.raise_for_status()
        data = r.json()
        self.id_token = data['idToken']
        self.refresh_token = data['refreshToken']
        return data

    def refresh_auth(self):
        if not self.refresh_token: return False
        payload = {"grant_type": "refresh_token", "refresh_token": self.refresh_token}
        r = requests.post(self.refresh_url, data=payload)
        if r.status_code == 200:
            self.id_token = r.json()['id_token']
            return True
        return False

    def _auth_header(self):
        if not self.id_token:
            return {}
        return {"Authorization": f"Bearer {self.id_token}"}

    def _to_firestore_type(self, value):
        if isinstance(value, bool): return {"booleanValue": value}
        if isinstance(value, int): return {"integerValue": str(value)}
        if isinstance(value, float): return {"doubleValue": value}
        if isinstance(value, str): return {"stringValue": value}
        if value is None: return {"nullValue": None}
        if isinstance(value, list): return {"arrayValue": {"values": [self._to_firestore_type(v) for v in value]}}
        if isinstance(value, dict):
            return {"mapValue": {"fields": {k: self._to_firestore_type(v) for k, v in value.items()}}}
        return {"stringValue": str(value)}

    def _from_firestore_type(self, value_dict):
        if not value_dict: return None
        key = list(value_dict.keys())[0]
        val = value_dict[key]
        if key == "booleanValue": return val
        if key == "integerValue": return int(val)
        if key == "doubleValue": return float(val)
        if key == "stringValue": return val
        if key == "nullValue": return None
        if key == "arrayValue": return [self._from_firestore_type(v) for v in val.get("values", [])]
        if key == "mapValue": return {k: self._from_firestore_type(v) for k, v in val.get("fields", {}).items()}
        return val

    def dict_to_document(self, data):
        return {"fields": {k: self._to_firestore_type(v) for k, v in data.items()}}

    def document_to_dict(self, doc):
        if 'fields' not in doc: return {}
        return {k: self._from_firestore_type(v) for k, v in doc['fields'].items()}

    def list_documents(self, path):
        """List all documents in a collection path."""
        r = requests.get(f"{self.base_url}/{path}", headers=self._auth_header())
        if r.status_code == 401:
            if self.refresh_auth():
                r = requests.get(f"{self.base_url}/{path}", headers=self._auth_header())
        if r.status_code in (404, 400):
            return []
        r.raise_for_status()
        res = r.json()
        docs = res.get('documents', [])
        results = []
        for doc in docs:
            data = self.document_to_dict(doc)
            data['id'] = doc['name'].split('/')[-1]
            results.append(data)
        return results

    def update_document(self, path, data):
        """Partial update (merge) of a document."""
        return self.set_document(path, data)

    def get_document(self, path):
        r = requests.get(f"{self.base_url}/{path}", headers=self._auth_header())
        if r.status_code == 401:
            if self.refresh_auth():
                r = requests.get(f"{self.base_url}/{path}", headers=self._auth_header())
        if r.status_code == 404: return None
        r.raise_for_status()
        doc = r.json()
        data = self.document_to_dict(doc)
        data['id'] = doc['name'].split('/')[-1]
        return data

    def set_document(self, path, data):
        doc_data = self.dict_to_document(data)
        # Using PATCH to act like SET (upsert)
        url = f"{self.base_url}/{path}"
        r = requests.patch(url, headers=self._auth_header(), json=doc_data)
        if r.status_code == 401:
            if self.refresh_auth():
                r = requests.patch(url, headers=self._auth_header(), json=doc_data)
        r.raise_for_status()
        return r.json()

    def delete_document(self, path):
        r = requests.delete(f"{self.base_url}/{path}", headers=self._auth_header())
        if r.status_code == 401:
            if self.refresh_auth():
                r = requests.delete(f"{self.base_url}/{path}", headers=self._auth_header())
        r.raise_for_status()
        return r.json()

    def run_query(self, collection_path, field, operator, value):
        # A simple structured query for equality
        # operator can be EQUAL, LESS_THAN, etc.
        query = {
            "structuredQuery": {
                "from": [{"collectionId": collection_path.split('/')[-1]}],
                "where": {
                    "fieldFilter": {
                        "field": {"fieldPath": field},
                        "op": operator,
                        "value": self._to_firestore_type(value)
                    }
                }
            }
        }
        
        # The path for runQuery is the parent of the collection
        parent_path = '/'.join(collection_path.split('/')[:-1])
        if not parent_path: parent_path = ""
        else: parent_path = f"/{parent_path}"
        
        url = f"{self.base_url}{parent_path}:runQuery"
        r = requests.post(url, headers=self._auth_header(), json=query)
        if r.status_code == 401:
            if self.refresh_auth():
                r = requests.post(url, headers=self._auth_header(), json=query)
        r.raise_for_status()
        
        results = []
        for res in r.json():
            if 'document' in res:
                doc = res['document']
                data = self.document_to_dict(doc)
                data['id'] = doc['name'].split('/')[-1]
                results.append(data)
        return results

    def batch(self):
        return BatchWriter(self)

class BatchWriter:
    def __init__(self, client):
        self.client = client
        self.writes = []

    def set(self, path, data):
        # path is a string relative to the base_url, e.g. "shops/SHOP1/products/123"
        # Wait, if we use db.collection('x').document('y'), we need mock objects for Collection and Document.
        pass

    def commit(self):
        if not self.writes: return
        url = f"https://firestore.googleapis.com/v1/projects/{self.client.project_id}/databases/(default)/documents:commit"
        payload = {"writes": self.writes}
        r = requests.post(url, headers=self.client._auth_header(), json=payload)
        if r.status_code == 401:
            if self.client.refresh_auth():
                r = requests.post(url, headers=self.client._auth_header(), json=payload)
        r.raise_for_status()

# To make it compatible with db.collection('x').document('y'):
class MockDocument:
    def __init__(self, client, path):
        self.client = client
        self.path = path
        
    def get(self):
        return self.client.get_document(self.path)
        
    def set(self, data):
        return self.client.set_document(self.path, data)
        
    def update(self, data):
        # Upsert for simplicity in this mock
        return self.client.set_document(self.path, data)
        
    def delete(self):
        return self.client.delete_document(self.path)

class MockCollection:
    def __init__(self, client, path):
        self.client = client
        self.path = path
        
    def document(self, doc_id=None):
        if not doc_id:
            import uuid
            doc_id = str(uuid.uuid4())
        return MockDocument(self.client, f"{self.path}/{doc_id}")
        
    def where(self, field, op, value):
        # Basic mapping of ops
        op_map = {'==': 'EQUAL', '<': 'LESS_THAN', '<=': 'LESS_THAN_OR_EQUAL', '>': 'GREATER_THAN', '>=': 'GREATER_THAN_OR_EQUAL', 'in': 'IN'}
        res = self.client.run_query(self.path, field, op_map.get(op, 'EQUAL'), value)
        return MockQuery(res)

    def stream(self):
        results = self.client.list_documents(self.path)
        for res in results:
            yield MockDocumentSnapshot(res)

class MockQuery:
    def __init__(self, results):
        self.results = results
        
    def stream(self):
        for res in self.results:
            yield MockDocumentSnapshot(res)
            
class MockDocumentSnapshot:
    def __init__(self, data):
        self._data = data
        self.id = data.get('id', '')
        
    def to_dict(self):
        return self._data
        
    @property
    def exists(self):
        return bool(self._data)

# Inject mock into BatchWriter
def _batch_set(self, doc_ref, data):
    # doc_ref is a MockDocument
    self.writes.append({
        "update": {
            "name": f"projects/{self.client.project_id}/databases/(default)/documents/{doc_ref.path}",
            **self.client.dict_to_document(data)
        }
    })
BatchWriter.set = _batch_set

# Inject collection into FirestoreClient
FirestoreClient.collection = lambda self, name: MockCollection(self, name)

firestore = FirestoreClient()

