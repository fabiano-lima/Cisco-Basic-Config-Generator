#!/usr/bin/env python
# -*- coding: utf-8 -*-
"###############################################################################################"
"Basic Config Generator"
"Author: Fabiano Lima - March 2015 Draft 2.0 - April 23rd 2015 Draft 3.0"
"This is a draft script for creating a basic config file from a full informed to be sent to a FE when replacing cisco routers or switches "
"###############################################################################################"



from ciscoconfparse import CiscoConfParse
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
from flask import Flask, make_response, request
from flask import send_file


UPLOAD_FOLDER = '/home/enteryourfolder>'
ALLOWED_EXTENSIONS = set(['txt'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def transform(filename):

	#1st Part

	with open(os.path.join(app.config['UPLOAD_FOLDER'],filename), "rU") as infile:

		p = CiscoConfParse(infile)

		objs = list()

		objs.extend(p.find_objects(r'^policy-map'))
		objs.extend(p.find_objects(r'ip\saccess-list'))
		objs.extend(p.find_objects(r'^class-map'))
		objs.extend(p.find_objects(r'^crypto pki'))
		objs.extend(p.find_objects(r'^track'))
		objs.extend(p.find_objects(r'^ip sla'))
		objs.extend(p.find_objects(r'^zone-pair'))
		objs.extend(p.find_objects(r'^archive'))
		objs.extend(p.find_objects(r'^banner '))
		objs.extend(p.find_objects(r'^line '))
		objs.extend(p.find_objects(r'^username'))
		objs.extend(p.find_objects(r'^logging '))
		objs.extend(p.find_objects(r'^end'))
		objs.extend(p.find_objects(r'^access-list'))

		for obj in objs:
			obj.delete()

		for interface in p.find_objects_w_child('^interface', 'spanning-tree portfast'):
			interface.delete(interface)

		for interface in p.find_objects_w_child('^interface', 'switchport port-security'):
			interface.delete(interface)

		p.commit()

		p.save_as (os.path.join(app.config['UPLOAD_FOLDER'], 'file_parsed_1st.txt'))


	#2nd Part

	with open (os.path.join(app.config['UPLOAD_FOLDER'], 'file_parsed_1st.txt'), "rU") as file_parsed_2nd:

		with open(os.path.join(app.config['UPLOAD_FOLDER'], 'file_parsed_2nd.txt'), "w") as outfile:

			security_lines = ['last','Last','version','service timestamps','service password','tcp-keepalives','marker','flow-','enable secret',
							'csdb', 'ip accouting','timezone','aaa','ssh','snmp','service-policy','tacacs','privilege',
							'alias','ntp','scheduler allocate','exec-timeout', 'service pad','syslog',
							'small-servers','enable password','zone-member','zone security','ip http','mls','igmp', 'radius-server',
							'forward-protocol','cdp','nagle','resource policy','gratuitous-arps','resource policy''control-plane',
							'-time','errdisable','#','Building configuration','Current configuration','memory-size iomem','no ip source-route',
							'no ip bootp server','no ip domain lookup','no ipv6 cef','no logging console','multilink bundle-name authenticated',
							'ip accounting','standby']

			emptyline = ['\n', '\r\n']

			for line in file_parsed_2nd:
				if not line in emptyline and not any(security_line in line for security_line in security_lines):
					outfile.write(line)



	# 3rd Part

			outfile.write('enable secret cisco\n')
			outfile.write('line vty 0 4\n')
			outfile.write('    password cisco\n')
			outfile.write('    no access-class 23 in\n')
			outfile.write('end\n')
			outfile.write('!\n')



		return send_file(os.path.join(app.config['UPLOAD_FOLDER'], 'file_parsed_2nd.txt'))




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():

	try:
		os.stat(app.config['UPLOAD_FOLDER'])
	except:
		os.mkdir(app.config['UPLOAD_FOLDER'])
	if request.method == 'POST':
		file = request.files['file']

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

			result = transform(filename)
			response = make_response(result)
			response.headers["Content-Type"] = 'text/plain'
			response.headers["Content-Disposition"] = "inline; filename=basic_config.txt"
			return response


	return render_template('index.html')


if __name__ == '__main__':
    app.run(
        debug=True
    )
