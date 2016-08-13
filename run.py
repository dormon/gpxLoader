#!/usr/bin/python

import os

files=[]

for dirname, dirnames, filenames in os.walk('.'):
  files+=filenames

files=filter(lambda x:x.find("loc")>=0,files)

#merge=""

for i in files:
  print i
  a=i.replace(" ","\\ ")
  a=a.replace("(","\\(")
  a=a.replace(")","\\)")
  os.system("./loctogps.py "+a)
#  merge+=" "+i

#bigname="big.loc"

#os.system("cat"+merge+" > "+bigname)

#os.system("./loctogps.py "+bigname)
#os.system("rm "+bigname)


