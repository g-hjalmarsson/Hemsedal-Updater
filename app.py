import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import date
import os
import smtplib
from email.message import EmailMessage

EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]

#Create pandas database
df = pd.DataFrame(columns=['Date', 'Open_Slopes', 'Total_Slopes', 'Slope_Ratio', 'Open_Lifts', 'Total_Lifts', "Lift_Ratio", "Resort"])

#Send email
def send_email(total_slopes, open_slopes, slope_ratio, total_lifts, open_lifts, lift_ratio):
    msg = EmailMessage()
    msg.set_content(f"In Hemsedal there is {open_slopes}/{total_slopes} slopes open.\n \n"
                    f"That is {slope_ratio}% of all slopes.\n \n"
                    f"There is {open_lifts}/{total_lifts} lifts open.\n \n"
                    f"That is {lift_ratio}% of all lifts\n ")
    msg["Subject"] = 'Hemsedal'
    msg['From'] = 'gustavhjalmarsson139@gmail.com'
    msg['To'] = 'gustav.hjalmarsson1@outlook.com'

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

def main(df):
    #Get the html data
    url = f'https://www.skistar.com/sv/vara-skidorter/hemsedal/vinter-i-hemsedal/vader-och-backar/?fo=88970'
    response = requests.get(url)

    soup = BeautifulSoup(response.text, "lxml")

    slopes_lifts = soup.find_all("div", class_="lpv-list__header")
    cleaned_text = [tag.get_text(strip=True) for tag in slopes_lifts]

    #Get the open and total lifts
    def get_lifts(cleaned_text):
        lifts = cleaned_text[0]

        open_lifts, total_lifts = lifts.split('av', 1)
        
        total_lifts = re.sub(r'[^0-9]', '', total_lifts)
        open_lifts = re.sub(r'[^0-9]', '', open_lifts)

        open_lifts = open_lifts.replace(" ", "")
        total_lifts = total_lifts.replace(" ", "")

        lift_ratio = int(open_lifts) / int(total_lifts) * 100

        return open_lifts, total_lifts, round(lift_ratio, 0)

    #Get the open and total slopes
    def get_slopes(cleaned_text):

        slopes = cleaned_text[1]

        open_slopes, total_slopes = slopes.split('av', 1)

        total_slopes = re.sub(r'[^0-9]', '', total_slopes) 
        open_slopes = re.sub(r'[^0-9]', '', open_slopes) 

        total_slopes = total_slopes.replace(" ", "")
        open_slopes = open_slopes.replace(" ", "")

        slope_ratio = int(open_slopes) / int(total_slopes) * 100

        return open_slopes, total_slopes, round(slope_ratio)
    
    Today = date.today()

    Open_Slopes, Total_Slopes, Slope_Ratio = get_slopes(cleaned_text)
    Open_Lifts, Total_Lifts, Lift_Ratio = get_lifts(cleaned_text)

    Hemsedal = 'Hemsedal'

    df.loc[len(df)] = [Today, Open_Slopes, Total_Slopes, Slope_Ratio, Open_Lifts, Total_Lifts, Lift_Ratio, Hemsedal]
    df_row = df.tail(1)
    df_row.to_csv("data.csv", mode="a",header=not os.path.exists("data.csv"), index=False)
    print(df)
    send_email(Total_Slopes, Open_Slopes, Slope_Ratio, Total_Lifts, Open_Lifts, Lift_Ratio)

main(df)