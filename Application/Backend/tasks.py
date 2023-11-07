from datetime import datetime
from workers import celery
from celery.schedules import crontab
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import csv

celery.conf.beat_schedule = {
    'run_task_every_day':{
        'task': 'send_daily',
        'schedule': crontab(hour=17, minute=0),
    },
    'run_task_every_30_days': {
        'task': 'send_monthly',
        'schedule': crontab(day_of_month='1', hour=0, minute=0),
    }
}


@celery.task()
def just_say_hello(name):
        print( "INSIDE TASK")
        print("hello"+str(name))
# code to run at 5pm every day

def format_message(template_file, data={}):
    with open(template_file) as file_:
        template = Template(file_.read())
        return template.render(data=data)


@celery.task()
def send_monthly(attachment_file,message, address, content="html"): 
    subject = "Monthly report"
    SMPTP_SERVER_HOST = "localhost"
    SMPTP_SERVER_PORT = 1025
    SENDER_ADDRESS = "email@hasingh.com"
    SENDER_PASSWORD = "" 
    msg = MIMEMultipart()

    msg["From"] = SENDER_ADDRESS
    msg["To"] = address
    msg["Subject"] = subject

    if content == "html":
        msg.attach(MIMEText(message, "html"))
    else:
        msg.attach(MIMEText(message, "plain"))

    if attachment_file:
        with open(attachment_file, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read()) 
        encoders.encode_base64(part)
        
        part.add_header(
            "Content-Disposition", f"attachment; filename= {attachment_file}",
        )
        msg.attach(part)

    s = smtplib.SMTP(host=SMPTP_SERVER_HOST, port=SMPTP_SERVER_PORT)
    
    s.login(SENDER_ADDRESS, SENDER_PASSWORD)
    s.send_message(msg)
    s.quit()
    
@celery.task()
def send_export_csv(subject,attachment_file,message, address, content="html"): 
    SMPTP_SERVER_HOST = "localhost"
    SMPTP_SERVER_PORT = 1025
    SENDER_ADDRESS = "email@hasingh.com"
    SENDER_PASSWORD = "" 
    msg = MIMEMultipart()

    msg["From"] = SENDER_ADDRESS
    msg["To"] = address
    msg["Subject"] = subject

    if content == "html":
        msg.attach(MIMEText(message, "html"))
    else:
        msg.attach(MIMEText(message, "plain"))

    if attachment_file:
        with open(attachment_file, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read()) 
        encoders.encode_base64(part)
        
        part.add_header(
            "Content-Disposition", f"attachment; filename= {attachment_file}",
        )
        msg.attach(part)

    s = smtplib.SMTP(host=SMPTP_SERVER_HOST, port=SMPTP_SERVER_PORT)
    
    s.login(SENDER_ADDRESS, SENDER_PASSWORD)
    s.send_message(msg)
    s.quit()
    

@celery.task()
def send_daily(content="html",attachment_file=None, address="sampleaddress@mail.com"): 
    data = {"name": "User", "email":"sampleuser@mail.com"}
    message = format_message("daily_scheduled_mail.html", data=data)
    subject = "daily mail"
    SMPTP_SERVER_HOST = "localhost"
    SMPTP_SERVER_PORT = 1025
    SENDER_ADDRESS = "email@hasingh.com"
    SENDER_PASSWORD = "" 
    msg = MIMEMultipart()

    msg["From"] = SENDER_ADDRESS
    msg["To"] = address
    msg["Subject"] = subject

    if content == "html":
        msg.attach(MIMEText(message, "html"))
    else:
        msg.attach(MIMEText(message, "plain"))

    if attachment_file:
        with open(attachment_file, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read()) 
        encoders.encode_base64(part)
        
        part.add_header(
            "Content-Disposition", f"attachment; filename= {attachment_file}",
        )
        msg.attach(part)

    s = smtplib.SMTP(host=SMPTP_SERVER_HOST, port=SMPTP_SERVER_PORT)
    
    s.login(SENDER_ADDRESS, SENDER_PASSWORD)
    s.send_message(msg)
    s.quit()
    

       

      
    