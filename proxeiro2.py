__author__ = 'wehappyfew'

import subprocess,os

# 1
# p = subprocess.Popen( "ipconfig", stdout=subprocess.PIPE, shell=True )
# (output, err) = p.communicate()
# print output, err

# filepath = "test.txt"
#
# file = open(filepath,'w')
# file.write("hello")
# file.close()
# print "File created"

# os.remove(filepath)

directory = "volume_CLIENT_ID"
if not os.path.exists(directory):
    os.makedirs(directory)