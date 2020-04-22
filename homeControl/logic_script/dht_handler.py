import time, sys, os, Adafruit_DHT as dht
print(os.getcwd())
from logic_script import save_to_file
from time import sleep
##################fast get to paths#########################
obj_save_file = save_to_file.HandlerSQL()
############################################################
class MyExceptions(Exception):
	def __init__(self, type_error, mgs):
		self.type_error = type_error
		self.mgs = mgs



class Container():	

	def __init__(self, file_obj):		
		self.file_obj = file_obj

	# def load_default(self):
	# 	names_container_default = {'salon': 7, 'maly_pokoj': 12, 'kuchnia': 16, 'warsztat': 20, 'wc': 8,
	# 							   'na_zewnatrz': 4}
	# 	self.file_obj.save_to_json(self.sensors_path, names_container_default)

	# def add_sensor(self, sensor_name, pin):
	# 	self.file_obj.update_file(path=self.sensors_path, key=sensor_name, content= pin)
	# 	return 'sensor {} was created'.format(sensor_name)

	# def remove_sensor(self, sensor_name):
	# 	self.file_obj.delete_data_from_file(self.sensors_path, sensor_name)
	# 	return 'sensor {} was remove'.format(sensor_name)


class DHT_Handler(Container):
	'''This class is responsible for handle reading, 
		saving to file date from sensors'''
	
	sensorDHT11 = 11
	sensorDHT22 = 22
	

	
	def __init__(self, file_obj=obj_save_file):
		super().__init__(file_obj)
		self.SQL_obj = file_obj
		self.table_name = self.SQL_obj.SQL_TABELS_NAMES[1]
		self.names_and_pins_default = file_obj.names_and_pins_default


	def dict_with_keys_as_room_names_and_dict_as_value(self) -> dict:
		# this method return dict include all room_names as key and dict as value where
		# key is temp and humidity and value is int 
		# e.g {'salon': {'temp':20, 'humidity'}, 'maly_pokoj': {'temp':20, 'humidity'}, itd.}
		data_from_sensor_file = self.SQL_obj.fetch_all_data_from_temp(pin_dict=True)			
		data_from_file_temps_tbl = self.SQL_obj.fetch_all_data_from_temp(temperature_dict=True)		
		dict_data_with_all_rooms_temp_and_humidity = {sensor_name: self.to_flask(pin=pin, sensor_name=sensor_name, 
			data_from_file=data_from_file_temps_tbl) for sensor_name, pin in data_from_sensor_file.items()}
		return dict_data_with_all_rooms_temp_and_humidity

	def recognicion_device(self, pin:int=None, name:str=None):
		'''This method may return three value:
			- data in tuple,
			- 10 in int obj
			- False in bool obj'''
		if type(pin) == int and pin > 31:
			raise MyExceptions(type_error=ValueError, mgs="pin are > 31")
		elif type(pin) != int:		
			raise MyExceptions(type_error=ValueError, mgs="pin are not int")
		else:
			pass		
		data_tuple = dht.read_retry(sensor = self.sensorDHT11, pin=pin, retries=7, delay_seconds=1)
		if None in data_tuple:
			print(f'{data_tuple} --> {name} --> DHT11')
			return 10
			# raise MyExceptions(type_error=ValueError, mgs=f"can't read humidity properly!!")
		else:
			return self.logic(data_tuple=data_tuple, sensor_name=name, pin=pin)
		 

	def logic(self, data_tuple, sensor_name=None, pin=None):
		# try:
		# range test						 
		if 20 < data_tuple[0] <= 100 and -30 < data_tuple[1] <= 60:				
			print(f'{data_tuple} --> {sensor_name}, device --> dht11')
			return data_tuple				
		else:
			print(f"{data_tuple} --> {sensor_name} can't read humidity properly!! DHT11")
			# here we get tuple with two value temp and humidity if are in range or 
			# error code: 10 if one of value in tuple is our of range
			return self.secondary_logic_to_check(sensor_name=sensor_name, pin=pin)
		# except:
		# 	# this exception are allways call when we have e.g. (30, None) in data_tuple
		# 	# when first index is None
		# 	raise MyExceptions(ValueError, 
		# 		'brak danych na pierwszym indexie',
		# 		f'{sys.exc_info()[1]}')

	def secondary_logic_to_check(self, sensor_name:int=None, pin:int=None):
		'''if logic method above cant recognize data from DHT11 sensor propertly try to
			read data from sensor DHT22 and return output depend on result:
			- data in tuple or
			- code error 10 int '''
		print(f'DHT22 method')		
			
		data = dht.read_retry(sensor=self.sensorDHT22, pin=pin, retries=7, delay_seconds=1)			
		# range test		
		if data[0] != None and 20 < data[0] <= 100 and data[1] != None and -30 < data[1] <= 60:
			print(f'{tuple(map(lambda x: round(x,2), data))} --> {sensor_name}, device --> dht22')
			return data
		else:
			# print(f'{data} --> {sensor_name} device --> dht11')
			print(f"{data} --> {sensor_name} can't read humidity properly!!")
			return 10

	def remove_token_error(self, sensor_name:str):
			'''This method remove all tokens from sensor when reads is OK'''
			# below var have ref to sensor_names as key and token int as value
			dict_obj = self.SQL_obj.fetch_data_from_tokens(row=1, show_dict=True)			
			tokens_int = tuple(0 if room_name == sensor_name else val 
								for room_name, val in dict_obj.items())						
			self.SQL_obj.update_data_tokens(tokens_int=tokens_int, 
												row=1)
			print(f'all tokens was remove from {sensor_name}')
			#return tuple with restarted tokens value			
			return tokens_int

	def add_token_error(self, sensor_name:str):
			''' This methon add one token to sensor when it's somthing wrong with reads '''			
			dict_obj = self.SQL_obj.fetch_data_from_tokens(row=1, show_dict=True)
			tokens_int = ()
			input_name_correct_flag = False
			input_allowe_value_flag = True
			for room_name, val in dict_obj.items():
				# print(room_name, val)
				if type(val) == int:
					if room_name == sensor_name:
						# val + 1 increment token value
						val += 1
						tokens_int += (val,)
						added_token_val = val
						input_name_correct_flag = True										
					else:
						tokens_int += (val,)
				else:
					print('!!WARNING!!\ntoken is not integer!')
					tokens_int += (None,)
					input_allowe_value_flag = False			
			 
			self.SQL_obj.update_data_tokens(tokens_int=tokens_int,
												row=1)
			
			if dict_obj and input_allowe_value_flag and input_name_correct_flag :
				print(f'Token was added to {sensor_name} token info {added_token_val}!!')				
				if added_token_val >=10:
					print(f'błąd w {sensor_name}!!!!!!!')
			return tokens_int				

	
	def to_flask(self, pin:int, sensor_name:str, data_from_file:dict) -> dict:
		'''method who create correct data form in allow range e.g 
		{temp: readed < 100, humidity: 20 < readed < 95) and return that data'''
		 
		readed_data = self.recognicion_device(pin=pin, name=sensor_name)

		if not readed_data or readed_data == 10:
			self.add_token_error(sensor_name=sensor_name)
			print('from file!!!', data_from_file[sensor_name])
			return data_from_file[sensor_name]

		else:
			#update all temps and humidity									
			data = {name: round(value,1) if value != None else value 
					for name, value in zip(['temp','humidity'], readed_data[::-1])}
			self.remove_token_error(sensor_name=sensor_name)
			return data
	

	def update(self) -> dict:
		'''this method return dict include all room_names as key and dict as value where
			key is temp and humidity and value is int 
			e.g {'salon': {'temp':20, 'humidity':40}, 'maly_pokoj': {'temp':20, 'humidity':06}, itd.}
			AND update temperature and humidity in table '''	
		container = self.dict_with_keys_as_room_names_and_dict_as_value()		
		#unpack container dict to temp values as tuple and humidity values as tupe
		temps, humidity = [tuple(value[t] for key, value in container.items()) 
							for t in ['temp','humidity']]			
		self.SQL_obj.update_data_in_temperature(temp_or_humidity=temps)
		self.SQL_obj.update_data_in_temperature(temp_or_humidity=humidity, temperature=False)
		return container

	
class SimpleyTesting(DHT_Handler):
	'''DESCRIPTION:
		Class created to test single sensors '''

	def single_sensor(self, sensor:int, pin:int, name='default'):
		'''set sensor 11 or 22. dht11 is 11, dht22 i 22'''
		if sensor in [11,22] and 0 < pin < 31:
			print(f'{name} ---> {dht.read_retry(sensor=sensor, pin=pin, retries=3, delay_seconds=1)}')
		else:
			if sensor not in [11,22]:
				raise MyExceptions(type_error=ValueError, mgs='sensor allowe 11 or 22')
			else:
				raise MyExceptions(type_error=ValueError, mgs='pin must be 0 < pin < 30')
	
	def all_sensors_in_row(self, sensors_dict):		
		for name_sensor, pin in sensors_dict.items():			
			if name_sensor == 'outside':
				print(f'{name_sensor}--->{[round(val,2) for val in dht.read_retry(sensor = 22, pin = pin, retries = 15, delay_seconds = 1)]}')
			else:
				print(f'{name_sensor}--->{dht.read_retry(sensor = 11, pin = pin, retries = 15, delay_seconds= 1)}')
		else:
			print('-'*10)

if __name__ == '__main__':	
	# instance = DHT_Handler()
	pass
	