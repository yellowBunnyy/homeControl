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
ERRORS_PATH = save_to_file_obj.STATIC_ERRORS_PATH
DB_ERRORS_PATH = save_to_file_obj.STATIC_DB_ERRORS_PATH
dht_handler_obj = dht_handler.DHT_Handler(
		data_path=DATA_PATH,
		sensors_path= SENSOR_PATH,
		errors_path = ERRORS_PATH,		
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
	temp_in_json = {f'{TEMP_KEY}' : save_to_file_obj.load_from_json(path=DATA_PATH, key=TEMP_KEY)}
	
	if temp_in_json:				
		json_data = json.dumps(temp_in_json)
		return json_data
	print('DATA NOT DETECTED temp')
	# container varible contain dict with sensor names and temp and humidity value {...'salon': {temp:21,'humidity':39}...}
	# we use here sensor list path with sensor name and pin e.g {...'salon':1...}
	container = {f'{TEMP_KEY}':dht_handler_obj.dict_with_keys_as_room_names_and_dict_as_value()}		
	json_data = json.dumps(container)
	return json_data


@app.route('/lighting', methods = ['GET','POST'])
def lighting_relays_loader():
	return virtual_relay_obj.lighting_handler(request=request)
   

@app.route('/settimeSockets', methods = ['POST', 'GET'])
def set_time_request_handling():
	'''function handel request for site. In this case handle a seted time from user and save it to .json file,
	if it is a POST methode othewise send to site response'''
	# POST
	if request.method == 'POST':		
		data = json.loads(request.data)
		# save data to file
		save_to_file_obj.update_file(DATA_PATH, 'sockets', data)
		return 'OK'
	# GET
	else:       
		data = json.dumps(save_to_file_obj.load_from_json(DATA_PATH,'sockets'))		
		return data

@app.route('/settimeHeat', methods=['POST', 'GET'])
def set_time_heat():        
	if request.method == 'POST':		                
		data = json.loads(request.data)		
		save_to_file_obj.update_file(DATA_PATH, 'heat_switch', data)
		return 'ok'
	else:				
		data = save_to_file_obj.load_from_json(DATA_PATH, 'heat_switch')		
		return json.dumps(data)

@app.route('/settempHeat', methods=['POST', 'GET'])
def set_temp_heat():
	if request.method == 'POST':
		data = json.loads(request.data)		
		save_to_file_obj.update_file(DATA_PATH, 'heats', data)
		return 'ok'
	else:		
		data = save_to_file_obj.load_from_json(DATA_PATH, 'heats')		        
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
		virtual_relay_obj.switch_handler(current_time=current_time)
		save_to_file.HandlerCsv().save_temp_to_csv_handler(
			full_time=full_time)		
		return 'ok'
	else:
		# send date to site 
		return current_date


@app.route('/updatetemp', methods=['GET'])
def update_temp():
	'''this function save to .json file readed temperature from sensors'''
	# print('IN UPDATE')
	# container varible contain dict with sensor names and temp and humidity value {...'salon': {temp:21,'humidity':39}...}
	# we use here sensor list path with sensor name and pin e.g {...'salon':1...}    
	container = dht_handler_obj.update()    
	return 'data was update!! {0}'.format(container)

@app.route('/dbupdate', methods=['GET'])
def update_db_file():	
	if request.method == 'GET':			
		SQL_obj = dht_handler_obj.SQL_obj
		table_name = dht_handler_obj.table_name
		# in below var (dict_data) we have dict with room_name as key and val as token_intereg 
		dict_data = dict(zip(SQL_obj.fetch_column_names(table_name=table_name), 
						SQL_obj.read_from_db(table_name=table_name)))
		print(dict_data)				
		json_data_to_server_as_response = json.dumps(dict_data)
		return json_data_to_server_as_response
	else:
		print('not GET reqeust')
		return False
	

if __name__ == '__main__':
	app.run(debug=1)


