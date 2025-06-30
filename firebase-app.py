import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import time

# --- Firebase Initialization ---
def initialize_firebase_app():
    """
    Initializes the Firebase Admin SDK using secrets from Streamlit.
    """
    global firebase_app, db

    if firebase_admin._apps: # Check if Firebase app is already initialized
        print("DEBUG (Firebase Init): Firebase app already initialized.")
        st.info("Firebase app already initialized.")
        db = firestore.client(app=firebase_admin.get_app())
        st.session_state['firestore_db'] = db
        return firebase_admin.get_app()

    print("DEBUG (Firebase Init): Attempting to initialize Firebase app...")
    try:
        # Define all required individual service account key fields
        # These keys MUST match the names in your .streamlit/secrets.toml
        required_secrets = [
            "firebase_admin_sdk_type",
            "firebase_admin_sdk_project_id",
            "firebase_admin_sdk_private_key_id",
            "firebase_admin_sdk_private_key",
            "firebase_admin_sdk_client_email",
            "firebase_admin_sdk_client_id",
            "firebase_admin_sdk_auth_uri",
            "firebase_admin_sdk_token_uri",
            "firebase_admin_sdk_auth_provider_x509_cert_url",
            "firebase_admin_sdk_client_x509_cert_url",
            "firebase_admin_sdk_universe_domain"
        ]

        missing_secrets = [s for s in required_secrets if s not in st.secrets]
        if missing_secrets:
            st.error(f"Missing Firebase Admin SDK secrets: {', '.join(missing_secrets)}. Please configure them in .streamlit/secrets.toml or Streamlit Cloud secrets.")
            print(f"ERROR (Firebase Init): Missing secrets: {missing_secrets}")
            st.stop() # Stop the app if crucial secrets are missing
            
        # Construct the credentials dictionary from individual secrets
        # IMPORTANT: Replace '\\n' with '\n' for the private_key if it's escaped in secrets.toml
        firebase_service_account_config = {
            "type": st.secrets["firebase_admin_sdk_type"],
            "project_id": st.secrets["firebase_admin_sdk_project_id"],
            "private_key_id": st.secrets["firebase_admin_sdk_private_key_id"],
            "private_key": st.secrets["firebase_admin_sdk_private_key"].replace('\\n', '\n'),
            "client_email": st.secrets["firebase_admin_sdk_client_email"],
            "client_id": st.secrets["firebase_admin_sdk_client_id"],
            "auth_uri": st.secrets["firebase_admin_sdk_auth_uri"],
            "token_uri": st.secrets["firebase_admin_sdk_token_uri"],
            "auth_provider_x509_cert_url": st.secrets["firebase_admin_sdk_auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["firebase_admin_sdk_client_x509_cert_url"],
            "universe_domain": st.secrets["firebase_admin_sdk_universe_domain"],
        }
        print("DEBUG (Firebase Init): Firebase service account config loaded from secrets.")

        # Initialize the app with credentials
        firebase_app = firebase_admin.initialize_app(credentials.Certificate(firebase_service_account_config))
        db = firestore.client(app=firebase_app)
        
        st.session_state['firestore_db'] = db # Store in session state for access
        
        st.success("Firebase Admin SDK and Firestore client initialized successfully!")
        print("DEBUG (Firebase Init): Firebase app and Firestore client initialized.")
        return firebase_app

    except Exception as e:
        st.error(f"Error initializing Firebase services: {e}")
        print(f"ERROR (Firebase Init): Initialization failed - {e}")
        st.stop() # Stop the app on critical initialization failure

# --- Main Streamlit Application Logic ---
def main():
    st.set_page_config(page_title="Firebase Test App", page_icon="🔥")
    st.title("Firebase Connection Test")
    st.write("This app tests connectivity to Firebase Admin SDK and Firestore.")

    # Initialize Firebase
    app = initialize_firebase_app()
    
    if app:
        st.header("Firestore Test")
        test_collection_name = "test_connectivity"
        test_doc_id = "streamlit_test_doc"
        
        # Access Firestore client from session state
        db_client = st.session_state.get('firestore_db')
        
        if db_client:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Write Data")
                test_message = st.text_input("Message to save to Firestore", "Hello Firebase!")
                if st.button("Save to Firestore"):
                    try:
                        doc_ref = db_client.collection(test_collection_name).document(test_doc_id)
                        doc_ref.set({
                            "message": test_message,
                            "timestamp": firestore.SERVER_TIMESTAMP
                        })
                        st.success(f"Message saved: '{test_message}' to '{test_collection_name}/{test_doc_id}'")
                        print(f"DEBUG (Firestore Write): Saved message '{test_message}'")
                    except Exception as e:
                        st.error(f"Error writing to Firestore: {e}")
                        print(f"ERROR (Firestore Write): {e}")

            with col2:
                st.subheader("Read Data")
                if st.button("Read from Firestore"):
                    try:
                        doc_ref = db_client.collection(test_collection_name).document(test_doc_id)
                        doc = doc_ref.get()
                        if doc.exists:
                            data = doc.to_dict()
                            st.write("Latest data from Firestore:")
                            st.json(data)
                            print(f"DEBUG (Firestore Read): Read data: {data}")
                        else:
                            st.info("No data found at specified path. Try saving first!")
                            print("DEBUG (Firestore Read): Document does not exist.")
                    except Exception as e:
                        st.error(f"Error reading from Firestore: {e}")
                        print(f"ERROR (Firestore Read): {e}")
        else:
            st.warning("Firestore client not available. Initialization might have failed.")

if __name__ == "__main__":
    main()
