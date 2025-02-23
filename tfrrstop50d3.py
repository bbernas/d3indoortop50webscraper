import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import plotly as px
import os

#Fully Works: Weight Throw, Shot Put, Pole Vault , High Jump, Triple Jump, Long Jump, Heptathlon, 60 Meters, 200 Meters, 400 Meters
#In Progress: 800 Meters, Mile, 3000 Meters, 5000 Meters, 4x400 Meters, Distance Medley Relay
#Not Working: 60 Hurdles
event = str (input("Enter the event you would like to know top 50 for D3 indoor: "))

def scrape_event():
    url = "https://tf.tfrrs.org/lists/4869/2024_2025_NCAA_Division_III_Indoor_Qualifying?gender=m"
    headers = {"User-Agent": "Chrome/91.0.4472.124"}  

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    event_headers = soup.find_all("h3")
    event_section = None

    for header in event_headers:
        if event in header.text: 
            event_section = header
            break

    table = event_section.find_next("table")

    rows = table.find_all("tr")
    data_list = []
    for row in rows:
        columns = row.find_all("td")
        if columns:
            data = [col.text.strip() for col in columns]
            data_list.append(data)

    with open("eventData.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Ranking", "Athlete", "Year", "School", "Mark","FeetMeet", "Meet" , "Date" , "Wind"])  
        writer.writerows(data_list) 

    print("Saved to eventData.csv") 

def plot_data():
    data = pd.read_csv('eventData.csv')
    data['Mark'] = data["Mark"].str.replace("m", "")
    data['Mark'] = data["Mark"].str.replace("#", "")
    data['Mark'] = data["Mark"].str.replace("@", "")
    data['Mark'] = data["Mark"].str.replace("(55)", "")
    
    if event in ["800 Meters", "Mile", "3000 Meters", "5000 Meters", "4x400 Meters", "Distance Medley Relay"]:
        data["Mark"] = pd.to_timedelta("00:" + data['Mark']).dt.total_seconds()
        fig = px.hist_frame(data, x='Athlete', y= "Mark", nbins=100)
        data_sorted = data.sort_values(by="Mark", ascending=False).reset_index(drop=True)
        data["color"] = "red"  
        top_20_marks = data_sorted["Mark"].iloc[:30].values  
        data.loc[data["Mark"].isin(top_20_marks), "color"] = "blue"
    
    if event in ["Weight Throw", "Shot Put", "Pole Vault", "High Jump", "Triple Jump", "Long Jump", "Heptathlon"]:
        fig = px.hist_frame(data, x='Athlete', y= "Mark", nbins=50)
        data_sorted = data.sort_values(by="Mark", ascending=False).reset_index(drop=True)
        data["color"] = "blue"  
        top_20_marks = data_sorted["Mark"].iloc[:20].values  
        data.loc[data["Mark"].isin(top_20_marks), "color"] = "red"
    if event in ["60 Meters", "60 Hurdles", "200 Meters", "400 Meters"]:
        fig = px.hist_frame(data, x='Athlete', y= "Mark", nbins=50)
        data_sorted = data.sort_values(by="Mark", ascending=False).reset_index(drop=True)
        data["color"] = "red"  
        top_20_marks = data_sorted["Mark"].iloc[:30].values  
        data.loc[data["Mark"].isin(top_20_marks), "color"] = "blue"

    fig = px.hist_frame(data, x="Athlete",y = 'Mark', nbins=30, color="color", color_discrete_map={"blue": "blue", "red": "red"}) #histogram with top 20 highlighted in red
    fig.update_layout(title=" Performance - Top 20 National Qualifiers Highlighted in Red", xaxis_title="Mark", yaxis_title="Count")
    fig.update_yaxes(range=[float(data["Mark"].min()) - .5, float(data["Mark"].max()) + .5])

    os.remove("eventData.csv") 
    print("eventData.csv removed")
    fig.write_html("/docs/weight.html")
    fig.show()

if __name__ == "__main__":
    scrape_event()
    plot_data()
