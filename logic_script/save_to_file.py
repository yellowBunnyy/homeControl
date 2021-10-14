import os, json, sys, datetime, csv, sqlite3, re
os.chdir('/home/pi/Desktop/env/fl/homeControl')
print(os.getcwd())

class MyExceptions(Exception):
	def __init__(self, message, error):		
		super().__init__(message)
		self.message = message
		self.error = error
	def __str__(self):
		return f'mgs = {self.message}, exceptionType = {self.error}'
	


class HandlerFile():
	
	STATIC_LIGHTING_PATH = os.path.join(os.getcwd(),'logic_script','lighting.json')	
	STATIC_DB_ERRORS_PATH = os.path.join(os.getcwd(),'logic_script','errors_tokens_db.db')
	STATIC_AGREGATE_TEMPERATURE = os.path.join(os.getcwd(),'logic_script','temp_data.csv')	
	room_names = ["salon","maly_pokoj","kuchnia","WC","outside"]
	names_and_pins_default = {'salon': 7, 
							'maly_pokoj': 12, 
							'kuchnia': 16,							
							'WC': 8,
							'outside': 4}
	
	def create_container(self, path, content=None):					
		exists = os.path.isfile(path)
		if exists:
			return 'container exist!!'
		else:
			if not os.path.splitext(path)[-1]:
				raise MyExceptions(message='path are directory not file', error=FileExistsError)
			with open(path, 'w') as file:
				file.write(json.dumps(content if content else {}))
			return 'container was created!!'
	

	def save_to_json(self, path, content):
		with open(path, 'w') as file:
			json_data = json.dumps(content)
			file.write(json_data)
		return 'data was saved {}'.format(json_data)
	
	
	def load_from_json(self, path, key=None):
		'''function return dict obj'''
		pattern = r'{.*}'
		with open(path, mode='r') as file:
			json_content = file.read()
			matched = re.match(pattern, json_content)
			if not matched:
				raise MyExceptions(message=f'Brak danych w json_content!!! PATH --> {path}', error=ValueError)
			else:
				content = json.loads(json_content)           
		if key:
			try:
				# print('data was load with key {}'.format(content[key]))
				return content[key]
			except KeyError:
				print(f'klucz do content == {key}')
				raise MyExceptions(message=f'Brak klucza w load from \
					json PATH klucz do content {key} --> {path}', error=ValueError)
		else:
			# print('data was load without key {}'.format(content))
			return content


	def update_file(self, path, key, content, key2=None):
		if not os.path.exists(path):			
			raise MyExceptions(message='path does not exist', error=FileNotFoundError)
		dict_obj = self.load_from_json(path)
		if not key in dict_obj or not content:
			raise MyExceptions(message='check key or content', error=KeyError)		
		if key2:
			dict_obj[key][key2] = content
		else:
			dict_obj[key] = content
		self.save_to_json(path, dict_obj)		
		print('container was updated {}'.format(dict_obj))				
		return dict_obj[key][key2] if key2 else dict_obj[key]

	
	def delete_data_from_file(self, path, key):
		if not os.path.exists(path):
			raise MyExceptions(message=f'{path} does not exists!', error=FileExistsError)
		dict_obj = self.load_from_json(path)		
		if key in dict_obj:
			dict_obj.pop(key)
			self.save_to_json(path, dict_obj)
			return dict_obj
		else: 
			raise MyExceptions(message=f'{key} not found in dict_obj', error=KeyError)
		
	
	def recur_search_key(self, d, s_key):
		if type(d) != dict:
			raise MyExceptions(message=f'{d} if not dict obj', error=TypeError)
		f_key = []
		for key, val in d.items():
			print(f'key {key} val {val}')
			if type(val) == dict:
				if key == s_key:
					print('puted to ans')
					f_key.append(key)
				f_key += self.recur_search_key(d=val, s_key=s_key)
			else:
				if key == s_key:
					print('puted to ans')
					f_key.append(d)
		else:
			return f_key
	

class HandlerSQL(HandlerFile):
	'''DISCRIPTION:
		this class handle everything what is related with operations 
		on data bases'''
	SQL_TABELS_NAMES = [
	'sockets', 
	'errors_tokens_and_seted_temperature',
	'temperature_humidity',]

	def __init__(self):
		'''Here we initial conection to database and create
		cursor object form connect object.'''
		# create connection with db and create cursor
		# db_file = self.STATIC_DB_ERRORS_PATH
		# if not db_file:
		# 	raise MyErrors('Please insert DataBase file path!!')
		# else:
		# 	self.db_file = db_file
		# 	self.conn = sqlite3.connect(db_file, check_same_thread=False)
		# 	self.c = self.conn.cursor()
		# 	print('have connetction')
		# 	# this var have reference to dict with key as table_name and value as
		# 	# list with method from SQL_Handlet class
		# 	self.initial_table_in_db()
		pass

	@staticmethod
	def time_str_validation(str_time:str):
		patt = r'[0-5][0-9]:[0-5][0-9]'
		is_valid_time_string = lambda patt, str_time: False if re.match(patt, str_time) and len(str_time) == 5 else True
		if is_valid_time_string(patt, str_time):
			return False
		else:
			return True

		
			
	def initial_table_in_db(self, add_default_value:bool=True, rows_amount:int=2) -> dict:
		'''Here we initial all tabels in data base.
		add_default_value: initial default value in tabels if this argument is true
		otherwise return list which contain table names as string '''

		SQL_dict = {
		self.SQL_TABELS_NAMES[0]: [self.table_sockets,
					self.insert_data_to_sockets_table,
					('00:00','00:00')],
		self.SQL_TABELS_NAMES[1]: 
						[self.table_errors_tokens_and_seted_temperature,
						self.insert_data_token_table,
						(0,0,0,0,0)],
		self.SQL_TABELS_NAMES[2]:
						[self.table_temperature, 
						self.insert_data_to_temperature,
						(0,0,0,0,0)],
		}		
		if add_default_value:
			# varible object represent list content			
			for table_name, objects in SQL_dict.items():				
				if self.recognize_if_table_in_db_exist(table_name=table_name):
					table_sheet, insert_data_method, default_values = objects
					self.create_table(
							table_sheet=table_sheet())		
					# insert two to rows in one table
					if table_name == self.SQL_TABELS_NAMES[2]:
						# create 3 rows
						for i in range(3):
							if i==2:
								insert_data_method(tuple(self.names_and_pins_default.values()))
							else:
								insert_data_method(default_values)
								
					else:																
						for _ in range(rows_amount):
							insert_data_method(default_values)
				else:
					print(f'table {table_name} EXISTS')
			else:
				return {'rows_amount':rows_amount,
						'table_names': list(SQL_dict.keys()),
						}		


	def recognize_if_table_in_db_exist(self, cursor, table_name:str) -> bool:
		'''Recognizon if table is in data base. If is return false
			otherwise return true'''
		# script search table which is input --> (table_name) arg this metchod
		cursor.execute('''SELECT name FROM sqlite_master WHERE type="table" AND name="{}"'''.format(table_name))
		# import wdb; wdb.set_trace()
		if cursor.fetchone():
			print('db exist --> flag :false')
			return False
		else:
			print('db does not exist --> flag: true')
			return True

	def fetch_column_names(self, cursor, table_name:str)-> list:
		'''This method fetch comumns names and return them in list'''
		column_list = cursor.execute(f'''SELECT * from {table_name}''')
		return [row[0] for row in column_list.description]

# CREATE TABLE

	def table_temperature(self) -> tuple:
		sql = '''CREATE TABLE IF NOT EXISTS 'temperature_humidity' (
				id integer PRIMARY KEY,
				salon integer,
				maly_pokoj integer,
				kuchnia integer,
				WC integer,
				outside integer);'''
		return self.SQL_TABELS_NAMES[2], sql
		

	def table_sockets(self,)-> tuple:
		'''Table sheet for table sockets
		return: tuple with table name and sql sheet'''        
		sql = '''CREATE TABLE IF NOT EXISTS sockets (
				id integer PRIMARY KEY,
				turn_on text,
				turn_off text);
		'''
		return self.SQL_TABELS_NAMES[0], sql

	def table_errors_tokens_and_seted_temperature(self) -> tuple:
		'''Table sheet for table with errors tokens
		and seted temperature on heaters
		return: tuple with table name and sql sheet'''        
		sql = '''CREATE TABLE IF NOT EXISTS errors_tokens_and_seted_temperature (
				id integer PRIMARY KEY,
				salon integer,
				maly_pokoj integer,
				kuchnia integer,
				WC integer,
				outside integer);'''
		return self.SQL_TABELS_NAMES[1], sql

	def create_table(self, cursor, table_sheet:tuple):
		'''Create table in data base. Where first value in tuple is table name
		second are sql sheet to create table'''
		# create new table
		cursor.execute(table_sheet[1])
		print('table was created --> {}'.format(table_sheet[0]))
		return True

### INSERT

	def insert_data_to_temperature(self, conn, tuple_int:tuple):
		'''tuple: tuple with 5 int's temperature value '''
		if type(tuple_int) != tuple:
			raise MyExceptions(message=f'{tuple_int} is not tuple!!', error = TypeError) 
		sql = '''INSERT INTO 'temperature_humidity' (
				salon,
				maly_pokoj,
				kuchnia,
				WC,
				outside)
				VALUES (?,?,?,?,?)'''
		cursor = conn.cursor()		
		cursor.execute(sql, tuple_int)
		conn.commit()
		print(f'data was added {tuple_int}')
		last_row = cursor.lastrowid
		return last_row

	def insert_data_to_sockets_table(self, conn, times:tuple) -> int:
		'''return last row in int'''
		if type(times) != tuple:
			raise MyExceptions(message=f'{times} is not tuple!!', error = TypeError)
		patt = r'[0-5][0-9]:[0-5][0-9]'
		is_valid_time_string = lambda patt, s_time: False if re.match(patt, s_time) and len(s_time) == 5 else True
		for s_time in times:
			if is_valid_time_string(patt, s_time):
				raise MyExceptions(message=f'{s_time} is not "00:00" format time!!', error = ValueError)
		sql = '''INSERT INTO sockets (
				turn_on, turn_off)
				VALUES(?,?)'''
		cursor = conn.cursor()
		cursor.execute(sql, times)
		conn.commit()
		print(f'data was added {times}')
		last_row = cursor.lastrowid
		return last_row

	def insert_data_token_table(self, conn, tokens_int:tuple=False, seted_temperature:tuple=False) -> int:
		'''Insert to table in data base tuple with tokens_int or tuple with value ints
		seted temperature for heaters return last row in int'''
		if isinstance(tokens_int, (bool, tuple)) and isinstance(seted_temperature, (bool, tuple)):
			pass
		else:
			raise MyExceptions(message=f'one of args are not tuple or bool obj', error = ValueError)
		sql = '''INSERT INTO errors_tokens_and_seted_temperature (
				salon,
				maly_pokoj,
				kuchnia,
				WC,
				outside)
				VALUES (?,?,?,?,?)'''
		cursor = conn.cursor()
		cursor.execute(sql, tokens_int if tokens_int else seted_temperature)
		conn.commit()
		print(f'data was added {tokens_int if tokens_int else seted_temperature}')
		last_row = cursor.lastrowid
		return last_row

## UPDATE

	def update_data_in_temperature(self, conn, temp_or_humidity:tuple, temperature:bool=True):
		# temperature or humidity with id depends of input
		# Note:
		# 1 - is temperature
		# 2 - is humidity
		if not isinstance(temperature, bool):
			raise MyExceptions(message=f'{temerature} is not bool type. Please check it.', error=ValueError )
		data = temp_or_humidity + (1,) if temperature else temp_or_humidity + (2,)
		sql = '''UPDATE temperature_humidity SET
						salon = ?,
						maly_pokoj = ?,
						kuchnia = ?,
						WC = ?,
						outside = ?
						WHERE id = ?'''
		cursor = conn.cursor()
		cursor.execute(sql, data)
		print(f'{"temp" if temperature else "humidity"} was updated {temp_or_humidity}')		
		conn.commit()
		 

	def update_data_in_sockets_table(self, conn, times:tuple, row:int):
		'''This method updates data in sockets table
		times: tuple with seted hours in str format
		row_id: row int format to update'''
		# varible contain times in str and row id in int
		# add function to find invalid string 
		times += (row,)		
		sql = '''UPDATE sockets SET
				turn_on = ?,
				turn_off = ?
				WHERE id = ?'''
		cursor = conn.cursor()
		row_explanation = {1 : 'sockets', 2: 'heaters_switch'}
		print('data was update in socket table {} in row {}'.format(times[:-1], 
													row_explanation[row]))
		cursor.execute(sql,tuple(times))
		conn.commit()
		# add somewhere method for prevent when we put does not existing row


	def update_data_tokens(self, conn, tokens_int:tuple=False, temperature_int:tuple=False, row:int=False):
		'''Update data in table with tokens and temerature.
			tokens_int: tuple with tokens int's.
			temperature_int: tuple with seted temperature on haters in int format'''
		# last row number
		last_row_num = self.fetch_data_from_tokens(conn=conn, with_id=True)[-1][0]
		# import wdb; wdb.set_trace()
		if tokens_int and temperature_int:
			raise MyExceptions(mgs=f'inserted tuple in both arg. Please check. You must select one of args', error=ValueError)
		if row > last_row_num:
			raise MyExceptions(mgs=f'input row out of index. Grater than {last_row_num}', error=IndexError)
		tuple_data = tokens_int + (row,) if tokens_int else temperature_int + (row,)
		sql = '''UPDATE errors_tokens_and_seted_temperature SET
						salon = ?,
						maly_pokoj = ?,
						kuchnia = ?,
						WC = ?,
						outside = ?
						WHERE id = ?'''
		cursor = conn.cursor()
		cursor.execute(sql, tuple_data)
		# without last one (in this case row no.)		
		print('data was update in tokens table {} row {}.'.format(tuple_data[:-1],
														tuple_data[-1]))
		conn.commit()

## FETCH DATA
	
	def fetch_all_data_from_temp(self, conn, row:int=False, temperature_dict:bool=False, pin_dict:bool=False) -> (dict, list):
		'''
		1 - temps,
		2 - humidity
		row must be > 0
				'''
		if type(row) == int and row <= 0:
			raise MyExceptions(message=f'{row} <=0. Must be grater than 0', error=ValueError)
		sql = '''SELECT * from temperature_humidity'''
		cursor = conn.cursor()
		cursor.execute(sql)
		# import wdb; wdb.set_trace()
		fetched_data = cursor.fetchall()
		if temperature_dict:
			# return dict obj where keys are room names and value 
			#	are dict obj with temp and humidity value			
			dict_obj = {name: values for name, values in zip(self.room_names, [{'temp':temp, 'humidity':hum} 
			for temp, hum in zip(fetched_data[0][1:],fetched_data[1][1:])])}			
			return dict_obj
		if pin_dict:
			#names and pins
			dict_obj = dict(zip(self.room_names, fetched_data[2][1:]))
			return dict_obj							
		if row:
			# data in tuple without row
			row = 1 if type(row) == bool else row			
			return fetched_data[row - 1][1:]
		return fetched_data


	def fetch_all_data_from_sockets(self, conn, row:int=False, turn_on:bool=False, turn_off:bool=False) -> (list, int):
		'''Fetch all data from socket table.
		row: row number.
		turn_on: return hour in str format if true
		turn_off: return hour in str format if true'''
		if row <= 0 or type(turn_on) != bool or type(turn_off) != bool:
			raise MyExceptions(message=f'{row} <=0. Must be grater than 0' if row <= 0 else f'{turn_on} != bool' if type(turn_on) != bool else f'{turn_off} != bool', error=ValueError)
		sql = '''SELECT * from sockets'''
		cursor = conn.cursor()
		cursor.execute(sql)
		fetched_data = cursor.fetchall()		
		if row and turn_on:
			return fetched_data[row-1][1]
		elif row and turn_off:
			return fetched_data[row-1][2]
		elif row:
			# return as tuple without id
			return fetched_data[row-1][1:]
		# else:
		# 	return [tup[1:] for tup in fetched_data]


	def fetch_data_from_tokens(self, conn, row:int=False, room_name:str='', with_id:bool=False, show_dict=False) -> (list, int):
		'''Fetch all data from error_tokens_and... table'''
		if type(row) == int:
			if row <= 0:
				raise MyExceptions(mgs=f'{row} <=0. Must be grater than 0.')
		else:
			if row:
				raise MyExceptions(mgs=f'{row} Must be int.')
		if type(with_id) != bool or type(show_dict) != bool:
			raise MyExceptions(mgs=f'{with_id} Must be bool.' if type(with_id) != bool else f'{show_dict} Must be bool.')
		
		sql = '''SELECT * from errors_tokens_and_seted_temperature'''
		cursor = conn.cursor()
		cursor.execute(sql)
		all_data = cursor.fetchall()
		# print(all_data)
		if row:			
			# dict obj with room names as key and tokens or temperature as values
			dict_obj = dict(zip(self.room_names, all_data[row - 1][1:]))
			# print(dic_obj)
			if room_name:
				# return int
				return dict_obj[room_name]
			#return list
			elif show_dict:
				# show dict with room's name's as key and value as counted tokens
				return dict_obj
			return all_data[row-1][1:]
		#return list
		if with_id:
			return all_data
		else:
			# tup[1:] -> remove row number
			return [tup[1:] for tup in all_data]

	def main_fetch_data_from_db(self, table_name:str, row=False):
		method_list = [self.fetch_all_data_from_sockets,
						self.fetch_data_from_tokens]
		method_dict = dict(zip(self.SQL_TABELS_NAMES, method_list))
		return method_dict[table_name](row)

## REMOVE

	def drop_table(self, table_name):
		sql = '''DROP TABLE IF EXISTS {}'''.format(table_name)
		cursor = self.conn.cursor()
		cursor.execute(sql)
		print(f'TBL {table_name} WAS REMOVED!!')
		self.conn.commit()

	def remove_row_from_tbl(self, tbl_name:str, row:int):
		sql = '''DELETE FROM {}
				WHERE id={}'''.format(tbl_name,row)
		cursor = self.conn.cursor()
		cursor.execute(sql)
		print(f'row: {row} form tbl: {tbl_name} was removed!!')
		self.conn.commit()

## BACKEND FILE
	
class FileHandler:
	def __init__(self, path:str):
		self.path = path
		print(f'backend file path: {path}')

	def open_file(self):
		return open(self.path, 'r')

	def save_to_file(self):
		return open(self.path, 'a+')

	def delete_file(self):
		os.remove(path=self.path)
		print('file was deleted')

	def close_f(self, obj):
		print('file was closed')
		obj.close()


class CSV_Class:
	   
	# backend file are file obj
	def __init__(self, backend_file):
		self.backend_file = backend_file

	def convert_to_dict(self, orderedDict_list: list) -> list:
		f = lambda data: {key: int(val) if re.match(r'^[0-9]+$', val) else val
						  for key, val in data.items()}
		list_with_dicts = list(map(f, orderedDict_list))
		return list_with_dicts

	def read_csv(self, close_file:bool=False) -> list:
		self.backend_file.seek(0)
		csv_obj = csv.DictReader(f=self.backend_file)
		readed_data = []
		count_rows = 0
		for row in csv_obj:
			readed_data.append(row)
			count_rows += 1
		if close_file:
			self.backend_file.close()
		# return list witch dicts
		return self.convert_to_dict(readed_data), count_rows

	def save_to_csv(self, dict_data:dict) -> list:
		fieldnames = list(dict_data.keys())
		csv_obj = csv.DictWriter(f=self.backend_file,
								 fieldnames=fieldnames)
		flag, _ = self.read_csv()
		if not flag:
			csv_obj.writeheader()
			print('file are empty!!')
		else:
			print('file contain data')
		csv_obj.writerow(dict_data)        
		converted_data, _ = self.read_csv(close_file=True)
		return converted_data


class HandlerCsv(HandlerSQL, FileHandler):

	TRIGGER_HOURS = ['08:00', '10:00','14:00','16:00','22:00','02:00']	

	def save_temp_to_csv_handler(self, path, full_time):
		date, current_time = full_time.split(',')	
		#fetch dict with temp and humidity for every room 	
		temperature_data = self.fetch_all_data_from_temp(temperature_dict=True)
		
		for trigger_time in self.TRIGGER_HOURS:
			# date = self.convert_to_str(datetime.datetime.now())
			print(f'{trigger_time} - {current_time} - {"correct" if trigger_time==current_time else "false"} hour: {trigger_time}' )			
			if trigger_time == current_time:				
				self.save_to_file_csv(path=path, data=temperature_data, hour=trigger_time, date=date)
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

	def save_to_file_csv(self, path:str, data:dict, hour:str, date:str):
		if any(1 for value in data.values() if type(value) == dict):
			data = {name: d_obj['temp'] for name, d_obj in data.items()}
		data_with_date = {'date': date}
		data_with_date['hour'] = hour
		for room, temp in data.items():
			data_with_date[room] = temp
		backend_file = FileHandler(path=path)
		csv_obj = CSV_Class(backend_file=backend_file.save_to_file())			
		csv_obj.save_to_csv(dict_data=data_with_date)


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

	

if __name__ == '__main__':
	obj = HandletFile()