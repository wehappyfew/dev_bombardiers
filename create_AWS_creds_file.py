__author__ = 'wehappyfew'



def create_boto_cfg(aws_key_id, aws_secret):
	"""
	The function creates a boto.cfg file in the user's folder [Linux].
	Check here: http://boto.readthedocs.org/en/latest/boto_config_tut.html

	If there is no file, it creates it.
	If new creds are provided, it rewrites the file.
	"""
	text = "[Credentials]\n" \
		   "AWS_ACCESS_KEY_ID={0}\n" \
		   "AWS_SECRET_ACCESS_KEY={1}"\
		.format(aws_key_id, aws_secret)
	f = file("~/.boto", "w")
	f.write(text)
	f.close()

create_boto_cfg("","")