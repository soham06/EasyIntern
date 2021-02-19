import tkinter as tk
from PIL import ImageTk, Image
import tkinter.font as font
import tkinter as ttk
import requests
import smtplib
import config
from bs4 import BeautifulSoup
import sys

jobs = []

# Web Scraping 
def extract_information(page_num, industry, location):
  headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'}
  URL = f'https://ca.indeed.com/jobs?q={industry}Intern&l={location}&fromage=3&start={page_num}'
  page = requests.get(URL, headers)
  soup = BeautifulSoup(page.content, 'html.parser')
  return soup

def transform(soup):
  divs = soup.find_all('div', class_='jobsearch-SerpJobCard')
  for item in divs:
    title = item.find('a').text.strip()
    company = item.find('span', class_='company').text.strip()
    location = item.find(class_='location accessible-contrast-color-location').text.strip()
    summary = item.find('div', class_='summary').text.strip()
    link = item.h2.a['href']
    if None in (title, location, summary, link):
            continue
    hyperlink = f"https://ca.indeed.com{link}\n"
    job_posting = {
      'title': title,
      'company': company,
      'location': location,
      'summary': summary,
      'link': hyperlink
    }
    jobs.append(job_posting)
  return

def send_email(email, msg):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    try:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(config.email, config.password)
        server.sendmail(config.email, email, msg.encode('utf-8'))
    except Exception as e:
        print(e)
    server.quit()

# GUI Implementation
app = tk.Tk()
app.title("Internship Searcher")
app.geometry('700x250')

#Title
img = Image.open('logo.png')
resized = img.resize((60, 45), Image.ANTIALIAS)
new_pic = ImageTk.PhotoImage(resized)
test = tk.PhotoImage(file="logo.png")
myFont = font.Font(family='Helvetica', size=30)
myFont2 = font.Font(family='Helvetica', size=20)
myFont3 = ("Verdana", 12)
my_label = tk.Label(app, text="Internship Searcher")
my_label.grid(row=0, column=1)
my_label["compound"] = tk.LEFT
my_label["image"] = new_pic
my_label['font'] = myFont

def popupmsg(msg):
    popup = tk.Tk()
    popup.wm_title("Disclaimer")
    label = ttk.Label(popup, text=msg, font=myFont3)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command = sys.exit)
    B1.pack()
    popup.mainloop()

def find_jobs():
    location = location_entry.get()
    industry = industry_entry.get()
    email = email_entry.get()
    words = industry.split()
    final_industry = ''
    location_entry.delete(0, 'end')
    industry_entry.delete(0, 'end')
    email_entry.delete(0, 'end')
    for word in words:
        final_industry += f"{word}+"
    for i in range(0,10,10):
        c = extract_information(i, final_industry, location)
        transform(c)
    body = ''
    for job in jobs:
        msg = f"""
            Job Title: {job['title']}
            Company: {job['company']}
            Location: {job['location']}
            Summary: {job['summary']}
            Link to Posting: {job['link']}
            """
        body += msg
    subject = 'New Job Postings'
    msg = f"Subject: {subject}\n\n{body}"
    if not jobs:
        popupmsg("No Job Postings in the Past 3 Days!")
    else:
        send_email(email, msg)
        popupmsg(f"Email sent to {email}")
    sys.exit()
           
location_label = tk.Label(app, text="Enter Internship Location:")
location_entry = tk.Entry(app)
location_label.grid(row=2, column=0)
location_entry.grid(row=2, column=1)

industry_label = tk.Label(app, text="Enter Internship Profession:")
industry_entry = tk.Entry(app)
industry_label.grid(row=3, column=0)
industry_entry.grid(row=3, column=1)

email_label = tk.Label(app, text="Enter Email Address:")
email_entry = tk.Entry(app)
email_label.grid(row=4, column=0)
email_entry.grid(row=4, column=1)

submit_button = tk.Button(app, text="Submit", command=find_jobs)
submit_button.grid(columnspan=2)
app.mainloop()
