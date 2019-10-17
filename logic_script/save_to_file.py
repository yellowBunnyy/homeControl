import os, json, sys, datetime, csv

os.chdir('/home/pi/Desktop/env/fl/src')
print(os.getcwd())

class MyExceptions(Exception):
	pass


class HandlerFile():

	STATIC_PATH = os.path.join(os.getcwd(),'logic_script','data.json')
	STATIC_SENSOR_PATH = os.path.join(os.getcwd(),'logic_script','sensor_list.json')
	STATIC_LIGHTING_PATH = os.path.join(os.getcwd(),'logic_script','lighting.json')
	STATIC_ERRORS_PATH = os.path.join(os.getcwd(),'logic_script','errors_tokens.json')	

	def create_container(self, path, content=None):
		file_name = path.split('/')[-1]
		# print(file_name)
		if self.file_existance(path, file_name):
			return 'container exist!!'
		else:
			with open(path, 'w') as file:
				file.write(json.dumps(content if content else {}))
			return 'container was created!!'

	def file_existance(self, path, file_name='data.json'):
		folder = os.path.dirname(path)
		if file_name in os.listdir(folder):
			return True
		else:
			return False

	def save_to_json(self, path, content):
		with open(path, 'w') as file:
			json_data = json.dumps(content)
			file.write(json_data)
		return 'data was saved {}'.format(json_data)
	
	
	def load_from_json(self, path, key=None):
		'''function return dict obj'''
		with open(path, mode='r') as file:
			json_content = file.read()
			if not json_content:
				raise MyExceptions(f'Brak danych w json_content!!! PATH --> {path}')
			else:
				content = json.loads(json_content)           
		if key:
			try:
				# print('data was load with key {}'.format(content[key]))
				return content[key]
			except KeyError:
				raise MyExceptions(f'Brak klucza w load from json PATH --> {path}')
		else:
			# print('data was load without key {}'.format(content))
			return content


	def update_file(self, path, key, content, key2=None):
		dict_obj = self.load_from_json(path)
		if key2:
			dict_obj[key][key2] = content
		else:
			dict_obj[key] = content
		self.save_to_json(path, dict_obj)
		return 'container was updated {}'.format(dict_obj)


	# def update_file2(self, path, key, key2 content):
	#     dict_obj = self.load_from_json(path)
	#     dict_obj[key][key2] = content
	#     self.save_to_json(path, dict_obj)
	#     return 'container was updated {}'.format(dict_obj)
	
	
	def delete_data_from_file(self, path, key):
		dict_obj = self.load_from_json(path)
		try:
			deleted_val = dict_obj.pop(key)
			self.save_to_json(path, dict_obj)
			return 'key {} with content {} was deleted'.format(key, deleted_val)
		except KeyError:
			return 'key {} is not in dict'.format(key)
		
	
	def search_key(self, d, s_key):        
		for key_1, val_1 in d.items():
			if key_1 == s_key:
				return 'finded {}'.format(key_1)
			else:
				if type(val_1) == dict:
					for key_2, val_2 in val_1.items():
						if key_2 == s_key:
							return 'finded {}'.format(key_2)
		else:
			return 'nothing here'
	
class HandlerCsv(HandlerFile):
	
	CSV_file = os.path.join(os.getcwd(),'logic_script','temp_data.csv')
	TRIGGER_HOURS = ['08:00', '10:00','14:00','16:00','22:00','02:00']	


	def save_temp_to_csv_handler(self, full_time):
		date, current_time = full_time.split(',')
		temperature_data = self.load_from_json(path=self.STATIC_PATH, key='temps')
		for trigger_time in self.TRIGGER_HOURS:
			# date = self.convert_to_str(datetime.datetime.now())
			print(f'{trigger_time} - {current_time} - {"correct" if trigger_time==current_time else "false"} | date: {date}' )			
			if trigger_time == current_time:			
				# data = self.load_from_json(path=self.STATIC_PATH, key='temps')
				self.save_to_file_csv(file_path=self.CSV_file, data=temperature_data, hour=trigger_time, date=date)
				print(f'{trigger_time}ZAPISANO DO CSV')


	def convert_to_str(self, date):
		'''convert datetime date object to str date object'''
		if type(date) == str:
			return date
		elif type(date) == datetime.datetime:
			date = date.strftime('%d-%m-%y')
			return date
		else:
			raise MyExceptions('unknow date format!')


	def read_from_csv(self, file_path, names=None, data=None, row_num=False, header=None):
		'''Multilpe function in this method.
		names = True --> show columns and data under columns in console window 
		row_num = True --> count rows and return number of rows
		header = True --> method check if file exist'''
		count_rows = 0
		try:
			with open(file_path, 'r') as file:
				reader = csv.DictReader(file)
				if header:
					return True
				if names:
					names = ['date'] + list(names)
					print(f'columns: \n{names}')
				for row in reader:
					count_rows += 1
					if names:
						print(' '.join(row[name] for name in names))
				else:
					if row_num:
						return count_rows
		except:
			return False

	def save_to_file_csv(self, file_path, data, hour, date):
		if any(1 for value in data.values() if type(value) == dict):
			data = {name: d_obj['temp'] for name, d_obj in data.items()}
		data_with_date = {'date': date}
		data_with_date['hour'] = hour
		for room, temp in data.items():
			data_with_date[room] = temp

		#this flag check if we have created hader in csv file			
		add_header_flag = self.read_from_csv(file_path, header=True)

		with open(file_path, 'a') as file:
			fieldnames = data_with_date.keys()
			df = csv.DictWriter(f=file, fieldnames=fieldnames,)
			if add_header_flag:
				df.writerow(data_with_date)
			else:
				df.writeheader()
				df.writerow(data_with_date)



############################# for numpy #############################
	def pandas_read_from_csv(self, file_path):
		with open(file_path, 'r') as file_csv:
			print(file_csv)
			for row in file_csv:
				print(row)
			# df = pd.DataFrame(data=file_csv)
			# print(df)


	def pandas_save_to_file(self, data, file_path, obj_date=datetime.datetime.now()):
		'''data - here we have dict object with key means rooms and value 
					means temp in every room's
				   date - in str format if not slave function convert to str'''
		if any(1 for value in data.values() if type(value) == dict):
			data = {name: d_obj['temp'] for name, d_obj in data.items()}

		data_with_date = {'date': self.convert_to_str(obj_date)}
		for room, temp in data.items():
			data_with_date[room] = temp
		# print(data_with_date)
		numb_index = self.read_from_csv(file_path=file_path, row_num=True)
		numb_index = numb_index if numb_index else 0
		df_obj = pd.DataFrame(data=data_with_date, index=[numb_index])
		if numb_index:
			df_obj.to_csv(path_or_buf=file_path, sep=',',header=False, mode='a')
			return True
		else:
			df_obj.to_csv(path_or_buf=file_path, sep=',',header=True, mode='w')
			return True

	def pandas_random_insert_data(self, no_examples, file_path):
		for _ in range(no_examples):
			tup_rand_choces = random.choices(range(-100,100),k=3)
			data = {name: val for name, val in zip(['salon', 'm_p', 'kuchnia'], tup_rand_choces)}
			ran_date = datetime.datetime(year=2019, month=random.choice(range(1,13)),
										 day=random.choice(range(1,31)))
			self.pandas_save_to_file(file_path=file_path, data=data, obj_date=ran_date)
############################# endBlock #############################

class HandlerSQL(HandlerCsv):
	
	def __init__(self, db_file):
		# create connection with db and create cursor
		self.db_file = db_file
		self.conn = sqlite3.connect(db_file)
		self.c = self.conn.cursor()
		print('have connetction')

	def close_db(self):
		#close db
		self.conn.close()

	def create_table(self, table_name, columns):
		# create new table
		# print(','.join(name_col for name_col in columns))
		self.c.execute('''CREATE TABLE {}
				   ({})'''.format(table_name, ','.join(name_col for name_col in columns)))
		print('table was created --> {}'.format(table_name))

	def save_data_to_db(self, data, table_name, *comumns):
		# this condition create table in db if dose not exist
		if self.recognize_if_table_in_db_exist(table_name=table_name):
			self.create_table(table_name=table_name, columns=comumns)

		if type(data)!= tuple:
			raise MyErrors('wrong data format!! allowed tuple!!')
		else:
			self.c.execute('''INSERT INTO {} VALUES ({})
				 '''.format(table_name,','.join('?'*len(data))),data)
			print('data was saved --> {}'.format(data))
			self.conn.commit()
			print('was commited')
			self.close_db()
			print('db was closed')

	def compare_with_current_temp_and_save(self, full_time):
		data = tuple(full_time.split(','))
		temps_values_tup = tuple(value for room, value in self.TEMP_DATA.items())
		all_data = data + temps_values_tup
		print(all_data,'||||||')
		if current_time in TRIGGER_HOURS:
			self.save_data_to_db()
			pass

	def read_from_db(self, table_name):
		for row in self.c.execute('''SELECT * FROM {}'''.format(table_name)):
			print(row)

	def create_random_input_data(self, no_col):
		date, hour = datetime.datetime.now().strftime('%d-%m-%Y,%H:%M').split(',')
		if no_col > 2:
			t = tuple(random.choices(range(-20, 35),k = no_col - 2))
			return (date, hour) + t
		else:
			raise MyErrors('not enough columns no_col > 2')

	def recognize_if_table_in_db_exist(self, table_name):
		'''Recognizon if data base is created. If is return false
			otherwise return true'''
		# script search table who is input arg this metchod
		self.c.execute('''SELECT name FROM sqlite_master WHERE type="table" AND name="{}"'''.format(table_name))
		if self.c.fetchone():
			print('db exist --> flag :false')
			return False
		else:
			print('db does not exist --> flag: true')
			return True

	

if __name__ == '__main__':
	obj = HandletFile()
	path = obj.STATIC_PATH
   # print(obj.create_container(obj.STATIC_PATH))	
	sample = {'ON':'20:30','OFF':'11:23'}
	second_sample = {'temp1':23, 'temp2':21, 'temp3':90}
	third_sample = {'sockets': {'ON': '20:30', 'OFF': '11:23'}, 'temps': {'temp2': 21, 'temp1': 23, 'temp3': 90}}
	# obj.save_to_json(obj.STATIC_PATH, third_sample)
	# print(obj.load_from_json(obj.STATIC_PATH, key='soda'))
   # obj.update_file(path, 'temps', second_sample)
   # print(obj.delete_data_from_file(path, 'temps'))
   # print(obj.search_key(d=third_sample, s_key='temp3'))
   # print(obj.search_requr(d=third_sample, s_key='ON'))
   #  obj.update_file(obj.STATIC_PATH, 'sockets', {'ON': '21:30', 'OFF': '0:00'})

	# print(obj.create_container(obj.STATIC_PATH))
