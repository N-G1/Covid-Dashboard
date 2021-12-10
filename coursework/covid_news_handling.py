import requests, json, sched, time, logging, sys, globals
from datetime import datetime 
global updated_articles

s = sched.scheduler(time.time, time.sleep)
config_file = json.loads(open("config.json").read())            #initialise scheduler, config file and logging file
logging.basicConfig(filename ="sys.log", filemode="a+")

def news_API_request(covid_terms=config_file["covid_terms"]):
    try:
        url = ("https://newsapi.org/v2/everything?qInTitle=" + 
               covid_terms + "&apiKey=" + config_file["api_key"] + config_file["URL_filters"])    #attempts to call news api using api key, covid terms and filters 
        req = (requests.get(url).json())                                                          #stored in config file, in the event of an exception prints error to config file
    except:
        logging.fatal("[" + datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] : "
                      + "Invalid API key, covid terms or url filters.")
        sys.exit(1)
   
    return req["articles"]

globals.articles = news_API_request()                                               #for the most part this section of the code works and does 
def update_news():                                                                  #store deleted articles however produces a strange error that
    for article in globals.articles:                                                #when the code is ran for the first time will display all                                
        with open(config_file["deleted_articles"], "r") as file:                    #articles including deleted but once a single article is removed
            for line in file:                                                       #from the notifications on the right it will update and remove all
                line = line.strip()                                                 #articles that shouldn't of been displayed, however works fine for                                 
                if article["title"] == line:                                        #refreshing and using the interface etc.
                    if article["title"] not in file:
                        globals.articles.remove(article)                            #calls news api and checks the article titles against a text file of 
                    else:                                                           #news titles that have been removed by the user and doesnt display them
                        globals.articles.remove(article)
                        logging.warning("[" + datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] : " 
                                        + "Article title removed is duplicate, code will still function correctly")
    file.close()
    return globals.articles

def delete_selected_article(title):
    del_articles = open(config_file["deleted_articles"], "a+")          #opens deleted articles file stored in config file and writes the title of the article
    del_articles.write(title + "\n")                                    #removed from display to the file which is then compared in the update news function and
    update_news()                                                       #doesn't display them
    del_articles.close()

def schedule_news_updates(update_interval, update_name, repeat = False):
    try:                                                                #checks to see if the title of the update just entered matches the name of an update already
        for value in globals.current_update_list:                       #stored and informs via the logging file that it will cause all updates with this name to be removed  
             if value["title"] == update_name:                          #if one is removed       
                logging.warning("[" + datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] : "+ 
                                "Update name |{}| matches name already stored in update list, will cause all updates with this name to be deleted if update is cleared".format(update_name))

        last_event = s.enter(update_interval,1,update_variable)                                 #enters the newly scheduled update into a list of already scheduled updates
        globals.stored_events = {"title": update_name, "content": last_event, "type": "news"}   #which allows for them to be later removed in the event the notification is deleted
        globals.current_update_list.append(globals.stored_events.copy())
        logging.info("[" + datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] : "+
                        "News update was entered into queue")
        if repeat == True:
            s.enter(update_interval, 1, schedule_news_updates,( update_interval, update_name))
        run_news_update()
    except Exception as error:
        logging.fatal("[" + datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] : "+ str(error))

def update_variable():
    globals.articles = news_API_request()           #once the scheduled update time is reached calls this function to update the list of articles
    globals.articles = update_news()
    logging.info("[" + datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] : "+ 
                 "News update was carried out")

def run_news_update():
    s.run(blocking = False)                         #periodically runs this function when the page is refreshed to check if update time has been met
    logging.info("[" + datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] : "+ 
                 "Run news updates was called")

def news_sched_remove(content):
    try:
        s.cancel(content)                               #called in main function to remove event from scheduler    
        logging.info("[" + datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] : "+ 
                     "News update was removed")
    except ValueError:
        logging.info("[" + datetime.now().strftime("%d.%b %Y %H:%M:%S") + "] : "+ 
                     "News update removed has been completed")
