from logic_script import dht_handler, save_to_file
room_names = save_to_file.HandlerFile().room_names
import pytest, flask_home


## SQL

@pytest.fixture
def SQL_obj():
	SQL_obj = save_to_file.HandlerSQL()
	return SQL_obj

@pytest.mark.parametrize('expected',(
	(dict),
	(room_names),
	))
def test_fetched_data(expected, SQL_obj):
	# SQL_obj = save_to_file.HandlerSQL()
	data = SQL_obj.fetch_all_data_from_temp(show_dict=True)
	if expected == dict:
		assert type(data) == dict
	else:
		data = list(data.keys())                                                                                                                                                                                                                                                                                                                                                                                                                       
		assert expected == data



def test_initial_fetched_data(SQL_obj):
	# SQL_obj = save_to_file.HandlerSQL()
	data = SQL_obj.fetch_all_data_from_temp()	
	assert data


def test_return_list(SQL_obj):
	# SQL_obj = save_to_file.HandlerSQL()
	data = SQL_obj.fetch_all_data_from_temp()
	assert type(data) == list


def test_room_names_are_correct(SQL_obj):
	# SQL_obj = save_to_file.HandlerSQL()
	fetched_list_with_tuples = SQL_obj.fetch_all_data_from_temp()	
	temps, humidity =  [tup[1:] for tup in fetched_list_with_tuples]
	list_with_temps_and_humidity = [{'temp':temp, 'humidity': hum} 
									for temp, hum in zip(temps, humidity)]
	ans = dict(zip(room_names, list_with_temps_and_humidity))
	assert ans == SQL_obj.fetch_all_data_from_temp(show_dict=True)

##DHT_module


@pytest.mark.parametrize('expected',(
	(dict),
	))
def test_is_dict(expected):
	dht_obj = dht_handler.DHT_Handler()
	from_method = dht_obj.dict_with_keys_as_room_names_and_dict_as_value()	
	assert expected == type(from_method)



# flask_home

@pytest.mark.parametrize('expected',(
	(str), #json format in string
	))
def test_temp_background(expected):
	from_method = flask_home.temp_background()	
	assert expected == type(from_method)





