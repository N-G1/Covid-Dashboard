from flask import *
from covid_data_handler import *
from covid_news_handling import *
from datetime import datetime, timedelta
import json, globals, logging

logging.getLogger().setLevel(logging.INFO)

globals.info = covid_API_request()
globals.articles = update_news()
globals.current_update_list = []            #initialise global variables and logger
globals.stored_events = {"title": "title",
                         "event": "event",
                         "type": "type"}

config_file = json.loads(open("config.json").read())                                        #store a covid api request for the nation which allows hospital cases and later
national_info = covid_API_request(config_file["nation"],config_file["location_type_N"])     #7 day infection rate to be displayed

info_updates = []
message_content = { "content": "content",
                    "title": "title" }

app = Flask(__name__)
@app.route('/index')
def main():
    repeat = False
    l_7day_infections = 0
    n_7day_infections = 0       #allows for new 7 day infection rate to be calculated each time the page is refreshed in the event of an update
    run_covid_update()          #checks to see if any scheduled updates need to be executed
    run_news_update()

    if "notif" in request.args:
        title = request.args.get("notif")   #checks to see if an article has been deleted and calls delete_selected_article if it has
        delete_selected_article(title)
        update_news()

    if "repeating" in request.args:
       repeat == True                   #checks to see if user wants update entered to be repeated and is passed to schedule updates functions 
    
    if "update" in request.args:
        converted_time = datetime.strptime(request.args["update"], "%H:%M")
        converted_time
        current_time = datetime.now()

        converted_seconds = converted_time.second + converted_time.minute*60 + converted_time.hour*3600     #calculates the time difference between current
        current_seconds = current_time.second + current_time.minute*60 + current_time.hour*3600             #time and time that was entered into update
        difference = converted_seconds - current_seconds                                                    
        if difference < 0:                                  #if the difference is <0 it means that the time entered is for the following day
            difference += 86400 
            logging.info("[" + datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] : "+ 
                 "Date stored is for the following day")
        
    if "covid-data" in request.args:
        message_content["title"] = request.args["two"]                              #puts title and content of notification for update into a dictionary and appends it to the 
        message_content["content"] = "Covid update at: " + request.args["update"]   #list of displayed updates 
        info_updates.append(message_content.copy())
        schedule_covid_updates(difference,request.args["two"], repeat)              #passes required info to schedule function

    if "news" in request.args:
        message_content["title"] = request.args["two"]                              
        message_content["content"] = "News update at: " + request.args["update"]    #similar to above function 
        info_updates.append(message_content.copy())
        schedule_news_updates(difference,request.args["two"], repeat)

    if "update_item" in request.args:

        for value in globals.current_update_list:
            if value["title"] == request.args["update_item"]:  #performs check to loop through list of stored updates against the title of the 
                if value["type"] == "news":                    #removed update and in the event they are the same passes event to schedule remove functions
                    news_sched_remove(value["content"])
                else:
                    covid_sched_remove(value["content"])
                for i in range(len(info_updates)):
                        if info_updates[i - 1]["title"] == request.args["update_item"]:     #removes update from both list of scheduled update and the list 
                            del info_updates[i - 1]                                         #containing the notification title and content
                            del globals.current_update_list[i - 1]


    for x in range(0,7):
        l_7day_infections += globals.info[x]["newCasesByPublishDate"]           #calculates 7 day infection rate locally and nationally 
        n_7day_infections += national_info[x]["newCasesByPublishDate"]


    return render_template(
    "index.html",
    image="covid.jpg",
    updates = info_updates,
    title="Covid Dashboard",
    local_7day_infections=l_7day_infections,
    nation_location=national_info[0]["areaName"],
    national_7day_infections=n_7day_infections,
    location=globals.info[0]["areaName"],
    deaths_total="Total Deaths: "+ str(national_info[1]["cumDeaths28DaysByDeathDate"]),
    hospital_cases="Hospital Cases: " + str(national_info[0]["hospitalCases"]),
    news_articles=globals.articles)

if __name__ == "__main__":
    app.run()
