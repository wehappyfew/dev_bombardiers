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

def create_jenkins_xml_config(github_username, repo_name="bombardiers", branch_name="master", filename = 'new_config.xml'):
	"""
	The function creates [is not exists] an XML config file for jenkins
	and sets the user provided data.
	If the file already exists, it rewrites it and replaces the variables with the new ones.

	:param github_username   : The user provided github username
	:param repo_name		 : The user provided repo name , defaults to 'bombardiers'
	:param branch_name 		 : The user provided branch name , defaults to 'master'
	:return:
	"""

	xml_text = \
	"<project>\n" \
	"<actions/>\n" \
	"<description/>\n" \
	"<keepDependencies>false</keepDependencies>\n" \
	"<properties>\n" \
	"<com.coravy.hudson.plugins.github.GithubProjectProperty plugin=\"github@1.14.0\">\n" \
	"<projectUrl>https://github.com/{0}/{1}/</projectUrl>\n" \
	"</com.coravy.hudson.plugins.github.GithubProjectProperty>\n" \
	"</properties>\n" \
	"<scm class=\"hudson.plugins.git.GitSCM\" plugin=\"git@2.4.0\">\n" \
	"<configVersion>2</configVersion>\n" \
	"<userRemoteConfigs>\n" \
	"<hudson.plugins.git.UserRemoteConfig>\n" \
	"<url>https://github.com/{0}/{1}.git</url>\n" \
	"</hudson.plugins.git.UserRemoteConfig>\n" \
	"</userRemoteConfigs>\n" \
	"<branches>\n" \
	"<hudson.plugins.git.BranchSpec>\n" \
	"<name>*/{2}</name>\n" \
	"</hudson.plugins.git.BranchSpec>\n" \
	"</branches>\n" \
	"<doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>\n" \
	"<submoduleCfg class=\"list\"/>\n" \
	"<extensions/>\n" \
	"</scm>\n" \
	"<canRoam>true</canRoam>\n" \
	"<disabled>false</disabled>\n" \
	"<blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>\n" \
	"<blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>\n" \
	"<triggers>\n" \
	"<com.cloudbees.jenkins.GitHubPushTrigger plugin=\"github@1.14.0\">\n" \
	"<spec/>\n" \
	"</com.cloudbees.jenkins.GitHubPushTrigger>\n" \
	"</triggers>\n" \
	"<concurrentBuild>false</concurrentBuild>\n" \
	"<builders/>\n" \
	"<publishers/>\n" \
	"<buildWrappers/>\n" \
	"</project>\n" .format(github_username, repo_name, branch_name)

	try:
		print('Creating new jenkins configuration xml file \n')
		file = open(filename,'w')
		file.write(xml_text)
		file.close()
		print "File created"

	except Exception as e:
		print 'Something went wrong!\n', e

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
j_url  = "http://52.91.136.13"
j_port = 32769 #Notice: must be taken as a cmdline arg -> sys.argv[1]
j_user = "jenkins"
j_pass = "bombardier"
job_name = "bombardier"

# create_new_jenkins_job(j_url=j_url,j_port=j_port,new_job_name=job_name, j_user=j_user, j_pass=j_pass)
temp_config = "temp_config.xml"
create_jenkins_xml_config("wehappyfew", branch_name="master", filename=temp_config)
post_new_xml_config(j_url, j_port, job_name, j_user,j_pass, temp_config)
delete_temp_xml_config(filepath=temp_config)
# Only for DEV --------------------------------------------------------------------------------------------------------