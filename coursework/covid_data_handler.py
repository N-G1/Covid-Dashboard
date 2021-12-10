import uk_covid19, sched, time, globals, json, logging
from datetime import datetime 

covid_s = sched.scheduler(time.time, time.sleep)
config_file = json.loads(open("config.json").read())        #initialise scheduler, config file and logging file
logging.basicConfig(filename ="sys.log", filemode="a+")

def parse_csv_data(filename):
   csv_filename = open(filename, "r") 
   return csv_filename.readlines()          #returns string for list of rows within the csv file
   csv_filename.close()

def process_covid_csv_data():
    covid_csv_data = parse_csv_data("nation_2021-10-28.csv")

    last7days_cases = 0
    for x in range(2,9):
        cinfo = (covid_csv_data[x + 1].strip()).split(",")      #returns current hospital cases, deaths and last 7 day cases from csv file
        cases = int(cinfo[6])
        last7days_cases += cases

    hospital_cases = (covid_csv_data[1].strip()).split(",")
    current_hospital_cases = hospital_cases[5]
    deaths = (covid_csv_data[14].strip()).split(",")
    total_deaths = deaths[4]

    return last7days_cases, current_hospital_cases, total_deaths

def covid_API_request(location=config_file["location"], location_type = config_file["location_type_L"]):
    filters = ["areaName=" + location,
               "areaType=" + location_type,]         
    dict = {
        "date": "date",
        "areaName": "areaName",         #calls covid api and stores information in dictionary
        "areaCode": "areaCode",
        "cumDeaths28DaysByDeathDate": "cumDeaths28DaysByDeathDate",
        "newCasesByPublishDate": "newCasesByPublishDate",
        "hospitalCases" : "hospitalCases"
      }
    api = uk_covid19.Cov19API(filters=filters,structure=dict)
    data = api.get_json()
    return data["data"]

def schedule_covid_updates(update_interval, update_name, repeat = False):
    try:
        for value in globals.current_update_list:                                               
             if value["title"] == update_name:                                                  #very similar to news scheduler, comments within that file explain functionality
                logging.warning("[" + datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] : "+    #am aware this could've been done within its own file to prevent copying of code 
                                "Update name |{}| matches name already stored in update list, will cause all updates with this name to be deleted if update is cleared".format(update_name))

        last_event = covid_s.enter(update_interval,1,update_variable)
        globals.stored_events = {"title": update_name, "content": last_event, "type": "covid"}
        globals.current_update_list.append(globals.stored_events.copy())
        logging.info("[" + datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] : "+
                        "Covid update was entered into queue")
        if repeat == True:
            covid_s.enter(update_interval, 1, schedule_covid_updates,( update_interval, update_name))
        run_covid_update()
    except Exception as error:
        logging.fatal("[" + datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] : "+ str(error))

def update_variable():
    globals.info = covid_API_request()                      #updates required variables here
    logging.info("[" + datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] : "+ 
                 "Covid update was carried out")

def run_covid_update():
    covid_s.run(blocking = False)                           #periodically called to check if time for scheduled update has been met 
    logging.info("[" + datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] : "+ 
                 "Run covid updates was called")

def covid_sched_remove(content):
    try:
        covid_s.cancel(content)                                 #called in main function to remove event from scheduler   
        logging.info("[" + datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] : "+ 
                     "Covid update was removed")
    except ValueError:
        logging.info("[" + datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] : "+ 
                     "Covid update removed has been completed")