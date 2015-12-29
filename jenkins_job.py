__author__ = 'wehappyfew'

import requests,pprint


def create_new_jenkins_job(j_url, j_port, new_job_name, j_user, j_pass):
	"""
	Create a new jenkins job

	:param j_url: eg http://mysite.com
	:param j_port: eg 8686 [8080 is jenkin's default]
	:param new_job_name: eg "NEW_JOB"
	:param j_user: Sauron
	:param j_pass: i_c_u
	:return:
	"""
	url     = '{0}:{1}/createItem?name={2}'.format(j_url, j_port, new_job_name)
	auth    = (j_user, j_pass)
	payload = '<project><builders/><publishers/><buildWrappers/></project>'
	headers = {"Content-Type" : "application/xml"}
	try:
		r = requests.post(url, data=payload, auth=auth, headers=headers)
		print "Responce code for -create_new_jenkins_job-", r.status_code
	except Exception , e:
		print "Something went wrong! I cound not create new Jenkins job.\n"
		print e

def create_jenkins_xml_config(github_username =None,
							  repo_name	= None,
							  juser = None,
							  jpass	= None,
							  j_xml_url	=None,
							  filename = None,
							  new_branch_name = None):
	"""
	The function reads the jenkins config.xml , saves it and changes the branch name.
	[Then, the file with the updated branch name is ready to be posted back.]

	1. Get the config.xml
	2. Save it to a file
	3. Parse the file with xmltodict and make it a puthon dictionary
	4. Parse the dictionary and find the branch name
	5. Replace it
	6. Rewrite the temp file with the new branch name [optionally the github_username and/or repo_name]

	:param github_username:
	:param repo_name:
	:param juser:
	:param jpass:
	:param j_xml_url: eg: http://55.66.11.184:8686/job/MyJobName/config.xml
	:param filename: Essentially the file path.If no path is provided , the file is created in this scripts path.
	:param new_branch_name:
	:return:
	"""
	import requests, xmltodict

	# Get the config.xml from the Jenkins URL
	auth    = (juser, jpass)
	headers = {"Content-Type" : "application/xml"}
	r = requests.get(j_xml_url, auth=auth, headers=headers)
	# print r.content # debugging

	# Create the temp file
	try:
		print('Creating new jenkins configuration xml file \n')
		file = open(filename,'w')
		file.write(r.content)
		file.close()
		print "File created"
	except Exception as e:
		print 'Something went wrong!\n', e

	# parse the xml and create a dict
	with open(filename) as fd:
		obj = xmltodict.parse(fd.read())

	# grab the current branch name
	branch_name = obj["project"]["scm"]["branches"]["hudson.plugins.git.BranchSpec"]["name"]
	print "Branch name found: ",branch_name

	# set the new branch name
	obj["project"]["scm"]["branches"]["hudson.plugins.git.BranchSpec"]["name"] = "*/%s"%new_branch_name
	print "New branch name set: */%s" % new_branch_name
	# optional: set the github_username, repo_name
	obj["project"]["scm"]["userRemoteConfigs"]["hudson.plugins.git.UserRemoteConfig"]["url"] = "git@github.com:{0}/{1}.git".format(github_username, repo_name)

	# write the temp file with the new branch name
	file = open(filename,'w')
	file.write(xmltodict.unparse(obj, pretty=True))
	file.close()
	print "File updated"

def post_new_xml_config(j_url, j_port, job_name, j_user, j_pass, new_config_path):
	"""
	The function reads the new file and posts it to replace the old one.
	It translates to Requests the cURL:
	curl -X POST http://jenkins:password@host.com:8686/job/Project/config.xml --data-binary "@new_config.xml"

	:param j_url: The url of the jenkins host
	:param j_port: The port jenkins listens on
	:param job_name: The jenkins job name
	:param j_user: The username
	:param j_pass: The password
	:param new_config_path: The path to the new config file.
							If it is in the same folder, use only the filename eg 'new_config.xml'
	:return: The responce code
	"""

	url 	= "{0}:{1}/job/{2}/config.xml".format(j_url, j_port, job_name)
	auth    = (j_user, j_pass)
	headers = {"Content-Type" : "application/xml"}
	try:
		with open(new_config_path, 'rb') as payload:
			print "Post to %s"%url
			r = requests.post(url, auth=auth, data=payload, headers=headers)
			if r.status_code == 200:
				print r.status_code
			else:
				print "- - -",r.status_code,"- - -"
				print r.text
	except Exception as e:
		print "Something went somewhat wrong..\n", e

def delete_temp_xml_config(filepath):
	"""
	If the script and the file to be deleted are in the same path enter as filepath only the file name.

	:param filepath:
	:return:
	"""
	import os
	os.remove(filepath)
	print "File deleted"


# Only for DEV --------------------------------------------------------------------------------------------------------
j_url  		= "http://52.91.136.13"
j_port 		= 32768 #Notice: must be taken as a cmdline arg -> sys.argv[1]
j_user 		= "jenkins"
j_pass 		= "bombardier"
job_name 	= "bombardier"
j_xml_url 	= "{0}:{1}/job/{2}/config.xml".format(j_url,j_port,job_name)

temp_config = "temp_config.xml"
create_jenkins_xml_config(github_username	="wehappyfew",
						  repo_name			="bombardiers",
						  juser				=j_user,
						  jpass				=j_pass,
						  j_xml_url			=j_xml_url,
						  filename			=temp_config,
						  new_branch_name	="master")
post_new_xml_config(j_url, j_port, job_name, j_user,j_pass, temp_config)
delete_temp_xml_config(filepath=temp_config)
# Only for DEV --------------------------------------------------------------------------------------------------------