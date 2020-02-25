from logic_script import dht_handler, save_to_file, virtual_relay
room_names = save_to_file.HandlerFile().room_names
import pytest, flask_home, os, Adafruit_DHT, flask, json, random, sqlite3
from unittest.mock import patch
from unittest.mock import Mock
from logic_script.save_to_file import MyExceptions


test_path = os.path.join(os.getcwd(),'logic_script','test_csv.csv')

#SQL fixtures

@pytest.fixture(name='SQL_obj')
def SQL_obj_class():
	SQL_obj = save_to_file.HandlerSQL()
	return SQL_obj

@pytest.fixture(name='sql_obj_not_called')
def SQL_obj_class_not_called():
	obj = save_to_file.HandlerSQL
	return obj

# csv fixture
@pytest.fixture(name='csv_in_class')
def csv_cls():
	csv_obj = save_to_file.HandlerCsv()
	return csv_obj

@pytest.fixture(name='pure_csv')
def pure_csv(backend):
	csv_obj = save_to_file.CSV_Class(backend_file=backend.save_to_file())
	return csv_obj

#Backend fixture

@pytest.fixture(name='backend')
def create_backend():
	backend_obj = save_to_file.FileHandler(path=test_path) 
	return backend_obj

# dht fuxture class obj

@pytest.fixture(name='dht_obj')
def dht_class_obj():
	dht_obj = dht_handler.DHT_Handler()
	return dht_obj

@pytest.fixture(name='dht_obj_not_called')
def dht_cls_obj():
	obj = dht_handler.DHT_Handler
	return obj

@pytest.fixture(name='simpleyTestingCls')
def simpleytTestingCls():
	obj = dht_handler.SimpleyTesting()
	return obj

# virtual relay fixture

@pytest.fixture(name='obj_v_relay_not_called')
def obj_virtual_realay():
	obj = virtual_relay.Relays_class
	return obj

# save to file fixture
@pytest.fixture(name='handler_file_obj')
def save_to_file_obj():
	obj = save_to_file.HandlerFile()
	return obj

@pytest.fixture(name='handler_file_not_called')
def save_to_file_obj_not_called():
	obj = save_to_file.HandlerFile
	return obj

# create file 
@pytest.fixture(name='test_json_file')
def create_test_file():
	path = r'/home/pi/Desktop/env/fl/src/logic_script/test.json'
	content = {'salon':1, 'wc':2}
	with open(path, 'w') as f:
		f.write(json.dumps(content))
	yield path, content 
	os.remove(path)


	

#monkeypath
@pytest.fixture(name='no_req')
def no_request(monkeypath):
	monkeypath.delattr('flask.request.method')
	
##### HandlerSQL class


# create backend db file
@pytest.fixture(name='backend_db_file')
def create_db_file():
	db_path = r'/home/pi/Desktop/env/fl/src/test_db.db'
	with open(db_path, 'w') as f:
		f.write('')
		yield db_path
	os.remove(db_path)


# create connection
@pytest.fixture(name='conn')
def create_connection(backend_db_file):
	conn = sqlite3.connect(backend_db_file)
	yield conn
	conn.close()

# created cursor
@pytest.fixture(name='cursor')
def create_cursor(backend_db_file):
	conn = sqlite3.connect(backend_db_file)
	cursor = conn.cursor()
	yield cursor
	conn.close()	


# cursor with maked socket table
@pytest.fixture(name='table_sockets')
def create_table_socket(conn):
	sql = '''CREATE TABLE IF NOT EXISTS sockets (
				id integer PRIMARY KEY,
				turn_on text,
				turn_off text);
		'''
	cursor = conn.cursor()
	cursor.execute(sql)
	yield conn

#cursor with maked errors tokens table
@pytest.fixture(name='table_tokens')
def create_table_token(conn):
	sql = '''CREATE TABLE IF NOT EXISTS errors_tokens_and_seted_temperature (
				id integer PRIMARY KEY,
				salon integer,
				maly_pokoj integer,
				kuchnia integer,
				WC integer,
				outside integer);'''
	cursor = conn.cursor()
	cursor.execute(sql)
	yield conn

#cursor with maked temp & humidity table
@pytest.fixture(name='table_temperature')
def create_table_temperature(conn):
	sql = '''CREATE TABLE IF NOT EXISTS 'temperature_humidity' (
				id integer PRIMARY KEY,
				salon integer,
				maly_pokoj integer,
				kuchnia integer,
				WC integer,
				outside integer);'''
	cursor = conn.cursor()
	cursor.execute(sql)	
	yield conn

@pytest.fixture(name='table_temperature_cursor')
def create_table_temperature_cursor(conn):
	sql = '''CREATE TABLE IF NOT EXISTS 'temperature_humidity' (
				id integer PRIMARY KEY,
				salon integer,
				maly_pokoj integer,
				kuchnia integer,
				WC integer,
				outside integer);'''
	cursor = conn.cursor()
	cursor.execute(sql)	
	yield cursor

## fetch data

# fetch all data from temp

@pytest.mark.parametrize('data_to_table, input_data, expected', (
	((20,21,22,23,24), [False, False, False], [(1, 20, 21, 22, 23, 24)]),
	))
def test_fetch_all_data_from_temp_one_row(data_to_table, input_data, expected, SQL_obj, table_temperature):
	table_temperature_conn = table_temperature
	SQL_obj.insert_data_to_temperature(conn=table_temperature_conn, tuple_int=data_to_table)
	row, temperature_dict, pin_dict = input_data
	from_method = SQL_obj.fetch_all_data_from_temp(conn=table_temperature_conn,
												row=row, 
												temperature_dict=temperature_dict,
												pin_dict=pin_dict)
	assert from_method == expected


@pytest.mark.parametrize('data_to_table, input_data, expected', (
	([(20,21,22,23,24), (11,22,33,44,55), (1,2,3,4,5)], 
		[False, False, False], # return pure fetchall()
		[(1, 20, 21, 22, 23, 24),(2,11,22,33,44,55), (3,1,2,3,4,5)]),
	([(20,21,22,23,24), (11,22,33,44,55), (1,2,3,4,5)],
		[1, False, False], # return wanted row > 0
		(20,21,22,23,24)),
	([(20,21,22,23,24), (11,22,33,44,55), (1,2,3,4,5)],
		[True, False, False], # return wanted row > 0
		(20,21,22,23,24)),
	([(20,21,22,23,24), (11,22,33,44,55), (1,2,3,4,5)],
		[2, False, False], # return wanted. row > 0
		(11,22,33,44,55)),
	([(20,21,22,23,24), (11,22,33,44,55), (1,2,3,4,5)],
		[3, False, False], # return wanted. row > 0
		(1,2,3,4,5)),
	([(20,21,22,23,24), (11,22,33,44,55), (1,2,3,4,5)],
		[False, True, False], # return dict with data e.g. look down 
		{'salon': {'temp':20, 'humidity':11}, 'maly_pokoj': {'temp':21, 'humidity':22},
		'kuchnia': {'temp':22, 'humidity':33}, 'WC': {'temp':23, 'humidity':44}, 'outside':{'temp':24, 'humidity':55}}),
	([(20,21,22,23,24), (11,22,33,44,55), (1,2,3,4,5)],
		[False, False, True], # return wanted row > 0
		{'salon':1, 'maly_pokoj':2, 'kuchnia':3, 'WC':4, 'outside':5}),
	))
def test_fetch_all_data_from_temp_multiple_rows(data_to_table, input_data, expected, SQL_obj, table_temperature, conn):
	table_temperature_conn = table_temperature
	for row_with_data in data_to_table:
		SQL_obj.insert_data_to_temperature(conn=table_temperature_conn, tuple_int=row_with_data)
	row, temperature_dict, pin_dict = input_data
	from_method = SQL_obj.fetch_all_data_from_temp(conn=conn,
												row=row, 
												temperature_dict=temperature_dict,
												pin_dict=pin_dict)
	assert from_method == expected


@pytest.mark.parametrize('data_to_table, input_data', (
	([(20,21,22,23,24), (11,22,33,44,55), (1,2,3,4,5)], 
		[10, False, False]), # row out of range	
	([(20,21,22,23,24), (11,22,33,44,55), (1,2,3,4,5)], 
		[0, False, False]),
	# ([(20,21,22,23,24), (11,22,33,44,55), (1,2,3,4,5)], 
	# 	[True, False, False]),
	))
def test_fetch_all_data_from_temp_multiple_rows_raise_err(data_to_table, input_data, SQL_obj, table_temperature, conn):
	#check row == 0
	table_temperature_conn = table_temperature
	for row_with_data in data_to_table:
		SQL_obj.insert_data_to_temperature(conn=table_temperature_conn, tuple_int=row_with_data)
	row, temperature_dict, pin_dict = input_data
	# import wdb; wdb.set_trace()
	with pytest.raises(Exception):
		from_method = SQL_obj.fetch_all_data_from_temp(conn=conn,
												row=row, 
												temperature_dict=temperature_dict,
												pin_dict=pin_dict)

# fetch all data from socket
@pytest.mark.parametrize('input_data, data_to_table, expected', (
	([1, True, False], [('00:12','10:20'), ('09:48', '23:59')], '00:12'), # return turn_on time
	([1, False, True], [('00:12','10:20'), ('09:48', '23:59')], '10:20'), # return turn_off time
	([1, False, False], [('00:12','10:20'), ('09:48', '23:59')], ('00:12','10:20')), # return row as tuple
	([False, False, False], [('00:12','10:20'), ('09:48', '23:59')], [('00:12','10:20'), ('09:48', '23:59')]),
	))
def test_fetch_all_data_from_sockets(input_data, data_to_table, expected, SQL_obj, table_sockets):
	row, turn_on, turn_off = input_data
	conn = table_sockets
	for tup_row in data_to_table:
		SQL_obj.insert_data_to_sockets_table(conn=conn, times=tup_row)
	from_method = SQL_obj.fetch_all_data_from_sockets(conn=conn, row=row, turn_on=turn_on, turn_off=turn_off)
	assert from_method == expected


def test_fetch_all_data_from_sockets_raise_err():
	pass

## SQL
	## tbl temperature_humidity


# @pytest.mark.parametrize('expected',(
# 	(dict),
# 	(room_names),
# 	))
# def test_fetched_data(expected, SQL_obj):	
# 	data = SQL_obj.fetch_all_data_from_temp(temperature_dict=True)
# 	if expected == dict:
# 		assert type(data) == dict
# 	else:
# 		data = list(data.keys())                                                                                                                                                                                                                                                                                                                                                                                                                       
# 		assert expected == data

# def test_initial_fetched_data(SQL_obj):	
# 	data = SQL_obj.fetch_all_data_from_temp()	
# 	assert data


# def test_return_list(SQL_obj):	
# 	data = SQL_obj.fetch_all_data_from_temp()
# 	assert type(data) == list


# def test_room_names_are_correct(SQL_obj):	
# 	fetched_list_with_tuples = SQL_obj.fetch_all_data_from_temp()	
# 	temps, humidity, _ =  [tup[1:] for tup in fetched_list_with_tuples]
# 	list_with_temps_and_humidity = [{'temp':temp, 'humidity': hum} 
# 									for temp, hum in zip(temps, humidity)]
# 	ans = dict(zip(room_names, list_with_temps_and_humidity))
# 	assert ans == SQL_obj.fetch_all_data_from_temp(temperature_dict=True)

# def test_fetch_all_data_from_temp_return_choosen_row(SQL_obj):
# 	method = SQL_obj.fetch_all_data_from_temp(row=3)
# 	expected = tuple(SQL_obj.names_and_pins_default.values())
# 	assert method == expected


# def test_initials_tbl_in_db_method(SQL_obj):	
# 	expected = 3
# 	fetched_data = SQL_obj.fetch_all_data_from_temp()
# 	assert expected == len(fetched_data)
# 	## other TBL

# def test_names_and_pins_output_data_is_dict(SQL_obj):
# 	from_method = SQL_obj.fetch_all_data_from_temp(pin_dict=True)
# 	expected = dict
# 	assert expected == type(from_method)

# def test_names_and_pins_correct_output_data(SQL_obj):
# 	from_method = SQL_obj.fetch_all_data_from_temp(pin_dict=True)
# 	expected = SQL_obj.names_and_pins_default
# 	assert expected == from_method


##CSV
# @pytest.mark.parametrize('time_examples',(
# 	(['23-10-2019,08:00', '24-10-2019,10:00', '25-10-2019,14:00']),
# 	(['30-10-2019,01:00', '31-10-2019,22:00', '31-10-2019,11:00']),
# 	))	
# def test_saved_data_to_csv_main_file(csv_in_class, backend, time_examples):
# # create and save data to file 	
# 	triggers = csv_in_class.TRIGGER_HOURS
# 	for full_time in time_examples:
# 		csv_in_class.save_temp_to_csv_handler(path=test_path, full_time=full_time)
# 		f = backend.save_to_file()
# 		_, expected = save_to_file.CSV_Class(
# 				backend_file=f).read_csv(close_file=True)			
# 	else:
# 		f = backend.save_to_file()
# 	_, rows = save_to_file.CSV_Class(
# 		backend_file=f).read_csv(close_file=True)
# 	assert expected == rows


def test_save_data_to_csv_main_file_correct_data_last_row(csv_in_class, pure_csv, backend):
# check if last row saved row are valid. then delete file.
	data = dict(zip(room_names, range(len(room_names))))
	date, hour = '31-10-2019,22:00'.split(',')
	expected = {'date':date, 'hour':hour}
	expected.update(data)	
	csv_in_class.save_to_file_csv(path=test_path, data=data, hour=hour, date=date)			
	fetched_data, _ = pure_csv.read_csv(close_file=True)
	last_row = fetched_data[-1]
	assert expected == last_row
	backend.delete_file()

	

##DHT_module

@pytest.mark.parametrize('input_data, expected',(
	(({'salon':12}, {'temp':23,'humidity':56}), {'salon':{'temp':23,'humidity':56}}),
	# (({'salon':12, 'WC':15}, {'temp':23,'humidity':56}), 
	# 	{'salon':{'temp':23,'humidity':56}, 'WC':{'temp':23,'humidity':56}}),
	))
def test_mocked_dict(input_data, expected, sql_obj_not_called, dht_obj):
	pin_dict, return_flask_dict = input_data
	# sql_obj = save_to_file.HandlerSQL
	sql_obj_not_called.fetch_all_data_from_temp = Mock()
	sql_obj_not_called.fetch_all_data_from_temp.return_value = pin_dict
	dht_obj.to_flask = Mock()
	dht_obj.to_flask.return_value = return_flask_dict
	from_method = dht_obj.dict_with_keys_as_room_names_and_dict_as_value()	
	assert expected == from_method

# SECONDARY_LOGIC_TO_CHECK METCHOD
@pytest.mark.parametrize('input_data, expected',(
	(['salon', 7], 10),
	(['WC', 8], 10),
	))
def test_secondary_logic_return_error_code_real_reads(input_data, expected, dht_obj):
	# real reads from sensors
	sensor_name, pin = input_data
	from_method = dht_obj.secondary_logic_to_check(sensor_name=sensor_name, pin=pin)	
	assert expected == from_method

@pytest.mark.parametrize('input_data, expected', (
	([None, None], 10),
	([20, None], 10),
	([30, None], 10),
	([110 , None],10),
	([90, 100],10),
	))
def test_secondary_logic_mocked(input_data, expected, dht_obj):
	# mocked method dht.read_retry check return error code		
	with patch.object(Adafruit_DHT, 'read_retry', return_value=input_data):
		from_method = dht_obj.secondary_logic_to_check()		
		assert expected == from_method
	
@pytest.mark.parametrize('input_data, expected', (
	([30, 60], [30, 60]),
	([40,30],[40,30]),
	([21,-13],[21,-13]),
	([90,60], [90,60]),
	))
def test_secondary_logic_mocked_without_err(input_data, expected, dht_obj):
	with patch.object(Adafruit_DHT, 'read_retry', return_value=input_data):
		from_method = dht_obj.secondary_logic_to_check()
		assert expected == from_method

#LOGIC METCHOD

@pytest.mark.parametrize('input_data, expected', (
	((30,30),(30,30)),
	((25, 50),(25, 50)),
	((90,-20), (90,-20)),	
	))
def test_logic_return_correct_data(input_data, expected, dht_obj):
	from_method = dht_obj.logic(data_tuple=input_data)
	assert expected == from_method

@pytest.mark.parametrize('input_data, expected',(
	((11,100),'test'),
	((11,50), 'test'),
	((32,100), 'test'),
	))
def test_logic_return_secondary_metchod(input_data, expected, dht_obj):
	with patch.object(dht_obj, 'secondary_logic_to_check', return_value='test'):
		from_method = dht_obj.logic(data_tuple=input_data)
		assert expected == from_method

# RECOGNICION_DEVICE

@pytest.mark.parametrize('input_data, expected', (
	((1, 'unknow'), 10),
	((2, 'unknow'), 10),
	((3, 'unknow'), 10),
	))
def test_rec_dev_ret_str(input_data, expected, dht_obj):
	pin, name = input_data
	from_method = dht_obj.recognicion_device(pin=pin, name=name)	
	assert from_method == expected	

@pytest.mark.parametrize('input_data, expected', (
	((40, 'unknow'), 10),
	((None, 'unknow'), 10),
	(('blah', 'unknow'), 10),
	))
def test_rec_dev_raises_err(input_data, expected, dht_obj):
	pin, name = input_data
	with pytest.raises(Exception):
		from_method = dht_obj.recognicion_device(pin=pin, name=name)

@pytest.mark.parametrize('input_data, expected', (
	((5,'unknow'), 10),
	((30,'unknow'), 10),
	))
def test_with_mock_ret_str(input_data, expected, dht_obj):
	pin, name = input_data
	with patch.object(Adafruit_DHT, 'read_retry', return_value=(None, None)):
		from_method = dht_obj.recognicion_device(pin=pin, name=name)
		assert from_method == expected


@pytest.mark.parametrize('input_data, expected', (
	((7, 'salon'), tuple),
	((12, 'm_pokój'), tuple),
	((16, 'kuchnia'), tuple),
	))
def test_with_correct_data_reco_dev(input_data, expected, dht_obj):
	pin, name = input_data
	from_method = dht_obj.recognicion_device(pin=pin, name=name)
	assert expected == type(from_method)

@pytest.mark.parametrize('input_data, expected', (
	((40, 50), (40, 50)),
	((30, 27), (30, 27)),
	((120, 40), 10)
	))
def test_with_mock_correct_data_reco_dev(input_data, expected, dht_obj):
	Adafruit_DHT.read_retry = Mock()
	Adafruit_DHT.read_retry.return_value = input_data
	from_method = dht_obj.recognicion_device(pin=7, name='whatever')
	assert expected == from_method
	Adafruit_DHT.read_retry.assert_called()


	
# TO FLASK

@pytest.mark.parametrize('input_data, expected', (
	((7,'salon',{'salon':{'temp':34,'humidity':60}}), {'temp':34,'humidity':60}),
	((9,'WC', {'salon':{'temp':34,'humidity':60}, 'WC':{'temp':35,'humidity':61}}), {'temp':35,'humidity':61}),
	))
@patch.object(dht_handler.DHT_Handler, 'recognicion_device', return_value=10) # pierwsza fałszywa (mokowana metoda)
@patch.object(dht_handler.DHT_Handler, 'add_token_error', return_value='do nothing') # druga fałszywa (mokowana metoda)
def test_with_mock_return_previous_data(mock_reco_dev, mock_add_err_tok, input_data, expected, dht_obj):
	pin, name, data_from_file = input_data
	from_method = dht_obj.to_flask(pin=pin, 
			sensor_name=name,
			data_from_file=data_from_file)		
	assert expected == from_method
	mock_reco_dev.assert_called()
	mock_add_err_tok.assert_called()

@pytest.mark.parametrize('input_data, expected', (
	((7, 'salon', (63,40)), {'temp': 40, 'humidity':63}),
	((22, 'whatever', (70,12)), {'temp': 12, 'humidity':70}),
	))
def test_with_mock_return_correct_data(input_data, expected, dht_obj):
	pin, name, return_value = input_data
	dht_obj.remove_token_error = Mock()
	dht_obj.remove_token_error.return_value = 'do nothing'
	dht_obj.recognicion_device = Mock()
	dht_obj.recognicion_device.return_value = return_value
	from_method = dht_obj.to_flask(pin=pin, sensor_name=name, data_from_file={})
	assert expected == from_method
	dht_obj.remove_token_error.assert_called()
	dht_obj.recognicion_device.assert_called()


# Remove token Error

@pytest.mark.parametrize('input_data', (
	({'salon':0, 'WC':0,'outside':0}),
	({'salon':-30, 'WC':2,'outside':23}),
	({'salon':None, 'WC':0,'outside':0}),
	({'outside':0}),
	({'salon':None, 'WC':'cokolwiek'}),
	({}),
	))
def test_with_mock_remove_token(input_data, sql_obj_not_called, dht_obj):
	expected = tuple(input_data.values())
	sql_obj_not_called.fetch_data_from_tokens = Mock()
	sql_obj_not_called.fetch_data_from_tokens.return_value = input_data
	sql_obj_not_called.update_data_tokens = Mock()
	sql_obj_not_called.update_data_tokens.return_value = 'do nothing'
	from_method = dht_obj.remove_token_error(sensor_name='')
	assert from_method == expected
	sql_obj_not_called.fetch_data_from_tokens.assert_called()
	sql_obj_not_called.update_data_tokens.assert_called()

# add token_error
@pytest.mark.parametrize('input_data, expected',(
	(({'salon':0, 'WC':0,'outside':0}, 'WC'), (0,1,0)),
	(({'salon':9, 'WC':0,'outside':0}, 'salon'), (10,0,0)),
	(({}, 'salon'),()),
	(({'salon':'stri', 'WC':0,'outside':0}, 'salon'), (None,0,0)),
	(({'salon':2, 'WC':0,'outside':0}, 'everythig'), (2,0,0)),
	))
def test_with_mock_add_token(input_data, expected, sql_obj_not_called, dht_obj):
	dict_data, sensor_name = input_data
	sql_obj_not_called.fetch_data_from_tokens = Mock()
	sql_obj_not_called.fetch_data_from_tokens.return_value = dict_data
	sql_obj_not_called.update_data_tokens = Mock()
	sql_obj_not_called.update_data_tokens.return_value = 'do nothing'
	from_method = dht_obj.add_token_error(sensor_name=sensor_name)
	assert from_method == expected
	sql_obj_not_called.fetch_data_from_tokens.assert_called()
	sql_obj_not_called.update_data_tokens()

# update

def test_update(sql_obj_not_called, dht_obj):
	input_data = {'salon': {'temp':20, 'humidity':40}, 'maly_pokoj': {'temp':20, 'humidity':60}}
	expected = input_data	
	dht_obj.dict_with_keys_as_room_names_and_dict_as_value = Mock()
	dht_obj.dict_with_keys_as_room_names_and_dict_as_value.return_value= input_data
	sql_obj_not_called.update_data_in_temperature = Mock()
	sql_obj_not_called.update_data_in_temperature.return_value = 'do nothing'
	from_method = dht_obj.update()
	assert from_method == expected	
	dht_obj.dict_with_keys_as_room_names_and_dict_as_value.assert_called()
	sql_obj_not_called.update_data_in_temperature.assert_called()



###### CLASS SimpleyTesting

# single sensor

@pytest.mark.parametrize('input_data', (
	((11, 7, 'salon')),
	((22, 4, 'outside')),
	))
def test_single_sensor_correct_data(input_data, simpleyTestingCls):
	sensor_name, pin, room_name = input_data
	from_method = simpleyTestingCls.single_sensor(
		sensor=sensor_name, pin=pin, name=room_name)

@pytest.mark.parametrize('input_data', (
	((12, 7, 'salon')), # wrong sensor test
	((11, 41,'salon')), # wrong pin > 31	
	))
def test_single_sensor_raise_err(input_data, simpleyTestingCls):
	sensor, pin, name = input_data
	with pytest.raises(Exception):
		from_method = simpleyTestingCls.single_sensor(sensor=sensor, pin=pin,name=name)	

# all sensors in row

def test_all_sensors_in_row(SQL_obj, simpleyTestingCls):
	input_dict = SQL_obj.names_and_pins_default
	from_method = simpleyTestingCls.all_sensors_in_row(sensors_dict=input_dict)


##### FLASK HOME (Main file)

#temperature backgound
@pytest.mark.parametrize('input_data', (
	({'salon':{'temp':34,'humidity':60}, 
		'WC': {'temp':24,'humidity':29},
		'outside':{'temp':-2,'humidity':98}}),
	))
def test_temp_bg(input_data, sql_obj_not_called):
	expected = json.dumps(input_data)
	sql_obj_not_called.fetch_all_data_from_temp = Mock()
	sql_obj_not_called.fetch_all_data_from_temp.return_value = input_data
	from_method = flask_home.temp_background()
	assert from_method == expected
	sql_obj_not_called.fetch_all_data_from_temp.assert_called()

@pytest.mark.parametrize('input_data', (
	([1,2,3,4]),
	({1,2,3,4}),
	('some_string'),
	(23),
	))
def test_temp_bg_raise_err(input_data, sql_obj_not_called):
	sql_obj_not_called.fetch_all_data_from_temp = Mock()
	sql_obj_not_called.fetch_all_data_from_temp.return_value = input_data	
	with pytest.raises(Exception):
		from_method = flask_home.temp_background()
	sql_obj_not_called.fetch_all_data_from_temp.assert_called()

@pytest.mark.parametrize('input_data', (
	({'salon':{'temp':34,'humidity':60}, 
		'WC': {'temp':24,'humidity':29},
		'outside':{'temp':-2,'humidity':98}}),
	))
def test_temp_return_correct_data(input_data, sql_obj_not_called, dht_obj_not_called):
	expected = json.dumps(input_data)
	sql_obj_not_called.fetch_all_data_from_temp = Mock()
	sql_obj_not_called.fetch_all_data_from_temp.return_value = ''
	dht_obj_not_called.dict_with_keys_as_room_names_and_dict_as_value = Mock()
	dht_obj_not_called.dict_with_keys_as_room_names_and_dict_as_value.return_value = input_data
	from_method = flask_home.temp_background()
	assert from_method == expected
	dht_obj_not_called.dict_with_keys_as_room_names_and_dict_as_value.assert_called()
	sql_obj_not_called.fetch_all_data_from_temp.assert_called()


# lighting relays loader
@patch.object(virtual_relay.Relays_class, 'lighting_handler', return_value="don't call function")
def test_lighting_relays_call(mock_v_r):
	from_method = flask_home.lighting_relays_loader()
	assert from_method

# set time request handling

def test_set_time():
	# próba za pomocą patch.mock.Mock()
	flask.request = Mock()

	# from_method = flask_home.
	# mocked_f.headers.get.assert_called()


##### SAVE TO FILE MODULE

## Handler File Class

# create container

@pytest.mark.parametrize('input_data, expected', (
	((r'/home/pi/Desktop/env/fl/src/logic_script', False), ValueError),
	((r'/home/pi/Desktop/env/fl/src/logic_script/test.txt', False), 'container was created!!'),
	((r'/home/pi/Desktop/env/fl/src/logic_script/test.txt', True), 'container exist!!'),
	))
def test_create_container(input_data, expected,  handler_file_obj):
	path, bool_val = input_data
	mock_f = os.path
	mock_f.isfile = Mock(return_value=bool_val)
	if type(expected) == str:
		from_method = handler_file_obj.create_container(path=path)
		if os.path.isfile(path):
			os.remove(path)
		assert from_method
	else:
		with pytest.raises(Exception):
			from_method = handler_file_obj.create_container(path=path)		
	
# save to json

def test_save_to_json(handler_file_obj):
	path = r'/home/pi/Desktop/env/fl/src/logic_script/test.txt'
	content = {'somthing': 'lol'}
	from_method = handler_file_obj.save_to_json(path=path, content=content)
	assert from_method
	if os.path.isfile(path):
		os.remove(path)


# load from json
@pytest.mark.parametrize('input_key', (
	(None),		
	('salon'),
	))
def test_load_from_json(input_key, test_json_file, handler_file_obj):
	path, content = test_json_file		
	from_method = handler_file_obj.load_from_json(path=path, key=input_key)
	if not input_key :
		assert from_method == content
	else:
		assert from_method == content[input_key]


@pytest.mark.parametrize('input_data, content', (
	([r'/home/pi/Desktop/env/fl/src/logic_script/test.json', None], ''),
	([r'/home/pi/Desktop/env/fl/src/logic_script/test.json', 'blabla'],
		{'salon':1, 'wc':2}),
	([r'/home/pi/Desktop/env/fl/src/logic_script/test.json', 'salon'],
		'common string'),
	([r'/home/pi/Desktop/env/fl/src/logic_script/test.json', 'blabla'],
		'{"blaca"}'),
	([r'/home/pi/Desktop/env/fl/src/logic_script/test.json', 'blabla'],
		'{blaca}'),
	))
def test_load_from_json_raise_err(input_data, content, handler_file_obj):
	path, key = input_data
	def create_file(path, content):
		with open(path, 'w') as f:
			content = json.dumps(content)
			f.write(content)		
	create_file(path=path, content=content)
	with pytest.raises(Exception):
		from_method = handler_file_obj.load_from_json(path=path, key=key)
	os.remove(path)

# update file
@pytest.mark.parametrize('input_data', (
	(['/home/pi/Desktop/env/fl/src',{'salon': 12, 'maly_pokoj':123, 'WC': 900},'WC','changed value', None]),
	(['/home/pi/Desktop/env/fl/src',{'salon': 12, 'maly_pokoj':123, 'WC': {'temp': 20, 'humidity': 99}},'WC','changed value', 'temp']),
	))
def test_update_file(input_data, handler_file_obj, handler_file_not_called):
	path, mocked_content, key, swap_content, key2 = input_data
	handler_file_not_called.load_from_json = Mock()
	handler_file_not_called.load_from_json.return_value = mocked_content
	handler_file_not_called.save_to_json = Mock()
	handler_file_not_called.save_to_json.return_value = 'do nothing'
	from_method = handler_file_obj.update_file(path=path, 
		key=key, content=swap_content, key2=key2)
	assert from_method == swap_content		
	handler_file_not_called.save_to_json.assert_called()		
	handler_file_not_called.load_from_json.assert_called()
	

@pytest.mark.parametrize('input_data', (
	(['/home/pi/Desktop/env/fl/src',{'salon': 12, 'maly_pokoj':123, 'WC': 900}, 'bla', 'changed value', None]),
	(['/home/pi/fake/dir',{'salon': 12, 'maly_pokoj':123, 'WC': 900}, 'bla', 'changed value', None]),
	(['/home/pi/Desktop/env/fl/src', {'salon': 12, 'maly_pokoj':123, 'WC': 900}, 'salon', '', None]),
	))
def test_update_file_raise_err(input_data, handler_file_obj, handler_file_not_called):
	path, mocked_content, key, swap_content, key2 = input_data
	handler_file_not_called.load_from_json = Mock()
	handler_file_not_called.load_from_json.return_value = mocked_content
	handler_file_not_called.save_to_json = Mock()
	handler_file_not_called.save_to_json.return_value = 'do nothing'
	with pytest.raises(Exception):
		from_method = handler_file_obj.update_file(path=path, key=key, content=swap_content, key2=key2)
	

# delete data from file

@pytest.mark.parametrize('input_data', (
	(['/home/pi/Desktop/env/fl/src', 'salon', {'salon':23, 'WC':34, 'outside': -1}]),
	))
def test_delete_data_from_file(input_data, handler_file_not_called, handler_file_obj):
	path, key, fake_content = input_data		
	handler_file_not_called.load_from_json = Mock()
	handler_file_not_called.load_from_json.return_value = fake_content
	handler_file_not_called.save_to_json = Mock()
	handler_file_not_called.save_to_json.return_value = 'do nothing'	
	from_method = handler_file_obj.delete_data_from_file(path=path, key=key)	
	assert from_method == fake_content
	handler_file_not_called.load_from_json.assert_called()
	handler_file_not_called.save_to_json.assert_called()


@pytest.mark.parametrize('input_data', (
	(['/home/pi/Desktop/env/fl/src', 'fakeKey', {'salon':23, 'WC':34, 'outside': -1}]),
	(['/fake/directory', 'WC', {'salon':23, 'WC':34, 'outside': -1}]),
	))
def test_delete_data_raise_err(input_data, handler_file_not_called, handler_file_obj):
	path, key, fake_content = input_data
	handler_file_not_called.load_from_json = Mock()
	handler_file_not_called.load_from_json.return_value = fake_content
	handler_file_not_called.save_to_json = Mock()
	handler_file_not_called.save_to_json.return_value = 'do nothing'
	with pytest.raises(Exception):
		from_method = handler_file_obj.delete_data_from_file(path=path, key=key)
		handler_file_not_called.load_from_json.assert_called()
		handler_file_not_called.save_to_json.assert_called()

# search key
@pytest.mark.parametrize('input_data, expected', (
	([{'a':1, 'd': {'mama': 12, 'dama':200}, 'c': 23}, 'dama'], [{'mama': 12, 'dama':200}]),
	([{'a':1, 'd': {'mama': 12, 'dama':200}, 'c': 23, 'dama':{'tak':1, 'nie':2}}, 'dama'], [{'mama': 12, 'dama':200}, 'dama']),
	))
def test_search_key(input_data, expected,  handler_file_obj):	
	dict_container, s_key = input_data	
	from_method = handler_file_obj.recur_search_key(d=dict_container, s_key=s_key)
	assert from_method == expected

@pytest.mark.parametrize('input_data', (
	(['str here', 'any_key']),
	([123, 'any_key']),

	))
def test_search_key_raise_err(input_data, handler_file_obj):
	d_content, key = input_data
	with pytest.raises(Exception):
		from_method = handler_file_obj.recur_search_key(d=d_content, s_key=key)
	



# recognizon table exists
@pytest.mark.parametrize('input_data', (
	(True),
	(False),
	))
def test_recognize_exists_table(input_data, cursor, table_temperature_cursor, SQL_obj):	
	if input_data:
		table_name = 'sockets'
		from_method = SQL_obj.recognize_if_table_in_db_exist(cursor=cursor, table_name=table_name)
		assert from_method == True
	else:
		table_name = 'temperature_humidity'
		from_method = SQL_obj.recognize_if_table_in_db_exist(cursor=table_temperature_cursor, table_name=table_name)
		assert from_method == False


@pytest.mark.parametrize('input_data', (
	([23, 'somthing']),
	([sqlite3.Cursor, 412])
	))
def test_recognize_existance_table_raise_err(input_data, SQL_obj):
	cursor, table_name = input_data
	with pytest.raises(Exception):
		from_method = SQL_obj.recognize_if_table_in_db_exist(cursor=cursor, table_name=table_name)

# fetch columns names

def test_fetch_column_names(table_temperature, SQL_obj):
	cursor = table_temperature
	table_name = 'temperature_humidity'
	from_method = SQL_obj.fetch_column_names(cursor=cursor, table_name=table_name)
	expected = ['id','salon', 'maly_pokoj', 'kuchnia','WC', 'outside']
	assert from_method == expected


@pytest.mark.parametrize('input_data', (
	(['somestring', ['abcd'], False]),
	([sqlite3.Cursor, ['abcd'], False]),
	([sqlite3.Cursor, 'some_table', False]),
	(['somthing', 'some_table', True]),
	(['somthing', '', True]),
	))
def test_fetch_column_names_raise_err(input_data, table_sockets, SQL_obj):
	cursor, table_name, flag = input_data
	with pytest.raises(Exception):
		if flag:
			SQL_obj.fetch_column_names(cursor=table_sockets, table_name=table_name)
		else:
			SQL_obj.fetch_column_names(cursor=cursor, table_name=table_name)	
	

# create table
def test_create_table(cursor, SQL_obj):	
	table_sheet = SQL_obj.table_errors_tokens_and_seted_temperature()
	from_method = SQL_obj.create_table(cursor=cursor, table_sheet=table_sheet)		
	assert from_method

def test_table_sheets(cursor, SQL_obj):
	tables = {SQL_obj.table_errors_tokens_and_seted_temperature: ['id', 'salon', 'maly_pokoj', 'kuchnia', 'WC', 'outside'],
				SQL_obj.table_temperature: ['id', 'salon', 'maly_pokoj', 'kuchnia', 'WC', 'outside'],
				SQL_obj.table_sockets: ['id','turn_on', 'turn_off'],
				}
	for key, expected in tables.items():
		table_sheet = key()			
		from_method = SQL_obj.create_table(cursor=cursor, table_sheet=table_sheet)		
		assert SQL_obj.fetch_column_names(cursor=cursor, table_name=table_sheet[0]) == expected


### insert data to table
# insert temp value to table
def test_insert_data_to_temperature(table_temperature, SQL_obj):	
	tuple_int = tuple(range(1,6))
	# last row id 
	expected = 1
	from_method = SQL_obj.insert_data_to_temperature(conn=table_temperature, tuple_int=tuple_int)
	assert from_method == expected


@pytest.mark.parametrize('input_data', (
	(list(range(1,6))),
	(tuple(range(1,10))),
	))
def test_insert_data_to_temperature_raise_err(input_data, table_temperature, SQL_obj):
	with pytest.raises(Exception):
		from_method = SQL_obj.insert_data_to_temperature(conn=table_temperature, tuple_int=input_data)

# insert sockets value to table

@pytest.mark.parametrize('input_data, expected', (
	(('00:29','12:00'),1),
	(('23:29','12:00'),1),
	))
def test_insert_data_to_sockets_table(input_data, expected, table_sockets, SQL_obj):
	from_method = SQL_obj.insert_data_to_sockets_table(conn=table_sockets, times=input_data)
	assert from_method == expected


@pytest.mark.parametrize('input_data', (
	(['not_conn_obj', ('23:29','12:00'), False]),
	(['will_be_changed_to_obj', ['23:29','12:00'], True]),
	(['will_be_changed_to_obj', ('23:290','12:00'), True]),
	(['will_be_changed_to_obj', ('23:290','da12:00'), True]),
	(['will_be_changed_to_obj', ('23:291d','112:00'), True]),
	(['will_be_changed_to_obj', ('!@#23:290','2:00'), True]),
	(['will_be_changed_to_obj', ('3:290','12:00'), True]),
	(['will_be_changed_to_obj', ('93:29','12:00'), True]),
	(['will_be_changed_to_obj', ('12:29','12:60'), True]),
	))
def test_insert_data_to_sockets_table_raise_err(input_data, table_sockets, SQL_obj):
	conn, times, flag = input_data
	with pytest.raises(Exception):
		if flag:
			conn = table_sockets
			from_method = SQL_obj.insert_data_to_sockets_table(conn=conn, times=times)
		else:
			from_method = SQL_obj.insert_data_to_sockets_table(conn=conn, times=times)

# insert token to table
@pytest.mark.parametrize('input_data, expected', (
	([(23,20,21,19, 12), True], 1),
	([(10,20,30,40,50), False], 1)	

	))
def test_insert_token_to_table(input_data, table_tokens, expected, SQL_obj):
	tokens_int, seted_temperature = input_data
	if seted_temperature:
		from_method = SQL_obj.insert_data_token_table(conn=table_tokens, tokens_int=tokens_int, seted_temperature=seted_temperature)
		assert from_method == expected
	else:
		from_method = SQL_obj.insert_data_token_table(conn=table_tokens, tokens_int=tokens_int, seted_temperature=False)
		assert from_method == expected

@pytest.mark.parametrize('input_data', (
	([(1,2,3,4), False]),
	([[1,2,3,4], False]),
	([[1,2,3,4,5], False]),
	([123, False]),
	(False, False),
	(True, False),
	(False, False),
	([True, (10,20,30,40,50)]),	
	))
def test_insert_token_to_table_raise_err(input_data, table_tokens, SQL_obj):
	tokens_int, seted_temperature = input_data
	with pytest.raises(Exception):
		from_method = SQL_obj.insert_data_token_table(conn=table_tokens, tokens_int=tokens_int, seted_temperature=seted_temperature)

## update

# update data in temperature
# @pytest.mark.parametrize('input_data', (
# 	([(10,20,30,40,50), True]),
# 	))
# def test_update_data_in_temp(input_data, SQL_obj):
# 	temp_or_humidity, temperature= input_data
# 	from_method = SQL_obj.update_data_in_temperature(temp_or_humidity=temp_or_humidity, temperature=temperature)
# 	pass



	


	
