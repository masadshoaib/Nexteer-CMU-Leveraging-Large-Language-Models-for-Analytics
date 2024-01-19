import streamlit as st
import requests

API_KEY = "your_API_KEY"
API_ENDPOINT = "https://api.askyourpdf.com/v1/api/upload"

def upload_pdf_to_api(file):
    headers = {
        'x-api-key': API_KEY
    }
    files = {
        'file': file
    }
    response = requests.post(API_ENDPOINT, headers=headers, files=files)
    if response.status_code == 201:
        return response.json().get("doc_id")
    else:
        st.error(f"Error uploading file: {response.text}")
        return None

def main():
    st.title("Executive Summary Generator")

    # File upload option
    uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

    # Check if a file is uploaded
    # if uploaded_file:
        # doc_id = upload_pdf_to_api(uploaded_file)
        # if doc_id:
        #     st.success(f"File uploaded successfully! Document ID: {doc_id}")

    # Add some space
    st.markdown("---")

    # Text input field for query with stylized title
    st.markdown("## **Query**")
    query_text = st.text_area("", "")

    # Button to process the query
    if st.button("Generate Summary"):
        if query_text:
            # Concatenate the string as described
            output_text = "The query asked is " + query_text

            # Add some space and display the output with a stylized title
            st.markdown("---")
            st.markdown("## **Output**")
            st.write(output_text)
        else:
            st.warning("Please enter a query!")

if __name__ == "__main__":
    main()
