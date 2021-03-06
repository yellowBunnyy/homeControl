import unittest, random, Adafruit_DHT as dht
from logic_script import dht_handler, save_to_file
import flask_home, os, datetime, time



class Basic_tests(unittest.TestCase):
   # obj_convert_test = convert_time.TimeConvertet()
	# flask_obj = flask_home
	# obj_dht_handler = flask_obj.dht_handler_obj
	# obj_SQL_class = obj_dht_handler.SQL_obj

	def flat_list(self, data):
			'''recur func. Flating or (vectorize) x dimension matrix'''
			container = []
			for val in data:
				if type(val) == int:
					container += [val]
				else:
					container += self.flat_list(val)
			return tuple(container)

	def test_room_names_in_dict(self):
		room_names = ["salon","maly_pokoj","kuchnia","WC","outside"]
		SQL_obj = save_to_file.HandlerSQL()
		data = SQL_obj.fetch_all_data_from_temp(show_dict=True)
		only_room_keys_list = list(data.keys())
		flag = room_names == only_room_keys_list
		self.assertTrue(flag)

	def test_room_names_are_correct(self):
		room_names = ["salon","maly_pokoj","kuchnia","WC","outside"]
		SQL_obj = save_to_file.HandlerSQL()
		fetched_list_with_tuples = SQL_obj.fetch_all_data_from_temp()	
		temps, humidity =  [tup[1:] for tup in fetched_list_with_tuples]
		list_with_temps_and_humidity = [{'temp':temp, 'humidity': hum} 
										for temp, hum in zip(temps, humidity)]
		expected = dict(zip(room_names, list_with_temps_and_humidity))
		from_method = SQL_obj.fetch_all_data_from_temp(show_dict=True)
		flag = expected == from_method
		self.assertTrue(flag)

	# def test_create_tbl_temperature(self):
	# 	flag = self.obj_SQL_class.recognize_if_table_in_db_exist(table_name='temperature_humidity')
	# 	self.assertTrue(not flag)


	# def test_fetch_data_tbl_temperature(self):
	# 	ans = tuple([0]*10)
	# 	sql_method = [tup[1:] for tup in self.obj_SQL_class.fetch_all_data_from_temp()]

	# 	flated_data = self.flat_list(sql_method)
	# 	flag = ans == flated_data
	# 	print(ans ,' | ', flated_data)
	# 	self.assertTrue(flag)


	# def test_update_data_tbl_temperature(self):
	# 	ans = tuple(range(10))
	# 	self.obj_SQL_class.update_data_in_temperature(
	# 		temp_or_humidity=ans[:len(ans)//2])
	# 	self.obj_SQL_class.update_data_in_temperature(
	# 		temp_or_humidity=ans[len(ans)//2:], temperature=False)
	# 	fetched_data = [tup[1:] for tup in self.obj_SQL_class.fetch_all_data_from_temp()]
	# 	to_compare = self.flat_list(fetched_data)
	# 	flag = ans == to_compare
	# 	print(ans, ' | ', to_compare)
	# 	self.assertTrue(flag)

	# def test_update_data_tbl_temperature_rdm(self):
	# 	for _ in range(100):
	# 		ans = tuple(random.choices(range(-200,200), k=10))
	# 		temp, humidity = tuple(ans[:len(ans)//2]),  tuple(ans[len(ans)//2:])
	# 		self.obj_SQL_class.update_data_in_temperature(
	# 			temp_or_humidity=temp)
	# 		self.obj_SQL_class.update_data_in_temperature(
	# 			temp_or_humidity=humidity, temperature=False)
	# 		fetched_data = [tup[1:] for tup in self.obj_SQL_class.fetch_all_data_from_temp()]
	# 		to_compare = self.flat_list(fetched_data)
	# 		flag = ans == to_compare
	# 		print(ans, ' | ', to_compare)
	# 		self.assertTrue(flag)




	# def test_drop_tbl(self):
	# 	table_name = 'temperature_humidity'
	# 	self.obj_SQL_class.drop_table(table_name=table_name)








	# def initial_db_and_tables(self, amt):
	# 	data_from_initial = self.obj_SQL_class.initial_table_in_db(rows_amount=amt)
	# 	rows_amount = data_from_initial['rows_amount']
	# 	table_names = data_from_initial['table_names']
	# 	return rows_amount, table_names

	# def test_fetch_data_sockets_withoun_rows(self,):
	# 	tbl = obj_SQL_class.SQL_TABELS_NAMES[0] # sockets tbl
	# 	ans = [('00:13', '19:47'),('08:10', '13:54')]
	# 	f = main_fetch_data_from_db()

	
	# def test_main_fetch_data(self):
	# 	tbl = self.obj_SQL_class.SQL_TABELS_NAMES[0]
	# 	ans = [('00:13', '19:47'),('08:10', '13:54')]
	# 	print(tbl)
	# 	f = self.obj_SQL_class.main_fetch_data_from_db(table_name=tbl)
	# 	print(f)
	# 	flag = ans == f
	# 	print(f'{f} {"==" if flag else "!="} {ans}')
	# 	self.assertTrue(flag)


		



	# def test_correctly_imputted_tokens_table_row1(self):
	# 	ans = tuple(range(1,6))
	# 	self.obj_SQL_class.update_data_tokens(tokens_int=ans, row=1)
	# 	fetched_data = tuple(self.obj_SQL_class.fetch_data_from_tokens(row=1))
	# 	flag = ans == fetched_data
	# 	print(f'{fetched_data} {"==" if flag else "!="} {ans}')
	# 	self.assertTrue(flag)

	# def test_correctly_imputted_tokens_table_row2(self):
	# 	ans = tuple(range(10,15))
	# 	self.obj_SQL_class.update_data_tokens(tokens_int=ans, row=2)
	# 	fetched_data = tuple(self.obj_SQL_class.fetch_data_from_tokens(row=2))
	# 	flag = ans == fetched_data
	# 	print(f'{fetched_data} {"==" if flag else "!="} {ans}')
	# 	self.assertTrue(flag)

	# def test_random_entered_token_values_and_rows(self):
	# 	n = 5
	# 	for _ in range(10):
	# 		rdm_value_in_tup = tuple(random.choices(range(-20,20), k=n))
	# 		rdm_row = random.choice(range(1,3))
	# 		self.obj_SQL_class.update_data_tokens(tokens_int=rdm_value_in_tup,
	# 											row=rdm_row)
	# 		fetched_data = tuple(self.obj_SQL_class.fetch_data_from_tokens(row=rdm_row))
	# 		flag = rdm_value_in_tup == fetched_data
	# 		print(f'{fetched_data} {"==" if flag else "!="} {rdm_value_in_tup}')
	# 		self.assertTrue(flag)
	


	
	# def test_db_has_been_created(self,):
	# 	'''whether db has been created'''		
	# 	# initial creating database with creating tables
	# 	db_name = os.path.split(self.obj_SQL_class.STATIC_DB_ERRORS_PATH)[-1]
	# 	print(db_name)
	# 	folder_content = os.listdir(os.path.join(os.getcwd(),'logic_script'))
	# 	flag_if_exist = True if db_name in folder_content else False
	# 	self.assertTrue(flag_if_exist)

	# def test_default_value_tokens_table(self):
	# 	r_amt = 2
	# 	rows, tb_names = self.initial_db_and_tables(amt=r_amt)
	# 	answer = [0,] * (r_amt * 5)
	# 	def flat_list(data):
	# 		'''recur func. Flating or (vectorize) x dimension matrix'''
	# 		container = []
	# 		for val in data:
	# 			if type(val) == int:
	# 				container += [val]
	# 			else:
	# 				container += flat_list(val)
	# 		return container
	# 	#list with x tupels
	# 	x_dimension_list= self.obj_SQL_class.fetch_data_from_tokens()
	# 	flat_data = flat_list(x_dimension_list)
	# 	flag = flat_data == answer
	# 	print(f'{len(flat_data)} {"==" if flag else "!="} {len(answer)}')
	# 	self.assertTrue(flag)

	# def test_correctly_inputted_data_socket_row1(self):
	# 	answer = ['10:00','12:31']
	# 	updata_date = tuple(answer)
	# 	self.obj_SQL_class.update_data_in_sockets_table(times=updata_date,row_id=1)
	# 	#list with two tuples
	# 	row_one_data = self.obj_SQL_class.fetch_all_data_from_sockets(row=1)[1:]		
	# 	is_same_flag = row_one_data == updata_date
	# 	print(f"{row_one_data} {'==' if is_same_flag else '!=' } {updata_date}")
	# 	self.assertTrue(is_same_flag)

	# def test_correctly_inputted_data_socket_row2(self):
	# 	answer = ['11:00','22:05']
	# 	updata_date = tuple(answer)
	# 	self.obj_SQL_class.update_data_in_sockets_table(times=updata_date,row_id=2)
	# 	#list with two tuples
	# 	row_one_data = self.obj_SQL_class.fetch_all_data_from_sockets(row=2)[1:]		
	# 	is_same_flag = row_one_data == updata_date
	# 	print(f"{row_one_data} {'==' if is_same_flag else '!=' } {updata_date}")
	# 	self.assertTrue(is_same_flag)

	# def test_random_hours_and_rows(self):
	# 	def generate_times_tuple():			
	# 		gen = lambda x: str(random.choice(range(x))).zfill(2)
	# 		convert_to_str = lambda s: time.strptime(s, '%H:%M')
	# 		while True:
	# 			turn_on, turn_off = ['{}:{}'.format(gen(24), gen(60))
	# 							 for _ in range(2)]
	# 			obj_turn_on, obj_turn_off = [convert_to_str(t) for t in [turn_on, turn_off]]
	# 			if obj_turn_on < obj_turn_off:
	# 				# print(turn_on, turn_off)                
	# 				return turn_on, turn_off

	# 	for _ in range(100):
	# 		row = random.choice(range(1,3))
	# 		answer = generate_times_tuple()
	# 		# print(row)
	# 		self.obj_SQL_class.update_data_in_sockets_table(times=answer, row_id=row)
	# 		row_one_data = self.obj_SQL_class.fetch_all_data_from_sockets(row=row)
	# 		is_same_flag = row_one_data == answer
	# 		print(f"{row_one_data} {'==' if is_same_flag else '!=' } {answer}")
	# 		self.assertTrue(is_same_flag)

	# def test_create_db(self):
	# 	self.obj_SQL_class.recognize_if_table_in_db_exist(
	# 		table_name=self.table_name_sockets)

	# def test_read_from_db(self):
	# 	print(self.obj_SQL_class.read_from_db(table_name=self.table_name))	
	

	# SENSORS_PATH = dht_handler.p3_errors_path	
	# folder = 'logic_script'

	# time convert tests
	# def test_convert_test_normal(self):
	#     print('normal')
	#     samples = [('00:00', '8:10', '8:00'),('00:00', '7:10', '8:00'),('00:00', '8:10', '8:00'),
	#               ('01:20', '10:10', '8:00'), ('04:00', '20:10', '17:00'), ('7:00', '7:10', '8:00')]
	#     answer = [1,0,1,1,1,0]
	#     for i, tup in enumerate(samples):
	#         print('sample {} answers {}'.format(tup, answer[i]))
	#         func = self.obj_convert_test.convert_test(tup)
	#         ans = answer[i]
	#         self.assertEqual(ans, func, msg='should be {} is {}'.format(ans, func))

	# def test_convert_test_first_value_is_bigger(self):
	#     print('reversed')
	#     samples = [('23:00', '8:10', '10:00'), ('22:30', '8:10', '7:20'), ('18:20', '05:30', '10:00'),
	#                ('11:00', '8:10', '10:00'),('11:30', '11:10', '10:00'), ('23:00', '20:10', '10:00')]
	#     answers = [0,1,0,0,1,1]
	#     for i, tup in enumerate(samples):
	#         # print(f'sample {tup} answers {ans}')
	#         func = self.obj_convert_test.convert_test(tup)
	#         ans = answers[i]
	#         print('sample {} answers {}'.format(tup, ans))
	#         self.assertEqual(ans, func, msg='should be {} is {}'.format(ans, func))

	#dht_handler tests
	# def test_logic_recognicion_device_basic(self):
	#     samples = [(200,20), (50,20), (100,100), (40, 130), (None, None)]
	#     answers = [dht.DHT22, dht.DHT11, dht.DHT22, dht.DHT11, 10]        
	#     for i, sample  in enumerate(samples):
	#         print(i, sample)
	#         f = self.obj_dht_handler.logic(sample)
	#         a = answers[i]
	#         self.assertEqual(a, f, 'sample = {} should be {} is {}'.format(sample, a, f))

	# def test_logic_recognicion_device_random(self):
	#     '''11 - DHT.11
	#         22 -0 DHT.22
	#         Error code:
	#         10 - can't read properly data from DHT sensor
	#         '''

	#     test_function = lambda tup: 10 if tup[0] == None else 11 if 20 < tup[0] <= 95 else 22         
	#     random_samples = (((random.randint(-10,500) if random.randint(0,1) else None), random.randint(-10,500)) for _ in range(1000))
	#     for sample in random_samples:           
	#         func = self.obj_dht_handler.logic(sample)
	#         answer = test_function(sample)
	#         self.assertEqual(answer, func, f'sample = {sample} should be {answer} is {func}')
		



	# def test_recognicon_device_basic_for_dht11(self):
	# 	print('for DHT11')
	# 	# in tuple first should be humidity second temperature
	# 	samples = [(50,23), (60,34), (30,80), (34,22)]    	
	# 	answers = samples[::]
	# 	for i, sample in enumerate(samples):
	# 		answer = answers[i]
	# 		f = self.obj_dht_handler.recognicion_device(test_tuple1=sample)
	# 		self.assertEqual(answer, f, f'should be {answer} is {f}')
			

	# def test_recognicon_device_basic_for_dht22(self):
	# 	print('for DHT22')
	# 	samples = [{'tup1': (100,23), 'tup2':(35, 20)}, 
	# 	{'tup1': (500,23), 'tup2': (56,34)}, 
	# 	{'tup1': (230,90), 'tup2': (78, 23)}]
	# 	for i, sample in enumerate(samples):
	# 		answer = samples[i]['tup2']
	# 		f = self.obj_dht_handler.recognicion_device(test_tuple1=sample['tup1'], 
	# 			test_tuple2=sample['tup2'])
	# 		self.assertEqual(answer, f, f'sould be {answer} is --> {f}')

	# def test_recognicon_device_basic_for_error_code_10(self):
	# 	print('for error code 10')
	# 	samples = [{'tup1': (None, None), 'tup2':(None, None)}, 
	# 	{'tup1': (100,23), 'tup2':(435, 123)},
	# 	{'tup1': (130,231), 'tup2':(123, 39)}, 
	# 	{'tup1': (100,23), 'tup2':(None, None)},
	# 	]
	# 	for i, sample in enumerate(samples):
	# 		answer = 10
	# 		f = self.obj_dht_handler.recognicion_device(test_tuple1=sample['tup1'], 
	# 			test_tuple2=sample['tup2'])
	# 		self.assertEqual(answer, f, f'should be {answer} is {f}')


	# def test_random_test(self):
	# 	# mixed random test with dht11 , dht22, error code 10
	# 	# single sample creator		
	# 	create_single_sample = lambda: {name: data for name, data in zip(['tup1', 'tup2'], 
	# 		[random.choices(population=list(range(-100,200)) if random.randint(0,5)
	# 			else (None, None), k=2), 
	# 		random.choices(population=list(range(-100,200)) if random.randint(0,5)
	# 			else (None, None), k=2)])}
	# 	# create list with samples 
	# 	samples = [create_single_sample() for _ in range(10000)]

	# 	def answers(data):
	# 		# we get here dict object with two key words tup1, tup2
	# 		tup1, tup2 = data['tup1'], data['tup2']

	# 		if tup1[0] == None:
	# 			return 10			
	# 		elif 20 < tup1[0] <= 100 and -30 < tup1[1] <= 60:
	# 			return tup1
	# 		elif tup2[0] == None:
	# 			return 10			
	# 		elif 20 < tup2[0] <= 100 and -30 < tup2[1] <= 60:
	# 			return tup2
	# 		else:
	# 			return 10			

	# 	for i, sample in enumerate(samples):
	# 		print(f'{i} ----> {sample}')
	# 		answer = answers(sample)
	# 		f = self.obj_dht_handler.recognicion_device(test_tuple1=sample['tup1'], 
	# 			test_tuple2=sample['tup2'])
	# 		print('\n')
	# 		self.assertEqual(answer, f, f'should be {answer} is --> {f}')

	# def test_file_in_folder(self):		
	# 	self.assertTrue(self.obj_dht_handler.check_if_file_in_folder(
	# 		path=self.SENSORS_PATH, 
	# 		folder=self.folder))
	# def test_file_not_in_folder(self):
	# 	self.assertFalse(self.obj_dht_handler.check_if_file_on_folder(
	# 		path=self.SENSORS_PATH, 
	# 		folder=self.folder))
	# def test_read_data_from_db(self):
	# 	self.obj_SQL_class.read_from_db(table_name=self.table_name)
	# column_names = [col for col, var in \
	# 					obj_dht_handler.names_container_default.items()]
	# data_to_update = list(100 + i for i in range(len(column_names)))
	# reset_tokens = list(0 for _ in range(len(column_names)))

	# def test_update_single_col_in_db(self):		
	# 	for col, int_data in zip(self.column_names, self.data_to_update):
	# 		dict_data = {col: int_data}
	# 		print(dict_data)
	# 		self.obj_SQL_class.update_token_in_column(table_name=self.table_name,
	# 													input_data=dict_data)
		 

	# def test_fetch_data_from_db(self):		
	# 	for single_col, int_data in zip(self.column_names, self.reset_tokens):
	# 		print(f'column name --> {single_col}')			
	# 		fetched_data = self.obj_SQL_class.fetch_token_int_from_column(
	# 						table_name=self.table_name,
	# 						column_name=single_col)
	# 		self.assertEqual(fetched_data, int_data, f'should be {int_data} is -=>{fetched_data}')
			
	# def test_reset_tokens_in_db(self):
	# 	self.obj_SQL_class.update_token_in_column(table_name=self.table_name,
	# 										input_data=False,
	# 										reset_all_tokens=self.column_names)	




if __name__ == '__main__':
	unittest.main()



