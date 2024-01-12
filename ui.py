import streamlit as st
import requests
import json
from PyPDF2 import PdfReader
import os
import re

API_ENDPOINT = "https://api.askyourpdf.com/v1/api/upload"
api_key = "ask_161c48be07ba0c38d676da599924e8de"  # ADD YOUR ASKMYPDF API KEY HERE, this one expires in at the end of December
file_path = "prompts.json"
headers = {"x-api-key": api_key}
ui_path = os.path.abspath(__file__)
directory = os.path.dirname(ui_path)


def extract_numbers(text):
    # This regex pattern looks for numbers and percentages
    # The updated pattern ensures we don't capture empty matches
    pattern = r"\b\d+(?:\.\d+)?%?\b"
    return re.findall(pattern, text)


def check_file_exists(file_path):
    return os.path.exists(file_path)


def normalize_number(number):
    if number.endswith("%"):
        return float(number.rstrip("%")), True
    return float(number), False


def validate_numbers(summary, source_text):
    summary_numbers = extract_numbers(summary)
    source_text_numbers = extract_numbers(source_text)

    # Normalize numbers
    summary_numbers = [normalize_number(num) for num in summary_numbers]
    source_text_numbers = [normalize_number(num) for num in source_text_numbers]

    non_matching_numbers = []

    # Check for matching numbers
    for num, is_percent in summary_numbers:
        if is_percent:
            if not any(
                (num == s_num or num / 100 == s_num)
                for s_num, s_is_percent in source_text_numbers
            ):
                non_matching_numbers.append(f"{num}%")
        else:
            if not any(num == s_num for s_num, s_is_percent in source_text_numbers):
                non_matching_numbers.append(str(num))

    return non_matching_numbers


def extract_pdf_text(file_path):
    text = ""
    with open(file_path, "rb") as file:
        pdf_reader = PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text


def load_prompts(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    else:
        # Return a default dictionary if the file doesn't exist
        return {"example": "This is a default prompt"}


def save_prompts(prompts, file_path):
    with open(file_path, "w") as file:
        json.dump(prompts, file)


def read_pdf(file):
    pdfReader = PdfReader(file)
    count = len(pdfReader.pages)
    all_page_text = ""
    for i in range(count):
        page = pdfReader.pages[i]
        all_page_text += page.extract_text()

    return all_page_text


def upload_pdf(pdf_path):
    with open(pdf_path, "rb") as file_data:
        response = requests.post(
            API_ENDPOINT, headers=headers, files={"file": file_data}
        )

    if response.status_code == 201:
        return response.json()["docId"]
    else:
        raise Exception(f"Error uploading file: {response.text}")


def ask_question(question, docId):
    data = [{"sender": "User", "message": question}]

    response = requests.post(
        f"https://api.askyourpdf.com/v1/chat/{docId}",
        headers=headers,
        data=json.dumps(data),
    )
    if response.status_code == 200:
        return response.json()["answer"]["message"]
    else:
        return response.text


def main():
    prompt_dict = load_prompts(file_path)
    # open('overall.txt', 'w').close()
    st.image("nexteer.png", width=100)
    st.title("Dashboard Summary Generator")

    st.markdown("---")

    # Change to your working directory and correct file path
    sourcing_file = directory + "/kpis/sourcing.pdf"
    ppap_file = directory + "/kpis/ppap.pdf"
    gate_file = directory + "/kpis/gate.pdf"
    cost_file = directory + "/kpis/meet.pdf"
    overall_file = directory + "/kpis/overall.pdf"

    col1, col2, col3 = st.columns(3)

    if "source_clicked" not in st.session_state:
        st.session_state["source_clicked"] = False
    if "ppap_clicked" not in st.session_state:
        st.session_state["ppap_clicked"] = False
    if "gate_clicked" not in st.session_state:
        st.session_state["gate_clicked"] = False
    if "cost_clicked" not in st.session_state:
        st.session_state["cost_clicked"] = False

    with col1:
        button_sourse = st.button("Sourcing On Time", use_container_width=True)
        st.session_state["source_clicked"] |= button_sourse
        button_ppap = st.button("PPAP On Time", use_container_width=True)
        st.session_state["ppap_clicked"] |= button_ppap

    with col2:
        button_gate = st.button("Gate Review", use_container_width=True)
        st.session_state["gate_clicked"] |= button_gate
        button_all = st.button("Executive Summary", use_container_width=True)

    with col3:
        button_cost = st.button("Meet Costbook", use_container_width=True)
        st.session_state["cost_clicked"] |= button_cost
        button_clear = st.button("Clear", use_container_width=True)

    # Button to process the query
    if button_sourse:
        sourcing_file = directory + "/kpis/sourcing.pdf"
        if check_file_exists(sourcing_file):
            st.markdown("---")
            st.markdown("## **Sourcing On Time Summary**")
            sourcing_doc_id = upload_pdf(sourcing_file)
            text = ask_question(prompt_dict["Sourcing on Time"], sourcing_doc_id)
            st.write(text)
            source_text = extract_pdf_text(sourcing_file)
            non_matching_numbers = validate_numbers(text, source_text)
            if non_matching_numbers:
                # Display warning if there are non-matching numbers
                st.warning(
                    f"Unable to verify numbers from the source: {', '.join(non_matching_numbers)}"
                )
            if not button_all:
                with open("overall.txt", "a+") as file:
                    file.write("## **Sourcing On Time Summary**\n")
                    file.write(text + "\n\n")
        else:
            st.warning(
                'The "Sourcing On Time" summary requires "sourcing.pdf" in the "kpis" folder.'
            )

    if button_ppap:
        ppap_file = directory + "/kpis/ppap.pdf"
        if check_file_exists(ppap_file):
            st.markdown("---")
            st.markdown("## **Perfect Launch - PPAP On Time Summary**")
            ppap_doc_id = upload_pdf(ppap_file)
            text = ask_question(prompt_dict["PPAP on Time"], ppap_doc_id)
            st.write(text)
            source_text = extract_pdf_text(ppap_file)
            non_matching_numbers = validate_numbers(text, source_text)
            if non_matching_numbers:
                # Display warning if there are non-matching numbers
                st.warning(
                    f"Unable to verify numbers from the source: {', '.join(non_matching_numbers)}"
                )
            if not button_all:
                with open("overall.txt", "a+") as file:
                    file.write("## **Perfect Launch - PPAP On Time Summary**\n")
                    file.write(text + "\n\n")
        else:
            st.warning(
                'The "Perfect Launch - PPAP On Time" summary requires "ppap.pdf" in the "kpis" folder.'
            )

    if button_gate:
        gate_file = directory + "/kpis/gate.pdf"
        if check_file_exists(gate_file):
            st.markdown("---")
            st.markdown("## **Gate Review On Time Summary**")
            gate_doc_id = upload_pdf(gate_file)
            text = ask_question(prompt_dict["Gate Review"], gate_doc_id)
            st.write(text)
            source_text = extract_pdf_text(gate_file)
            non_matching_numbers = validate_numbers(text, source_text)
            if non_matching_numbers:
                # Display warning if there are non-matching numbers
                st.warning(
                    f"Unable to verify numbers from the source: {', '.join(non_matching_numbers)}"
                )
            if not button_all:
                with open("overall.txt", "a+") as file:
                    file.write("## **Gate Review On Time Summary**\n")
                    file.write(text + "\n\n")
        else:
            st.warning(
                'The "Gate Review On Time" summary requires "gate.pdf" in the "kpis" folder.'
            )

    if button_cost:
        cost_file = directory + "/kpis/meet.pdf"
        if check_file_exists(cost_file):
            st.markdown("---")
            st.markdown("## **Perfect Launch - Meet Costbook Summary**")
            cost_doc_id = upload_pdf(cost_file)
            text = ask_question(prompt_dict["Meets Costbook"], cost_doc_id)
            st.write(text)
            source_text = extract_pdf_text(cost_file)
            non_matching_numbers = validate_numbers(text, source_text)
            if non_matching_numbers:
                # Display warning if there are non-matching numbers
                st.warning(
                    f"Unable to verify numbers from the source: {', '.join(non_matching_numbers)}"
                )
            if not button_all:
                with open("overall.txt", "a+") as file:
                    file.write("## **Perfect Launch - Meet Costbook Summary**\n")
                    file.write(text + "\n\n")
        else:
            st.warning(
                'The "Perfect Launch - Meet Costbook" summary requires "meet.pdf" in the "kpis" folder.'
            )

    # Check if all other buttons have been clicked
    all_buttons_clicked = (
        st.session_state["source_clicked"]
        and st.session_state["ppap_clicked"]
        and st.session_state["gate_clicked"]
        and st.session_state["cost_clicked"]
    )
    if all_buttons_clicked:
        if button_all:
            st.markdown("---")
            st.markdown("## **Executive Summary**")
            # Read the contents of 'overall.txt'
            # with open("overall.txt", "rb") as file:
            #     overall_text = file.read()

            # Create the overall_prompt variable
            overall_prompt = prompt_dict["Executive Summary"]
            summaries_doc_id = upload_pdf("overall.txt")
            dashboard_doc_id = upload_pdf(overall_file)
            print(dashboard_doc_id)
            # Use overall_prompt in ask_question
            text1 = ask_question(prompt_dict["Overall Dashboard"], dashboard_doc_id)
            text2 = ask_question(overall_prompt, summaries_doc_id)
            with open("executive.txt", "w") as file:
                file.write(text1)
                file.write(text2)
            overall_doc_id = upload_pdf("executive.txt")
            text = ask_question(prompt_dict["Integration"], overall_doc_id)
            st.write(text)

    if not all_buttons_clicked and button_all:
        st.warning(
            "Please get individual summary for all other KPIs first before getting the overall summary."
        )

    if button_clear:
        button_all = False
    # Checkbox to toggle edit mode
    edit = st.checkbox("Edit prompts?")
    if edit:
        # Dropdown to select the word
        prompt_to_edit = st.selectbox(
            "Choose a word to edit", options=list(prompt_dict.keys())
        )

        # Text area for editing the definition
        new_prompt = st.text_area("Edit prompt", value=prompt_dict[prompt_to_edit])

        # Button to save the new definition
        if st.button("Save Prompt"):
            prompt_dict[prompt_to_edit] = new_prompt
            save_prompts(prompt_dict, file_path)
            st.success(f"Prompt for '{prompt_to_edit}' updated.")


if __name__ == "__main__":
    main()
