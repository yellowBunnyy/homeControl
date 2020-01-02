from logic_script import dht_handler, save_to_file
room_names = save_to_file.HandlerFile().room_names
import pytest, flask_home, os

test_path = os.path.join(os.getcwd(),'logic_script','test_csv.csv')

@pytest.fixture(name='SQL_obj')
def SQL_obj_class():
	SQL_obj = save_to_file.HandlerSQL()
	return SQL_obj

@pytest.fixture(name='csv_in_class')
def csv_cls():
	csv_obj = save_to_file.HandlerCsv()
	return csv_obj

@pytest.fixture(name='pure_csv')
def pure_csv(backend):
	csv_obj = save_to_file.CSV_Class(backend_file=backend.save_to_file())
	return csv_obj

@pytest.fixture(name='backend')
def create_backend():
	backend_obj = save_to_file.FileHandler(path=test_path) 
	return backend_obj

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


# @pytest.mark.parametrize('expected',(
# 	(dict),
# 	))
# def test_is_dict(expected):
# 	dht_obj = dht_handler.DHT_Handler()
# 	from_method = dht_obj.dict_with_keys_as_room_names_and_dict_as_value()	
# 	assert expected == type(from_method)



# # flask_home

# @pytest.mark.parametrize('expected',(
# 	(str), #json format in string
# 	))
# def test_temp_background(expected):
# 	from_method = flask_home.temp_background()	
# 	assert expected == type(from_method)





