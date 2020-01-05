from flask import Flask, render_template, request, redirect, Response
import json, os, datetime
os.chdir('/home/pi/Desktop/env/fl/src')
from logic_script import virtual_relay, save_to_file, dht_handler

app = Flask(__name__)
print(os.getcwd())
TEMP_KEY = 'temps'
save_to_file_obj = save_to_file.HandlerCsv()
LIGHTING_PATH = save_to_file_obj.STATIC_LIGHTING_PATH
CSV_file_path = save_to_file_obj.STATIC_AGREGATE_TEMPERATURE
dht_handler_obj = dht_handler.DHT_Handler(		
		file_obj=save_to_file_obj)
SQL_obj = save_to_file_obj
virtual_relay_obj = virtual_relay.Relays_class(obj=save_to_file_obj)

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
def temp_background() -> dict:
	'''function working background. this function read temp from sensors and save to .json file.
	Next send response to site in this case is list of dictionary with temperatures and huminidity'''
		
	temperature_in_db = SQL_obj.fetch_all_data_from_temp(temperature_dict=True)
	if type(temperature_in_db) == dict:
		json_data = json.dumps(temperature_in_db)
		return json_data
	elif temperature_in_db:
		raise TypeError('temperature_in_db is not dict!!')
	else:
		print('DATA NOT DETECTED temp')
		# container varible contain dict with sensor names and temp and humidity value {...'salon': {temp:21,'humidity':39}...}
		# we use here sensor list path with sensor name and pin e.g {...'salon':1...}
		container = dht_handler_obj.dict_with_keys_as_room_names_and_dict_as_value()
		json_data = json.dumps(container)
		return json_data	
	
	
			
	


@app.route('/lighting', methods = ['GET','POST'])
def lighting_relays_loader():
	return virtual_relay_obj.lighting_handler(request=request)
   

@app.route('/settimeSockets', methods = ['POST', 'GET'])
def set_time_request_handling():
	'''function handel request for site. In this case handle a seted time from user and save it to .json file,
	if it is a POST methode othewise send to site response.
	We use here dht_handler_obj instead save_to_file_obj because there we
	have variable which have reference to HandlerSQL. So is useless to create new
	reference.'''	
	# POST
	if request.method == 'POST':
		# fetch data from site and decode to dict object		
		data = json.loads(request.data)			
		# times in string ON and Off received from site
		tup_data = tuple(data.values())		
		SQL_obj.update_data_in_sockets_table(times=tup_data, row=1)		
		return 'OK'
	# GET
	else:		
		fetched_times_tuple = SQL_obj.fetch_all_data_from_sockets(row=1)
		data_to_send = dict(zip(['ON','OFF'], fetched_times_tuple))		
		db_data = json.dumps(data_to_send)		
		return db_data

@app.route('/settimeHeat', methods=['POST', 'GET'])
def set_time_heat():        
	if request.method == 'POST':
		# times recived from site converted to dict.		                
		data = json.loads(request.data)			
		SQL_obj.update_data_in_sockets_table(times=tuple(data.values()),
											row=2) # heaters		
		return 'ok'
	else:		
		fetched_data = SQL_obj.fetch_all_data_from_sockets(row=2) # heaters switch		
		data_from_db = dict(zip(['ON','OFF'], fetched_data))					
		return json.dumps(data_from_db)

@app.route('/settempHeat', methods=['POST', 'GET'])
def set_temp_heat():
	if request.method == 'POST':
		data = json.loads(request.data)				
		# with wc and outside but values are setet to 0 
		tokens_int = tuple(data.values()) + (0,0,)
		SQL_obj.update_data_tokens(temperature_int=tokens_int, row=2)# heaters temperature set		
		return 'ok'
	else:
		to_remove = ["WC", "outside"]		
		data_db = SQL_obj.fetch_data_from_tokens(row=2, show_dict=True)		
		# dict with rooms
		data_to_send = {room: val for room, val in data_db.items() 
						if room not in to_remove}				        
		return json.dumps(data_to_send)


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
		save_to_file_obj.save_temp_to_csv_handler(path=CSV_file_path, full_time=full_time)		
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

@app.route('/tokensupdate', methods=['GET'])
def update_tokens_in_db_file():	
	if request.method == 'GET':
		table_name = dht_handler_obj.table_name # tokens_table
		# in below var (dict_data) we have dict with room_name as key and val as token_intereg
		colum_names = SQL_obj.fetch_column_names(table_name=table_name)[1:]# without id
		dict_data = dict(zip(colum_names,
						SQL_obj.main_fetch_data_from_db(table_name=table_name,row=1)))						
		json_data_to_server_as_response = json.dumps(dict_data)
		return json_data_to_server_as_response
	else:
		print('not GET reqeust')
		return False
	

if __name__ == '__main__':
	app.run(debug=1)


