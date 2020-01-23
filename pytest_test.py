from logic_script import dht_handler, save_to_file
room_names = save_to_file.HandlerFile().room_names
import pytest, flask_home, os, Adafruit_DHT
from unittest.mock import patch
from unittest.mock import Mock


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

## SQL
	## tbl temperature_humidity


@pytest.mark.parametrize('expected',(
	(dict),
	(room_names),
	))
def test_fetched_data(expected, SQL_obj):	
	data = SQL_obj.fetch_all_data_from_temp(temperature_dict=True)
	if expected == dict:
		assert type(data) == dict
	else:
		data = list(data.keys())                                                                                                                                                                                                                                                                                                                                                                                                                       
		assert expected == data

def test_initial_fetched_data(SQL_obj):	
	data = SQL_obj.fetch_all_data_from_temp()	
	assert data


def test_return_list(SQL_obj):	
	data = SQL_obj.fetch_all_data_from_temp()
	assert type(data) == list


def test_room_names_are_correct(SQL_obj):	
	fetched_list_with_tuples = SQL_obj.fetch_all_data_from_temp()	
	temps, humidity, _ =  [tup[1:] for tup in fetched_list_with_tuples]
	list_with_temps_and_humidity = [{'temp':temp, 'humidity': hum} 
									for temp, hum in zip(temps, humidity)]
	ans = dict(zip(room_names, list_with_temps_and_humidity))
	assert ans == SQL_obj.fetch_all_data_from_temp(temperature_dict=True)

def test_fetch_all_data_from_temp_return_choosen_row(SQL_obj):
	method = SQL_obj.fetch_all_data_from_temp(row=3)
	expected = tuple(SQL_obj.names_and_pins_default.values())
	assert method == expected


def test_initials_tbl_in_db_method(SQL_obj):	
	expected = 3
	fetched_data = SQL_obj.fetch_all_data_from_temp()
	assert expected == len(fetched_data)
	## other TBL

def test_names_and_pins_output_data_is_dict(SQL_obj):
	from_method = SQL_obj.fetch_all_data_from_temp(pin_dict=True)
	expected = dict
	assert expected == type(from_method)

def test_names_and_pins_correct_output_data(SQL_obj):
	from_method = SQL_obj.fetch_all_data_from_temp(pin_dict=True)
	expected = SQL_obj.names_and_pins_default
	assert expected == from_method


##CSV
@pytest.mark.parametrize('time_examples',(
	(['23-10-2019,08:00', '24-10-2019,10:00', '25-10-2019,14:00']),
	(['30-10-2019,01:00', '31-10-2019,22:00', '31-10-2019,11:00']),
	))	
def test_saved_data_to_csv_main_file(csv_in_class, backend, time_examples):
# create and save data to file 	
	triggers = csv_in_class.TRIGGER_HOURS
	for full_time in time_examples:
		csv_in_class.save_temp_to_csv_handler(path=test_path, full_time=full_time)
		f = backend.save_to_file()
		_, expected = save_to_file.CSV_Class(
				backend_file=f).read_csv(close_file=True)			
	else:
		f = backend.save_to_file()
	_, rows = save_to_file.CSV_Class(
		backend_file=f).read_csv(close_file=True)
	assert expected == rows


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

# @pytest.mark
# def test_with_mock_raise_err_pin_incorrect_pin(dht_obj):
# 	pin, name = 34, 'unknow'
# 	# przechwytuje exception		
# 	with pytest.raises(Exception):
# 		from_method = dht_obj.recognicion_device(pin=pin, name=name)

		

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

# def test_with_mock_remove_token(sql_obj_not_called, dht_obj):
# 	sql_obj_not_called.fetch_data_from_tokens = Mock()
# 	sql_obj_not_called.fetch_data_from_tokens.return_value = 'do nothing'
	
	






	



