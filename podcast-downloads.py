import re
import httpagentparser
import sys

args = str(sys.argv)

logFile = sys.argv.pop();

pattern = re.compile(r'^([0-9.]+)\s([\w.-]+)\s([\w.-]+)\s(\[[^\[\]]+\])\s"((?:[^"]|\")+)"\s(\d{3})\s(\d+|-)\s"((?:[^"]|\")+)"\s"((?:[^"]|\")+)"$')
                
mp3_downloads = {}

lines = [line.strip() for line in open(logFile)]
for line in lines:
    if (line):
        #print line;
        match= pattern.finditer(line)
        for m in match: 
           
           useragent = m.group(9)
           request = m.group(5)
           ref = m.group(7)
           if ( re.search("mp3", request, re.I)):
               
               if (re.search("itunes", useragent, re.I) ):
                   if not "iTunes" in mp3_downloads:
                       mp3_downloads["iTunes"] = 1;
                   else:
                       mp3_downloads["iTunes"] += 1;
                 
               elif (re.search("googlebot", useragent, re.I) or re.search("bingbot", useragent, re.I) or re.search("FAST Enterprise Crawler", useragent, re.I)):
                     if not "googlebot, bingbot, etc" in mp3_downloads:
                       mp3_downloads["googlebot, bingbot, etc"] = 1;
                     else:
                       mp3_downloads["googlebot, bingbot, etc"] += 1;
                     
               else: 
                   agent = httpagentparser.simple_detect(useragent);
                   os = agent[0];
                   browser = agent[1];
                   if re.search("unknown", os, re.I):
                       simplestring = browser;
                   else:
                       simplestring = os;                         
                   if not simplestring in mp3_downloads:
                       mp3_downloads[simplestring] = 1;
                   else:
                       mp3_downloads[simplestring] += 1;                
                       
                
for agent, count in sorted(mp3_downloads.items()):
    print agent, ":", count;
                    
           
           