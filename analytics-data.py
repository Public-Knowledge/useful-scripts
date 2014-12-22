import sys
import argparse
import json
import requests
import json
import time
from datetime import datetime, timedelta
from pprint import pprint
from tabulate import tabulate

start_date = "";
end_date = "";

json_data=open('config.json');
configData = json.load(json_data);    
json_data.close();  
client_id = configData["client_id"];
client_secret = configData["client_secret"];
gID = configData["google_analytics_id"];

      

    
def checkForNewAuthorization(device_code):

    headers = { 'Content-Type' : 'application/x-www-form-urlencoded' };
    url = 'https://accounts.google.com/o/oauth2/token';
    values = {'client_id' : client_id,
              'grant_type' : "http://oauth.net/grant_type/device/1.0",
              'client_secret' :  client_secret, 
              'code' : device_code }

    r = requests.post(url, headers=headers, data=values);
    response = r.json();
    
    if  response.has_key("access_token"):
        storeAuthorization(response);
        return response;
    else:
        if response.has_key("error"):
            print response["error"];
        return {};
 
def generateAuthCodeRequest():

    headers = { 'Content-Type' : 'application/x-www-form-urlencoded' };
    url = 'https://accounts.google.com/o/oauth2/device/code';
    values = {'client_id' : client_id,
          'scope' : 'email profile https://www.googleapis.com/auth/analytics.readonly' }

    r = requests.post(url, params=values)
    response = r.json();
    print "Open", response['verification_url'], "in a web browser and enter", response['user_code'];
    print "After that, run again with -a",  response['device_code'];
    authenticated = False;
    time.sleep(5);
    print "checking if authenticated yet";
    while not(authenticated):
        authResponse = checkForNewAuthorization(response['device_code']);
        if  authResponse.has_key("access_token"):
            authenticated = True;
            print "User authentication now stored."
        else:
            time.sleep(5);
    
    return authResponse;

def storeAuthorization(authTokens):
    with open('auth.txt', 'w') as outfile:
        json.dump(authTokens, outfile);
    
      
         
def getAuthorizationFromFile():
      json_data=open('auth.txt');
      data = json.load(json_data);
      json_data.close();  
      return data; 
      
      
def fetchPageViews(authTokens, start_date, end_date):  
    values = {'ids' : gID,
              'start-date' : start_date,
              'end-date' : end_date,
              'metrics' : 'ga:sessions,ga:bounces,ga:avgSessionDuration'};
    analyticsResponse = fetchData(authTokens, values);              
    print "Data for", analyticsResponse["profileInfo"]["profileName"], "for date range", start_date, "to", end_date;
    for metric in analyticsResponse["totalsForAllResults"]:
            print metric, ":", analyticsResponse["totalsForAllResults"][metric];
    print "   " * 20;        

def fetchDailyTraffic(authTokens, start_date, end_date):
    
    #daily visits/percentage of new visits for dates
    values = {'ids' : gID,
              'dimensions' : "ga:date",
              'metrics' : 'ga:visits,ga:visitors,ga:percentNewVisits, ga:pageviews',
              'start-date' : start_date,
               'end-date' : end_date};
    analyticsResponse = fetchData(authTokens, values);   
       
    columnHeaders = [];
    for entry in analyticsResponse["columnHeaders"]:
        columnHeaders.append(entry["name"]);                  
    print tabulate(analyticsResponse["rows"], headers=columnHeaders);
    print "   " * 20;
            
def fetchKeywordReport(authTokens, start_date, end_date, count):
         
    values = {'ids' : gID,
              'dimensions' : "ga:keyword",
              'metrics' : 'ga:organicSearches',
              'max-results' : count,
              'start-date' : start_date,
              'end-date' : end_date};
              
    analyticsResponse = fetchData(authTokens, values);  
    
    print analyticsResponse["profileInfo"]["profileName"], "keywords for",  analyticsResponse["query"]["start-date"], "to", analyticsResponse["query"]["end-date"];
    columnHeaders = [];
    for entry in analyticsResponse["columnHeaders"]: 
        columnHeaders.append(entry["name"]);              
    print tabulate(analyticsResponse["rows"], headers=columnHeaders);
    print "   " * 20;
        
def fetchMobileReport(authTokens, start_date, end_date, count):
       
    values = {'ids' : gID,
                  'dimensions' : "ga:source,ga:medium",
                  'metrics' : 'ga:sessions,ga:pageviews,ga:sessionDuration,ga:bounces',
                  'max-results' : count,
                  'start-date' : start_date,
                  'end-date' : end_date};
        
    analyticsResponse = fetchData(authTokens, values)  
    columnHeaders = [];
    print analyticsResponse["profileInfo"]["profileName"], "Mobile Traffic for",  analyticsResponse["query"]["start-date"], "to", analyticsResponse["query"]["end-date"];
   
    for entry in analyticsResponse["columnHeaders"]:    
        columnHeaders.append(entry["name"]);
    print tabulate(analyticsResponse["rows"], headers=columnHeaders);
    print "   " * 20;
 
def fetchUserReport(authTokens, start_date, end_date):
    
    values = {'ids' : gID,
                  'dimensions' : "ga:userType",
                  'metrics' : 'ga:sessions,ga:pageviews,ga:sessionDuration',
                  'start-date' : start_date,
                  'end-date' : end_date};
        
    analyticsResponse = fetchData(authTokens, values)  
    columnHeaders = [];
    print analyticsResponse["profileInfo"]["profileName"], "New v Returning Users for",  analyticsResponse["query"]["start-date"], "to", analyticsResponse["query"]["end-date"];
   
    for entry in analyticsResponse["columnHeaders"]:    
        columnHeaders.append(entry["name"]);
    print tabulate(analyticsResponse["rows"], headers=columnHeaders);
    print "   " * 20; 
 
def fetchReferralReport(authTokens, start_date, end_date, count):
     
    values = {'ids' : gID,
                  'dimensions' : "ga:fullReferrer",
                  'metrics' : 'ga:visits,ga:visitors,ga:percentNewVisits, ga:pageviews',
                  'max-results' : count,
                  'start-date' : start_date,
                  'end-date' : end_date};
        
    analyticsResponse = fetchData(authTokens, values)  
    columnHeaders = [];
    print analyticsResponse["profileInfo"]["profileName"], "Top Referrers for",  analyticsResponse["query"]["start-date"], "to", analyticsResponse["query"]["end-date"];
   
    for entry in analyticsResponse["columnHeaders"]:    
        columnHeaders.append(entry["name"]);
    print tabulate(analyticsResponse["rows"], headers=columnHeaders);
    print "   " * 20;
    
    
#    
def fetchTrafficSourcesReport(authTokens, start_date, end_date, count):
     
    values = {'ids' : configData["google_analytics_id"],
                  'dimensions' : "ga:source,ga:medium",
                  'metrics' : 'ga:sessions,ga:pageviews,ga:sessionDuration,ga:exits',
                  'sort' : '-ga:sessions',
                  'max-results' : count,
                  'start-date' : start_date,
                  'end-date' : end_date};
      
    analyticsResponse = fetchData(authTokens, values)  
    columnHeaders = [];
    print analyticsResponse["profileInfo"]["profileName"], "Traffic Sources for",  analyticsResponse["query"]["start-date"], "to", analyticsResponse["query"]["end-date"];
   
    for entry in analyticsResponse["columnHeaders"]:    
        columnHeaders.append(entry["name"]);
    print tabulate(analyticsResponse["rows"], headers=columnHeaders);
    print "   " * 20;        
     
def fetchBrowserReport(authTokens, start_date, end_date, count):
    #referrals?    
    values = {'ids' : gID,
                  'dimensions' : "ga:operatingSystem,ga:operatingSystemVersion,ga:browser,ga:browserVersion",
                  'metrics' : 'ga:sessions,ga:percentNewVisits, ga:pageviews',
                  'sort' : '-ga:sessions',
                  'max-results' : count,
                  'start-date' : start_date,
                  'end-date' : end_date};
        
    analyticsResponse = fetchData(authTokens, values)  
    columnHeaders = [];
    print analyticsResponse["profileInfo"]["profileName"], "Browser & OS for",  analyticsResponse["query"]["start-date"], "to", analyticsResponse["query"]["end-date"];
   
    for entry in analyticsResponse["columnHeaders"]:    
        columnHeaders.append(entry["name"]);
    print tabulate(analyticsResponse["rows"], headers=columnHeaders);
    print "   " * 20;               
        
def fetchTOSReport  (authTokens, start_date, end_date):
    values = {'ids' : gID,
              'metrics' : 'ga:sessions,ga:sessionDuration',
              'start-date' : start_date,
              'end-date' : end_date};
        
    analyticsResponse = fetchData(authTokens, values)  
   
    columnHeaders = [];
    print analyticsResponse["profileInfo"]["profileName"], "Time on Site for",  analyticsResponse["query"]["start-date"], "to", analyticsResponse["query"]["end-date"];
   
    for entry in analyticsResponse["columnHeaders"]:    
        columnHeaders.append(entry["name"]);
    print tabulate(analyticsResponse["rows"], headers=columnHeaders);
    print "   " * 20;        
  
def fetchReferringSitesReport(authTokens, start_date, end_date, count):
    #referrals?    
    values = {'ids' : gID,
                  'dimensions' : "ga:source",
                  'metrics' : 'ga:pageviews,ga:sessionDuration,ga:exits',
                  'filters' : 'ga:medium==referral',
                  'sort' : '-ga:pageviews',
                  'max-results' : count,
                  'start-date' : start_date,
                  'end-date' : end_date};
        
    analyticsResponse = fetchData(authTokens, values)  
    columnHeaders = [];
    print analyticsResponse["profileInfo"]["profileName"], "Referring Sites for",  analyticsResponse["query"]["start-date"], "to", analyticsResponse["query"]["end-date"];
   
    for entry in analyticsResponse["columnHeaders"]:    
        columnHeaders.append(entry["name"]);
    print tabulate(analyticsResponse["rows"], headers=columnHeaders);
    print "   " * 20;               
        
def fetchSearchEnginesOrganicReport(authTokens, start_date, end_date, count):
    #referrals?    
    values = {'ids' : gID,
                  'dimensions' : "ga:source",
                  'metrics' : 'ga:pageviews,ga:sessionDuration,ga:exits',
                  'filters' : 'ga:medium==organic',
                  'sort' : '-ga:pageviews',
                  'max-results' : count,
                  'start-date' : start_date,
                  'end-date' : end_date};
        
    analyticsResponse = fetchData(authTokens, values)  
    columnHeaders = [];
    print analyticsResponse["profileInfo"]["profileName"], "Search Engines Organic Traffic Report for",  analyticsResponse["query"]["start-date"], "to", analyticsResponse["query"]["end-date"];
   
    for entry in analyticsResponse["columnHeaders"]:    
        columnHeaders.append(entry["name"]);
    print tabulate(analyticsResponse["rows"], headers=columnHeaders);
    print "   " * 20;   
 
def fetchSearchEnginesReport(authTokens, start_date, end_date, count):
    #referrals?    
    values = {'ids' : gID,
                  'dimensions' : "ga:source",
                  'metrics' : 'ga:pageviews,ga:sessionDuration,ga:exits',
                  'filters' : 'ga:medium==cpa,ga:medium==cpc,ga:medium==cpm,ga:medium==cpp,ga:medium==cpv,ga:medium==organic,ga:medium==ppc',
                  'sort' : '-ga:pageviews',
                  'max-results' : count,
                  'start-date' : start_date,
                  'end-date' : end_date};
        
    analyticsResponse = fetchData(authTokens, values)  
    columnHeaders = [];
    print analyticsResponse["profileInfo"]["profileName"], "Search Engines Report for",  analyticsResponse["query"]["start-date"], "to", analyticsResponse["query"]["end-date"];
   
    for entry in analyticsResponse["columnHeaders"]:    
        columnHeaders.append(entry["name"]);
    print tabulate(analyticsResponse["rows"], headers=columnHeaders);
    print "   " * 20; 
 
def fetchTopContentReport(authTokens, start_date, end_date, count):
    #referrals?    
    values = {'ids' : gID,
                  'dimensions' : 'ga:pagePath',
                  'metrics' : 'ga:pageviews,ga:uniquePageviews,ga:timeOnPage,ga:bounces,ga:entrances,ga:exits',
                  'sort' : '-ga:pageviews',
                  'max-results' : count,
                  'start-date' : start_date,
                  'end-date' : end_date};
        
    analyticsResponse = fetchData(authTokens, values)  
    columnHeaders = [];
    print analyticsResponse["profileInfo"]["profileName"], "Top Content Report for",  analyticsResponse["query"]["start-date"], "to", analyticsResponse["query"]["end-date"];
   
    for entry in analyticsResponse["columnHeaders"]:    
        columnHeaders.append(entry["name"]);
    print tabulate(analyticsResponse["rows"], headers=columnHeaders);
    print "   " * 20;  
    
def fetchTopLandingPageReport(authTokens, start_date, end_date, count):
    #referrals?    
    values = {'ids' : gID,
                  'dimensions' : 'ga:landingPagePath',
                  'metrics' : 'ga:entrances,ga:bounces',
                  'sort' : '-ga:entrances',
                  'max-results' : count,
                  'start-date' : start_date,
                  'end-date' : end_date};
        
    analyticsResponse = fetchData(authTokens, values)  
    columnHeaders = [];
    print analyticsResponse["profileInfo"]["profileName"], "Top Landing Page Report for",  analyticsResponse["query"]["start-date"], "to", analyticsResponse["query"]["end-date"];
   
    for entry in analyticsResponse["columnHeaders"]:    
        columnHeaders.append(entry["name"]);
    print tabulate(analyticsResponse["rows"], headers=columnHeaders);
    print "   " * 20;
    
    

def fetchWeeklyEmailOverviewReport(authTokens, start_date, end_date):
    #referrals?    
    values = {'ids' : gID,
                  
                  'metrics' : 'ga:pageviewsPerSession,ga:users,ga:bounceRate,ga:sessions,ga:uniquePageviews,ga:pageviews,ga:avgSessionDuration',
                  'start-date' : start_date,
                  'end-date' : end_date};
        
    analyticsResponse = fetchData(authTokens, values);
    
    columnHeaders = [];
    print analyticsResponse["profileInfo"]["profileName"], "Top Landing Page Report for",  analyticsResponse["query"]["start-date"], "to", analyticsResponse["query"]["end-date"];
   
    for entry in analyticsResponse["columnHeaders"]:    
        columnHeaders.append(entry["name"]);
    print tabulate(analyticsResponse["rows"], headers=columnHeaders);
    print "   " * 20;
    
     
        
def fetchData(authTokens, values):
    token = 'Bearer ' + authTokens["access_token"];
    headers = {'Authorization':  token};
    url = "https://www.googleapis.com/analytics/v3/data/ga";
    r = requests.get(url, headers=headers, params=values);
    analyticsResponse = r.json();
    if  analyticsResponse.has_key("error"):
            if "Invalid Credentials" in analyticsResponse["error"]["message"]:
                print "   " * 20; 
                print "   " * 20; 
                print "Please refresh your credentials by re-running with --begin (or -b) option";
                print "   " * 20; 
                print "   " * 20; 
                return;
    return analyticsResponse;     
        
         
        
def getDates():
    if args.startDate:
         
        start_date = args.startDate;
            
    if args.endDate:
         
        end_date = args.endDate;
    else:
         
        now = datetime.now();
        yesterday = datetime.now() + timedelta(days = -1);
        
        start_date = str(yesterday.year) + "-" + str(yesterday.month) + "-" + str(yesterday.day);
        end_date = str(now.year) + "-" + str(now.month) + "-" + str(now.day);
    return (start_date, end_date);         


parser = argparse.ArgumentParser(description='Generate Simple Analytics Report')

parser.add_argument('-b','--begin', action='store_true',
                    help='Call with begin if you need to generate an authorization URL and Token as your first step') # boolean arg

parser.add_argument('-r','--report', action='store_true',
                    help='Call with report to generate a summary traffic report. You can also set a start and end date') # boolean arg

parser.add_argument('-k','--keywordreport', action='store_true',
                    help='Call with keywordreport to generate a keyword report. You can also set a start and end date') # boolean arg

parser.add_argument('-rf','--referralreport', action='store_true',
                    help='Call with referralreport to generate a referral traffic report. You can also set a start and end date') # boolean arg
parser.add_argument('-m','--mobilereport', action='store_true',
                    help='Call with mobilereport to generate a mobile traffic report. You can also set a start and end date') # boolean arg
parser.add_argument('-u','--userreport', action='store_true',
                    help='Call with userreport to generate number of new sessions vs returning sessions. You can also set a start and end date') # boolean arg
parser.add_argument('-bo','--browserreport', action='store_true',
                    help='Call with browserreport to generate breakdown of sessions by  Operating System & web browser. You can also set a start and end date') # boolean arg

parser.add_argument('-tos','--timeonsitereport', action='store_true',
                    help='Call with timeonsitereport to generate number of sessions and total time on site. You can also set a start and end date') # boolean arg

parser.add_argument('-tr','--alltrafficsourcesreport', action='store_true',
                    help='Call with alltrafficsourcesreport to generate site usage data broken down by source and medium, sorted by sessions in descending order. You can also set a start and end date') # boolean arg
parser.add_argument('-rs','--referringsitesreport', action='store_true',
                    help='Call with referringsitesreport to generate list of domains and how many sessions each referred to your site, sorted by pageviews in descending order. You can also set a start and end date') # boolean arg

parser.add_argument('-se','--searchenginesreport', action='store_true',
                    help='Call with searchenginesreport to generate list of domains and how many sessions each referred to your site, sorted by pageviews in descending order. You can also set a start and end date') # boolean arg
parser.add_argument('-seo','--searchenginesorganicreport', action='store_true',
                    help='Call with searchenginesorganicreport to generate site usage data for organic traffic by search engine, sorted by pageviews in descending order. You can also set a start and end date') # boolean arg
parser.add_argument('-tc','--topcontentreport', action='store_true',
                    help='Call with topcontentreport to generate most popular content, sorted by most pageviews. You can also set a start and end date') # boolean arg
parser.add_argument('-tlp','--toplandingpagereport', action='store_true',
                    help='Call with toplandingpagereport to generate most popular landing page, sorted by most pageviews. You can also set a start and end date') # boolean arg
parser.add_argument('-week','--weeklyemailreport', action='store_true',
                    help='Call with weeklyemailreport to generate data for email report. You can also set a start and end date') # boolean arg




parser.add_argument('-s','--startDate', 
                    help='Call with startDate and a date in format YYYY-MM-DD') # boolean arg

parser.add_argument('-e','--endDate', 
                    help='Call with startDate and a date in format YYYY-MM-DD') # boolean arg



args = parser.parse_args();


if args.begin:                       
     
    generateAuthCodeRequest();
    

if args.report:
    (start_date, end_date) = getDates();    
    authTokens = getAuthorizationFromFile();
    fetchPageViews(authTokens, start_date, end_date);
    fetchDailyTraffic(authTokens, start_date, end_date);
    
elif args.keywordreport:    
     (start_date, end_date) = getDates();
     authTokens = getAuthorizationFromFile();
     fetchKeywordReport(authTokens, start_date, end_date, 100);
    
elif args.referralreport:
     (start_date, end_date) = getDates();
     authTokens = getAuthorizationFromFile();
     fetchReferralReport(authTokens, start_date, end_date, 100);

elif args.mobilereport:
     (start_date, end_date) = getDates();
     authTokens = getAuthorizationFromFile();
     fetchMobileReport(authTokens, start_date, end_date, 100);
     
elif args.userreport:
     (start_date, end_date) = getDates();
     authTokens = getAuthorizationFromFile();
     fetchUserReport(authTokens, start_date, end_date);

elif args.browserreport:         
     (start_date, end_date) = getDates();
     authTokens = getAuthorizationFromFile();
     fetchBrowserReport(authTokens, start_date, end_date, 100);
     
elif args.timeonsitereport:
     (start_date, end_date) = getDates();
     authTokens = getAuthorizationFromFile();
     fetchTOSReport(authTokens, start_date, end_date);
     
elif args.alltrafficsourcesreport:
     (start_date, end_date) = getDates();
     authTokens = getAuthorizationFromFile();
     fetchTrafficSourcesReport(authTokens, start_date, end_date, 100);
     
elif args.referringsitesreport:
     (start_date, end_date) = getDates();
     authTokens = getAuthorizationFromFile();
     fetchReferringSitesReport(authTokens, start_date, end_date, 100);

elif args.searchenginesreport:         
     (start_date, end_date) = getDates();
     authTokens = getAuthorizationFromFile();
     fetchSearchEnginesReport(authTokens, start_date, end_date, 100);
     
elif args.searchenginesorganicreport:     
     (start_date, end_date) = getDates();
     authTokens = getAuthorizationFromFile();
     fetchSearchEnginesOrganicReport(authTokens, start_date, end_date, 100);

elif args.topcontentreport:     
     (start_date, end_date) = getDates();
     authTokens = getAuthorizationFromFile();
     fetchTopContentReport(authTokens, start_date, end_date, 100);
     
elif args.toplandingpagereport:
     (start_date, end_date) = getDates();
     authTokens = getAuthorizationFromFile();
     fetchTopLandingPageReport(authTokens, start_date, end_date, 100); 
     
elif args.weeklyemailreport:      
     (start_date, end_date) = getDates();
     authTokens = getAuthorizationFromFile();
     fetchWeeklyEmailOverviewReport(authTokens, start_date, end_date);
     fetchReferralReport(authTokens, start_date, end_date, 10);
     fetchTopLandingPageReport(authTokens, start_date, end_date, 10);
                  
else:
    parser.print_help()                 # or print help

    
