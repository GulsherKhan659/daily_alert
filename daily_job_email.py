import os
import smtplib
import requests
import feedparser
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- SECURE CONFIGURATION (Loaded from GitHub Secrets) ---
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

def get_newspaper_jobs():
    print("Scanning Newspapers via Google News...")
    # RSS Feed for 'Sindh Government Jobs'
    rss_url = "https://news.google.com/rss/search?q=Sindh+Government+Jobs+Pakistan&hl=en-PK&gl=PK&ceid=PK:en"
    
    try:
        feed = feedparser.parse(rss_url)
        jobs = []
        for entry in feed.entries[:5]: 
            jobs.append(f"📰 {entry.title}\n   Link: {entry.link}")
        return jobs
    except Exception as e:
        print(f"Error scanning news: {e}")
        return []

def get_rozee_jobs():
    print("Scanning Rozee.pk for Govt Jobs...")
    url = "https://www.rozee.pk/job/jsearch/q/sindh%20government"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        jobs = []
        
        job_divs = soup.find_all('div', class_='job-t')
        
        for job in job_divs[:5]:
            title = job.find('a').text.strip()
            link = job.find('a')['href']
            if not link.startswith("http"):
                link = "https://www.rozee.pk" + link
            jobs.append(f"💼 {title}\n   Link: {link}")
            
        return jobs
    except Exception as e:
        print(f"Error scanning Rozee: {e}")
        return []

def send_daily_email(news_jobs, portal_jobs):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("Error: Missing Email Secrets!")
        return

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"DAILY ALERT: Sindh Govt Jobs ({datetime.now().strftime('%d-%b')})"

    body = "Here is your daily summary:\n\n"
    body += "--- 📰 NEWSPAPER HIGHLIGHTS ---\n"
    body += "\n\n".join(news_jobs) if news_jobs else "No new newspaper alerts."
    body += "\n\n--- 💼 JOB PORTAL LISTINGS ---\n"
    body += "\n\n".join(portal_jobs) if portal_jobs else "No new portal listings."
    body += "\n\n(Automated by GitHub Actions)"

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("✅ Daily Email Sent Successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    news = get_newspaper_jobs()
    rozee = get_rozee_jobs()
    
    if news or rozee:
        send_daily_email(news, rozee)
    else:
        print("No new jobs found today.")