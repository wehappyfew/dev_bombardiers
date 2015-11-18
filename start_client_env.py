__author__ = 'wehappyfew'
import subprocess
import time
from jenkins_job import create_jenkins_xml_config, post_new_xml_config
# TODO: scenario1: both containers will share a host volume [Notice PROBLEM: Jenkins inside the container cannot build the code]
# TODO: scenario2: locust will have access to the tests inside the jenkins container. That way the jenkins container can never be stopped or the client data will be lost

# User provided vars
CLIENT_locustfile 	= "locustfile.py"
CLIENT_gh_username  = "wehappyfew"
CLIENT_repo_name 	= "bombardiers"
CLIENT_branch_name 	= "master" #should default to master

# I define these vars
client_id 	= "wehappyfew" 				# Notice: make it dynamic. Based on signup id . Or use the unique username
j_url  		= "http://52.91.136.13/" 	# Notice: normally www.bombardier.com
j_user 		= "jenkins"
j_pass 		= job_name = "bombardier" 	# Notice: j_pass must be based on client_id
new_config 	= "{0}_config.xml".format(client_id)

# # Create a host volume for the new client in the specific volumes folder Notice:migrate to S3
# # Notice: choose which hosts file you will use
# subprocess.call(["ansible-playbook", "-i", "hosts", "--extra-vars", "'{\"CLIENT_ID\":\"%s\"}'"%client_id, "create_new_client_volume.yml"])

print "START: Initializing environment for user '%s'"%client_id
# JENKINS CONTAINER SETUP-----------------------------------------------------------------------------------------------
# 

# 1. --Start the jenkins container--
j_name = "{0}-jenkins".format(client_id)
workspace_path = "/var/jenkins_home/jobs/bombardier/workspace"

subprocess.call(["docker", "run", "-d",
				 "--name", j_name,
				 "-p", "8080", # Notice: maps it to a random host port [but the client wont have access to it]
				 "-v", "{0}".format(workspace_path), # is needed to connect jenkins volume with locust container Notice: may use host volume [/home/ubuntu/clients_volumes/CLIENT_ID_volume]
				 "kostadis/bombardier:jenkins-gh"
				])

print "Container '%s' is up."%j_name
print "[%s] Waiting for JenkinsCI server to start..."%j_name ; time.sleep(20)

# 2. --Grab the Jenkins random host port--
port_cmd = "docker inspect --format '{{ (index (index .NetworkSettings.Ports \"8080/tcp\") 0).HostPort }}' {0}".format(j_name)
p = subprocess.Popen( port_cmd, stdout=subprocess.PIPE, shell=True )
(j_output, j_err) = p.communicate()
jenkins_random_port = j_output

print "[{0}] The JenkinsCI server's port is: {1}".format(j_name, jenkins_random_port)

# 3. --Set the user's username & repo URL--
# The Jenkins container has already setup the bombardier job and the GH plugin
create_jenkins_xml_config(CLIENT_gh_username, CLIENT_repo_name, CLIENT_branch_name, filename=new_config )
post_new_xml_config(j_url, jenkins_random_port, job_name, j_user, j_pass, new_config_path=new_config)
print "[%s] JenkinsCI server config is set."%j_name

# 
# JENKINS CONTAINER SETUP-----------------------------------------------------------------------------------------------


# LOCUST CONTAINER SETUP-----------------------------------------------------------------------------------------------
# 

# 4. --Start the locust container--
l_name = "{0}-locust".format(client_id)

subprocess.call(["docker", "run", "-d",
				 "--name", l_name,
				 "-p", "8089", # Notice: maps it to a random host port [will be client accessible]
				 "--volumes-from", j_name, # attach jenkins workspace volume Notice: may use host volume
				 "kostadis/bombardier:lbomb", # TODO finalize the image
				 "locust", "-f", "{0}/{1}".format(workspace_path, CLIENT_locustfile), "--master"
				#  Notice: check if is needed the locust master to be sent to background
				])

print "Container '%s' is up."%l_name
print "[%s] Waiting for Locust master server to start..."%l_name ; time.sleep(5)

# 5. --Grab the locust web UI random host port
port_cmd = "docker inspect --format '{{ (index (index .NetworkSettings.Ports \"8089/tcp\") 0).HostPort }}' {0}".format(l_name)
p = subprocess.Popen( port_cmd, stdout=subprocess.PIPE, shell=True )
(l_output, l_err) = p.communicate()
locust_random_port = l_output

print "[{0}] The Locust master server's port is: {1}".format(l_name, locust_random_port)

# 6. --Edit the AWS security group with the locust_random_port--
# todo
subprocess.call(["ansible-playbook", "-i", "hosts",
				 "--extra-vars",
				 "'{\"CLIENT_USERNAME\":\"{0}\" , \"REGION\":\"us-east-1\" , \"J_PORT\":\"{1}\", \"L_PORT\":\"{2}\" }'".format(client_id,jenkins_random_port,locust_random_port),
				 "create_sec_group.yml"])
