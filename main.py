from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask import Flask, render_template, redirect, url_for, flash, abort, request
import requests
import os
import time
import time
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



PROJECT_CACHE = None
CACHE_TIMESTAMP = 0
CACHE_TTL = 600  




PROJECT_CACHE = None
CACHE_TIMESTAMP = 0
CACHE_TTL = 600  


@app.route('/')
def home():
    return render_template("index.html")



def get_projects():
    global PROJECT_CACHE, CACHE_TIMESTAMP

    now = time.time()

    # Return cached data if still valid
    if PROJECT_CACHE and (now - CACHE_TIMESTAMP < CACHE_TTL):
        print("DEBUG: Returning cached projects")
        return PROJECT_CACHE

    global PROJECT_CACHE, CACHE_TIMESTAMP

    now = time.time()

    # Return cached data if still valid
    if PROJECT_CACHE and (now - CACHE_TIMESTAMP < CACHE_TTL):
        print("DEBUG: Returning cached projects")
        return PROJECT_CACHE

    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('STRAPI_API_TOKEN')}"
        }


        response = requests.get(STRAPI_URL, headers=headers, timeout=10)
        response.raise_for_status()


        projects = response.json().get('data', [])


        if projects and projects[0].get('thumbnail'):
            print(f"DEBUG: First project has {len(projects[0]['thumbnail'])} thumbnail(s)")

        # Save to cache
        PROJECT_CACHE = projects
        CACHE_TIMESTAMP = now

        print("DEBUG: Projects cached successfully")


        # Save to cache
        PROJECT_CACHE = projects
        CACHE_TIMESTAMP = now

        print("DEBUG: Projects cached successfully")

        return projects


    except requests.exceptions.RequestException as e:
        print(f"Error fetching projects: {e}")

        # Fallback to cache if API fails
        if PROJECT_CACHE:
            print("DEBUG: Returning stale cache due to API failure")
            return PROJECT_CACHE


        # Fallback to cache if API fails
        if PROJECT_CACHE:
            print("DEBUG: Returning stale cache due to API failure")
            return PROJECT_CACHE

        return []


# -----------------------------
# STARTUP CACHE WARMING
# -----------------------------
@app.before_request
def warm_cache():
    print("DEBUG: Warming API cache on startup...")
    get_projects()


@app.route('/projects')
def projects():
    projects = get_projects()


    print(f"DEBUG: Passing {len(projects)} projects to template")


    if projects:
        print(f"DEBUG: First project thumbnail count: {len(projects[0].get('thumbnail', []))}")


        if projects[0].get('thumbnail'):
            print(f"DEBUG: First thumbnail URL: {projects[0]['thumbnail'][0].get('url')}")


    return render_template("projects.html", projects=projects)


@app.route('/contact', methods=["GET", "POST"])

@app.route('/contact', methods=["GET", "POST"])
def contact():
    form = ContactForm()


    if form.validate_on_submit():
        form_name = form.name.data
        form_email = form.email.data


        try:
            print(f"DEBUG: Form submitted with Name: {form_name}, Email: {form_email}, Message: {form.message.data}")


            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as connection:
                connection.login(
                    user=os.getenv("TO_EMAIL"),
                    password=os.getenv("EMAIL_APP_PASSWORD")
                )

                connection.login(
                    user=os.getenv("TO_EMAIL"),
                    password=os.getenv("EMAIL_APP_PASSWORD")
                )

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


            flash("Message sent successfully!", "success")
            return redirect(url_for('home'))


        except Exception as e:
            print(f"An error occurred: {e}")
            flash(f"Error sending message: {str(e)}", "error")

    return render_template("contact.html", form=form)

    return render_template("contact.html", form=form)


# -----------------------------
# HEALTH ROUTE (for uptime monitoring)
# -----------------------------
@app.route('/health')
def health():
    return {"status": "ok", "service": "portfolio-api"}

# -----------------------------
# HEALTH ROUTE (for uptime monitoring)
# -----------------------------
@app.route('/health')
def health():
    return {"status": "ok", "service": "portfolio-api"}


if __name__ == "__main__":
    app.run(debug=False)