from flask import Flask, render_template, request, redirect, Response
import json, os, datetime
os.chdir('/home/pi/Desktop/env/fl/src')
from logic_script import virtual_relay, save_to_file, dht_handler

app = Flask(__name__)
print(os.getcwd())
TEMP_KEY = 'temps'
SOCKETS_KEY = 'sockets'
SENSOR_ERRORS = 'sensor_errors'
save_to_file_obj = save_to_file.HandlerFile()
virtual_relay_obj = virtual_relay.Relays_class(obj=save_to_file_obj)
DATA_PATH = save_to_file_obj.STATIC_PATH
SENSOR_PATH = save_to_file_obj.STATIC_SENSOR_PATH
LIGHTING_PATH = save_to_file_obj.STATIC_LIGHTING_PATH
dht_handler_obj = dht_handler.DHT_Handler(
		data_path=DATA_PATH,
		sensors_path= SENSOR_PATH,
		file_obj=save_to_file_obj)


#create container to data
print(save_to_file_obj.create_container(DATA_PATH))

class MyExceptions(Exception):
	pass

@app.route('/')
def home():
	name = '''it is my own project'''
	return render_template('home.html', name=name)

@app.route('/temp')
def temp():
	'''function to view html page in site. Show all temp in rooms'''
	return render_template('temp.html', title='Temperatury')


@app.route('/sockets')
def sockets():
	'''function to view html page in site. Show selectbox to swith off and on sockets'''
	return render_template('sockets.html', title='Gniazda')

@app.route('/heat')
def heat_config():
	return render_template('heat.html', title='Ogrzewanie')



@app.route('/temp_logic', methods=['GET'])
def temp_background():
	'''function working background. this function read temp from sensors and save to .json file.
	Next send response to site in this case is list of dictionary with temperatures and huminidity'''
	temp_in_json = {f'{TEMP_KEY}' : save_to_file_obj.load_from_json(DATA_PATH, TEMP_KEY)}
	sensor_errors = {f'{SENSOR_ERRORS}': save_to_file_obj.load_from_json(DATA_PATH, SENSOR_ERRORS)}
	if temp_in_json:
		print('DATA WAS DETECTED TEMP')        
		temp_in_json.update(sensor_errors)
		# print(temp_in_json,'w nowej funkcji') 
		json_data = json.dumps(temp_in_json)
		return json_data
	print('DATA NOT DETECTED temp')
	# container varible contain dict with sensor names and temp and humidity value {...'salon': {temp:21,'humidity':39}...}
	# we use here sensor list path with sensor name and pin e.g {...'salon':1...}
	container = {f'{TEMP_KEY}':dht_handler_obj.temp_containter_list()}
	# extend with sensor_errors
	container.update(sensor_errors)
	# print('{} tu mamy container dla temp'.format(container))
	json_data = json.dumps(container)
	return json_data



@app.route('/lighting', methods = ['GET','POST'])
def lighting_relays_loader():
	return virtual_relay_obj.lighting_handler(request=request)
   

@app.route('/settimeSockets', methods = ['POST', 'GET'])
def set_time_request_handling():
	'''function handel request for site. In this case handle a seted time from user and save it to .txt file,
	if it is a POST methode othewise send to site response'''
	# POST
	if request.method == 'POST':
		# print('POST')
		data = json.loads(request.data)
		# save data to file
		save_to_file_obj.update_file(DATA_PATH, 'sockets', data)
		return 'OK'
	# GET
	else:       
		data = json.dumps(save_to_file_obj.load_from_json(DATA_PATH,'sockets'))
		# print(data, type(data))
		return data

@app.route('/settimeHeat', methods=['POST', 'GET'])
def set_time_heat():        
	if request.method == 'POST':
		# print('POST from site')                
		data = json.loads(request.data)
		# print('in post',data, type(data))
		save_to_file_obj.update_file(DATA_PATH, 'heat_switch', data)
		return 'ok'
	else:
		# print('GET from site')
		# test_data = {'ON':1,'OFF':2}
		data = save_to_file_obj.load_from_json(DATA_PATH, 'heat_switch')
		# print('in get',data, type(data))
		return json.dumps(data)

@app.route('/settempHeat', methods=['POST', 'GET'])
def set_temp_heat():
	if request.method == 'POST':
		data = json.loads(request.data)
		# print(data, type(data))
		save_to_file_obj.update_file(DATA_PATH, 'heats', data)
		return 'ok'
	else:
		# print('GET from seted temps heat')
		data = save_to_file_obj.load_from_json(DATA_PATH, 'heats')
		# print('in GEt', data, type(data) )        
		return json.dumps(data)


@app.route('/current', methods=['POST', 'GET'])
def recive_current_time():
	''' This function handling everything is related with current time and date.
	Function refresh current time and date then send date to site, turn on or off relays,
	or save data to csv file.'''
	full_time = datetime.datetime.now().strftime("%d/%m/%Y,%H:%M")	
	current_date, current_time = full_time.split(',')	
	if request.method == 'POST':
		print('Aktualna godzina ze strony: {}'.format(request.data.decode('ascii')))
		# current_time = request.data.decode('ascii')        
		virtual_relay_obj.switch_handler(current_time=current_time)
		save_to_file.HandlerCsv().save_temp_to_csv_handler(
			current_time=current_time)
		return 'ok'
	else:
		# send date to site 
		return current_date

# @app.route('/refreshdate', methods=['GET'])
# def refresh_date():
# 	pass		

@app.route('/updatetemp', methods=['GET'])
def update_temp():
	'''this function save to .json file readed temperature from sensors'''
	print('IN UPDATE')
	# container varible contain dict with sensor names and temp and humidity value {...'salon': {temp:21,'humidity':39}...}
	# we use here sensor list path with sensor name and pin e.g {...'salon':1...}    
	container = dht_handler_obj.update()    
	return 'data was update!! {0}'.format(container)
	

if __name__ == '__main__':
	app.run(debug=1)


