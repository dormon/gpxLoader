#!/usr/bin/python
#coding: utf-8

import string
import re
import sys
import os
import xml.dom.minidom
import urllib2
import string

user = "dormon"

gpsFileName="/media/"+user+"/GARMIN/Garmin/GPX/dormon.gpx"
visitedFileName = "/media/"+user+"/GARMIN/Garmin/geocache_visits.txt"


visitedFileText = open(visitedFileName).read().decode("utf-16")

#html text
mapText = open(sys.argv[1]).read()

allIcons=re.findall(r"<img src.*?class=\"leaflet-marker-icon.*?\".*?>",mapText)
#found caches True/False
foundCaches = map(lambda x:re.findall("MyFind.png",x)!=[],allIcons)
#names
cacheNames = map(lambda x:re.search("title=\"(.*?)\"",x).group(1),allIcons)
#(name,True/False)*
foundNames = dict(zip(cacheNames,foundCaches))

#sed "s/\">/\">\n/g" | grep "data-key" | sed "s/.*data-key=\"\(.*\)\">/\1/g" | sort | uniq

#<img src="./Geocaching _ Geocaching     Maps_files/MyFind.png" class="leaflet-marker-icon  leaflet-clickable leaflet-zoom-animated" title="Stará valašská II" style="margin-left: -10px; margin-top: -11px; width: 21px; height: 2    1px; transform: translate3d(-17px, 19px, 0px); z-index: 19;">

re.sub("\">","\">\n",mapText)
datakeys = re.findall("data-key=\"[A-Z0-9]*\"",mapText)
datalat = re.findall("data-lat=\"[0-9.]*\"",mapText)
datalng = re.findall("data-lng=\"[0-9.]*\"",mapText)
keys = map(lambda x:x[10:][:-1],datakeys)
lat = map(lambda x:x[10:][:-1],datalat)
lng = map(lambda x:x[10:][:-1],datalng)

waypoints = zip(keys,lat,lng)

#print waypoints

gpxNamesOnGPS = {}
gpxOnGPS = []

gpxCounter=0

if os.path.exists(gpsFileName):
  #load gpx file
  gpsFile = xml.dom.minidom.parse(open(gpsFileName,"r"))
  #gets wpts
  wpt = gpsFile.getElementsByTagName("wpt")
  for w in wpt:
    w.childNodes[3].setAttribute("id",str(gpxCounter))
    gpxOnGPS += [w]
    gpxNamesOnGPS[w.childNodes[1].childNodes[0].nodeValue]=w
    gpxCounter+=1

wptExample="""
<wpt lat="49.439133" lon="17.833233">
  <name>GC44444</name>
  <groundspeak:cache id="1" xmlns:groundspeak="http://www.groundspeak.com/cache/1/0">
    <groundspeak:name>name</groundspeak:name>
    <groundspeak:type>Traditional Cache</groundspeak:type>
    <groundspeak:container>Micro</groundspeak:container>
    <groundspeak:difficulty>2</groundspeak:difficulty>
    <groundspeak:terrain>1.5</groundspeak:terrain>
    <groundspeak:long_description html="True">jojojojo</groundspeak:long_description>
  </groundspeak:cache>
</wpt>
"""

starsToValue = {
  "stars1.gif"   : "1",
  "stars1_5.gif" : "1.5",
  "stars2.gif"   : "2",
  "stars2_5.gif" : "2.5",
  "stars3.gif"   : "3",
  "stars3_5.gif" : "3.5",
  "stars4.gif"   : "4",
  "stars4_5.gif" : "4.5",
  "stars5.gif"   : "5"
}

typeToValue = {
  "2"    : "Traditional Cache",
  "3"    : "Multi-Cache",
  "5"    : "Letterbox Hybrid",
  "6"    : "Event Cache",
  "8"    : "Mystery Cache",
  "137"  : "EarthCache",
  "1858" : "Wherigo Cache"
}

alreadyInside = gpxCounter

for w in waypoints:
  url = "http://www.geocaching.com/geocache/"+w[0]
  idname = w[0]
  name   = w[0]
  lat    = w[1]
  lon    = w[2]

  if re.search(idname,visitedFileText):
    print str(gpxCounter-alreadyInside+1)+" out of: "+str(len(waypoints))+" "+name+" - in visited file"
    gpxCounter+=1
    continue

  if not gpxNamesOnGPS.has_key(idname):
    newWpt = xml.dom.minidom.parseString(wptExample).getElementsByTagName("wpt")[0]
    #set lat
    newWpt.setAttribute("lat",lat)
    #set lon
    newWpt.setAttribute("lon",lon)
    #set idname
    newWpt.getElementsByTagName("name")[0].firstChild.nodeValue=idname
    #set id
    newWpt.getElementsByTagName("groundspeak:cache")[0].setAttribute("id",str(gpxCounter))
    #TODO download difficulty, terrain container description type
    response = urllib2.urlopen(url)
    html = response.read()

    name = re.findall("<span id=\"ctl00_ContentBody_CacheName\">.*?</span>",html)[0][39:][:-7]

    if foundNames.has_key(name):
        if foundNames[name]:
            print str(gpxCounter-alreadyInside+1)+" out of: "+str(len(waypoints))+" "+name+" - uz nalezena kes"
            gpxCounter+=1
            continue
    else:
        print name+" nema klic"

    printable = set(string.printable)
    name = filter(lambda x: x in printable, name)

    newWpt.getElementsByTagName("groundspeak:cache")[0].getElementsByTagName("groundspeak:name")[0].firstChild.nodeValue = name

    print str(gpxCounter-alreadyInside+1)+" out of: "+str(len(waypoints))+" "+name
    terrainText     = html[html.find("Terrain:"   ):][:1000]
    difficultyText  = html[html.find("Difficulty:"):][:1000]
    sizeText        = html[html.find("/images/icons/container/")+len("/images/icons/container/"):][:1000]
    typeText        = html[html.find("/images/WptTypes/"       )+len("/images/WptTypes/"       ):][:1000]
    hintText        = html[html.find("div_hint"   ):][:1000]
    hintText2       = hintText[hintText.find("WrapFix\">")+len("WrapFix\">"):hintText.find("</div>")]
    decryptText     = html[html.find("Decryption Key"):][:1000]
    decryptText2    = decryptText[decryptText.find("<br")+len("<br"):][:1000] 

    decryptTextA    = decryptText [decryptText.find("WidgetBody\">")+len("WidgetBody\">"):decryptText.find("<br")] 
    decryptTextB    = decryptText2[decryptText2.find("<br />")+len("<br />")+1:decryptText2.find("</p>")] 

    dA = decryptTextA.split("|")
    dB = decryptTextB.split("|")
    ldA = map(lambda x:x.lower(),dA)
    ldB = map(lambda x:x.lower(),dB)

    decrypt = dict(zip(dA,dB)+zip(dB,dA)+zip(ldA,ldB)+zip(ldB,ldA))

    terrainStarsValue    = starsToValue[terrainText   [terrainText   .find("/images/stars/")+len("/images/stars/"):terrainText   .find(".gif")+4]]
    difficultyStarsValue = starsToValue[difficultyText[difficultyText.find("/images/stars/")+len("/images/stars/"):difficultyText.find(".gif")+4]]
    containerValue       = sizeText[0:sizeText.find(".gif")]
    typeValue            = typeToValue[typeText[0:typeText.find(".gif")]]
    hintValue            = filter(lambda x:x in string.printable,reduce(lambda x,y:x+y,map(lambda x:decrypt[x] if decrypt.has_key(x) else x,hintText2)))

    #print terrainStarsValue
    #print difficultyStarsValue
    #print containerValue
    #print typeValue
    #print "#"+hintValue+"#"

    newWpt.getElementsByTagName("groundspeak:cache")[0].getElementsByTagName("groundspeak:terrain"         )[0].firstChild.nodeValue = terrainStarsValue
    newWpt.getElementsByTagName("groundspeak:cache")[0].getElementsByTagName("groundspeak:difficulty"      )[0].firstChild.nodeValue = difficultyStarsValue
    newWpt.getElementsByTagName("groundspeak:cache")[0].getElementsByTagName("groundspeak:container"       )[0].firstChild.nodeValue = containerValue
    newWpt.getElementsByTagName("groundspeak:cache")[0].getElementsByTagName("groundspeak:type"            )[0].firstChild.nodeValue = typeValue
    newWpt.getElementsByTagName("groundspeak:cache")[0].getElementsByTagName("groundspeak:long_description")[0].firstChild.nodeValue = filter(lambda x: x in printable, hintValue)


    gpxOnGPS +=[newWpt]
    gpxCounter+=1
  else:
    print str(gpxCounter-alreadyInside+1)+" out of: "+str(len(waypoints))+" "+name+" - alredy loaded"
    gpxCounter+=1

gpsFile = open(gpsFileName,"w")

gpsFile.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
gpsFile.write("<gpx>\n")
for i in gpxOnGPS:
  gpsFile.write(i.toxml()+"\n")
gpsFile.write("</gpx>\n")
gpsFile.close()



