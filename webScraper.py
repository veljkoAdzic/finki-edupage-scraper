from selenium import webdriver
import json
import time
from storage import storeData
def scrapeForData():
    URL = "https://finki.edupage.org/timetable/"
    TARGET_URL = URL + "server/regulartt.js?__func=regularttGetData"

    # no gui
    option = webdriver.ChromeOptions()
    option.add_argument("--headless=new")

    # # capture logs
    option.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    # launching webdriver
    driver = webdriver.Chrome(options=option)

    # open website
    driver.get(URL)
    time.sleep(10)

    # Get db payload
    json_data = None
    logs = driver.get_log("performance")
    for entry in logs:
        log = log = json.loads(entry["message"])["message"]
        if log["method"] == "Network.responseReceived":
            res = log["params"]
            req_id = res["requestId"]
            url = res["response"]["url"]

            if TARGET_URL == url:
                try:
                    res_body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": req_id})
                    print(res_body["body"][:100])
                    json_data = res_body["body"]
                    break
                except Exception as e:
                    print("[ERROR]: unable to fetch body |\n", e)

    # close web driver
    driver.quit()
    
    if json_data:
        storeData(json_data)

# if __name__ == "__main__":
#     scrapeForData()