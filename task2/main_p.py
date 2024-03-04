import requests
import json
import http.client
import smtplib
from time import sleep
import ssl
import http.client
from string import Template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from dotenv import dotenv_values

def get_access_token(client_id, client_secret):
    token_url = "https://api.surveymonkey.com/oauth/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(token_url, data=data)
    access_token = response.json().get("access_token")
    return access_token

config = dotenv_values(".env")
client_id = config["client_id"]
client_secret = config["client_secret"]
access_token = get_access_token(client_id, client_secret)
sender_mail = config["EMAIL"]
password = config["PASSWORD"].strip()

def get_template(filename):
    template_file = open(filename, mode="r", encoding="utf-8")
    template_file_content = template_file.read()
    return Template(template_file_content)

msg_template = get_template("template.txt")

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def create_survey(name_survey):
    conn = http.client.HTTPSConnection("api.surveymonkey.com")
    payload = {
        "title": name_survey,
        "nickname": "Reuben's Survey",
        "language": "en",
        "buttons_text": {
            "next_button": "Next Question",
            "prev_button": "Previous Question",
            "exit_button": "Exit Survey",
            "done_button": "Submit Survey"
        },
        "custom_variables": {},
        "footer": True,
    }

    headers = {
        'Content-Type': "application/json",
        'Accept': "application/json",
        'Authorization': f"Bearer {access_token}"
        }

    json_payload = json.dumps(payload)

    conn.request("POST", "/v3/surveys", json_payload, headers)
    res = conn.getresponse()
    data = res.read()
    survey_data = json.loads(data)
    survey_id = survey_data["id"]
    return(survey_id)

def insert_questions(survey_id):
    conn = http.client.HTTPSConnection("api.surveymonkey.com")

    headers = {
        'Content-Type': "application/json",
        'Accept': "application/json",
        'Authorization': f"Bearer {access_token}"
    }

    page1_payload = {
        "title": "first page",
        "description": "holds the questions"
    }

    page2_payload = {
        "title": "second page",
        "description": "holds the other questions"
    }

    requests.post(f"https://api.surveymonkey.com/v3/surveys/{survey_id}/pages", json=page1_payload, headers=headers)    
    requests.post(f"https://api.surveymonkey.com/v3/surveys/{survey_id}/pages", json=page2_payload, headers=headers)

    pages_response = requests.get(f"https://api.surveymonkey.com/v3/surveys/{survey_id}/pages", headers=headers)
    pages_json = pages_response.json()
    page_ids = [page["id"] for page in pages_json["data"]]
    
    page1_id = page_ids[0]

    survey_questions = read_json_file("questions.json")

    for page_name, page_data in survey_questions["Favorite_Foods_Survey"].items():
        for question_name, question_data in page_data.items():
            question_payload = {
                "headings": [{"heading": question_data["Description"]}],
                "family": "single_choice",
                "subtype": "vertical",
                "answers": {"choices": [{"text": answer} for answer in question_data["Answers"]]},
            }
            response = requests.post(f"https://api.surveymonkey.com/v3/surveys/{survey_id}/pages/{page1_id}/questions", json=question_payload, headers=headers)
            print(f"Added question '{question_data['Description']}' to the survey. Response: {response.json()}")
            print("\n")          
    
def create_collector(survey_id):
    conn = http.client.HTTPSConnection("api.surveymonkey.com")
    payload = {
        "type": "weblink",
        "name": "web_link_collector",
        "thank_you_page": {
            "is_enabled": True,
            "message": "Thanks for completing our survey!!!"
        },
        "thank_you_message": "tysm",
        "closed_page_message": "Survey fin",
        "display_survey_results": True,
        "allow_multiple_responses": True,
    }
    headers = {
        'Content-Type': "application/json",
        'Accept': "application/json",
        'Authorization': f"Bearer {access_token}"
        }
    collector_data = requests.post(f"https://api.surveymonkey.com/v3/surveys/{survey_id}/collectors", json=payload, headers=headers)
    collector_data = collector_data.json()
    print(collector_data)
    return collector_data.get("url", None)

def login(sender_email, password):
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(sender_email, password)
    return server

def mail_service(server, sender_email, receiver_email, survey_link):
    if server:
        message_body = msg_template.substitute(LINK=survey_link)
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "Survey Invitation"
        message.attach(MIMEText(message_body, "plain"))
        server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"Invitation sent to {receiver_email}")

def send_mails(survey_link, emails):
    server = login(sender_mail, password)
    if server:
        for email in emails:
            mail_service(server, sender_mail, email, survey_link)
        server.quit()

def main():
    with open("recipients.txt", "r") as text_file:
        recipients_data = text_file.read().splitlines()
    emails=[]
    for email in recipients_data:
        emails.append(email)
    survey_name = input("Enter the name of the survey: ")
    print("\nCREATING SURVEY...")
    survey_id = create_survey(survey_name)
    print(f"SURVEY CREATED WITH SURVEY ID: {survey_id}")
    sleep(0.5)
    print("\nLOADING QUESTIONS...")
    insert_questions(survey_id)
    print("\nSETTING UP MAIL CLIENT...")
    survey_link = create_collector(survey_id)
    print("\nSENDING EMAILS...")
    send_mails(survey_link, emails)
    print("\n---fin---")


if __name__ == "__main__":
    main()