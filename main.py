from flask import Flask, render_template, redirect, url_for, flash, abort,request
import requests
import os
from dotenv import load_dotenv
from form import ContactForm
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import gunicorn


load_dotenv()
STRAPI_URL = os.getenv("STRAPI_URL")


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_KEY")

@app.route('/')
def home():
    return render_template("index.html")

def get_projects():
    try:
        
        headers = {
            "Authorization": f"Bearer {os.getenv("STRAPI_API_TOKEN")}"
        }
        response = requests.get(STRAPI_URL, headers=headers, timeout=10)
        response.raise_for_status()
        projects = response.json().get('data', [])
        

        for project in projects:
            if 'thumbnail' in project and isinstance(project['thumbnail'], list):
                for image in project['thumbnail']:
                    if 'url' in image and image['url'].startswith('/'):
                        # Construct full URL from Strapi base
                        strapi_base = STRAPI_URL.split('/api/')[0]
                        image['url'] = strapi_base + image['url']
                        print(f"DEBUG: Thumbnail URL updated to: {image['url']}")
        
        print(f"DEBUG: Total projects: {len(projects)}")
        if projects:
            print(f"DEBUG: First project thumbnails: {len(projects[0].get('thumbnail', []))}")
            if projects[0].get('thumbnail'):
                print(f"DEBUG: First image URL: {projects[0]['thumbnail'][0].get('url')}")
        
        return projects
    except requests.exceptions.RequestException as e:
        print(f"Error fetching projects: {e}")
        return []

@app.route('/projects')
def projects():
    projects = get_projects()
    return render_template("projects.html", projects=projects)

@app.route('/contact',methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        form_name = form.name.data
        form_email = form.email.data
        
        try:
            print(f"DEBUG: Form submitted with Name: {form_name}, Email: {form_email}, Message: {form.message.data}")
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as connection:
                connection.login(user=os.getenv("TO_EMAIL"),password=os.getenv("EMAIL_APP_PASSWORD"))
                
                msg = MIMEMultipart()
                msg['From'] = os.getenv("TO_EMAIL")
                msg['To'] = os.getenv("TO_EMAIL")
                msg['Subject'] = f"Contact Form Submission from {form_name}"
                
                body = f"Name: {form_name}\nEmail: {form_email}\n\nMessage:\n{form.message.data}"
                msg.attach(MIMEText(body, 'plain'))
                
                connection.sendmail(
                    from_addr=os.getenv("TO_EMAIL"),
                    to_addrs=os.getenv("TO_EMAIL"),
                    msg=msg.as_string()
                )
            print("Email sent successfully!")
            flash("Message sent successfully!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            print(f"An error occurred: {e}")
            flash(f"Error sending message: {str(e)}", "error")
    return render_template("contact.html",form=form)



if __name__ == "__main__":
    app.run(debug=False)