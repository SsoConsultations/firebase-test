import streamlit as st
import os
from supabase import create_client, Client

# --- Supabase Initialization ---
def initialize_supabase_client() -> Client:
    """
    Initializes and returns the Supabase client.
    Reads Supabase URL and Anon Key from environment variables.
    """
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_ANON_KEY"]

    if not supabase_url or not supabase_key:
        st.error("Supabase URL or Anon Key not found in environment variables. "
                 "Please configure SUPABASE_URL and SUPABASE_ANON_KEY.")
        st.stop() # Stop the app if crucial variables are missing

    try:
        # Check if client already exists in session state to prevent re-initialization
        if 'supabase_client' not in st.session_state:
            st.session_state['supabase_client'] = create_client(supabase_url, supabase_key)
            st.success("Supabase client initialized successfully!")
        return st.session_state['supabase_client']
    except Exception as e:
        st.error(f"Error initializing Supabase client: {e}")
        st.stop() # Stop the app on critical initialization failure

# --- Main Streamlit Application Logic ---
def main():
    st.set_page_config(page_title="Supabase Connection Test", page_icon="🟢")
    st.title("Supabase Connection Test")
    st.write("This app tests connectivity to your Supabase project and the 'test_messages' table.")

    # Initialize Supabase client
    supabase: Client = initialize_supabase_client()
    
    if supabase:
        st.header("Supabase 'test_messages' Table Operations")
        
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Write Data")
            new_message = st.text_input("Enter a message to save:", "Hello Supabase from Streamlit!")
            author = st.text_input("Your Name/ID:", "TestUser")

            if st.button("Save Message to Supabase"):
                try:
                    response = supabase.table("test_messages").insert(
                        {"message_text": new_message, "author": author}
                    ).execute()
                    if response.data:
                        st.success(f"Message saved: '{new_message}' by '{author}'")
                        st.write("Response from Supabase:", response.data)
                    else:
                        st.error(f"Failed to save message: {response.error}")
                        st.write("Supabase Error:", response.error)
                except Exception as e:
                    st.error(f"An error occurred during save: {e}")

        with col2:
            st.subheader("Read Data")
            if st.button("Load Messages from Supabase"):
                try:
                    response = supabase.table("test_messages").select("*").order("created_at", desc=True).limit(5).execute()
                    if response.data:
                        st.write("Latest messages from 'test_messages' table:")
                        for msg in response.data:
                            st.json(msg)
                    else:
                        st.info("No messages found in 'test_messages' table.")
                        st.write("Supabase Error (if any):", response.error)
                except Exception as e:
                    st.error(f"An error occurred during load: {e}")

    st.markdown("---")
    st.info("Remember: For security in a real app, manage Row Level Security (RLS) in Supabase and "
            "use server-side logic for sensitive operations, not direct client-side calls for all data.")

if __name__ == "__main__":
    # Clear any lingering Firebase objects if this is a fresh start
    if 'firestore_db' in st.session_state:
        del st.session_state['firestore_db']
    if 'bucket' in st.session_state:
        del st.session_state['bucket']
    # You might also want to ensure no old firebase_admin apps are present
    # if firebase_admin._apps:
    #     for app_name in list(firebase_admin._apps.keys()):
    #         firebase_admin.delete_app(firebase_admin.get_app(app_name))

    main()
