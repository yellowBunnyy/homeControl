
import time, sys, os, Adafruit_DHT as dht
from logic_script import save_to_file, virtual_relay
from time import sleep
##################fast get to paths######################### 
p1_data = save_to_file.HandlerFile().STATIC_PATH
p2_sensors = save_to_file.HandlerFile().STATIC_SENSOR_PATH
p3_errors_path = save_to_file.HandlerFile().STATIC_ERRORS_PATH
obj_save_file = save_to_file.HandlerFile()
############################################################
class MyExceptions(Exception):
	pass


class Container():	

	def __init__(self, data_path, sensors_path, errors_path, file_obj):
		
		self.data_path = data_path
		self.sensors_path = sensors_path
		self.errors_path = errors_path
		# file obj here is save_to_file module
		self.file_obj = file_obj
		self.file_obj.create_container(self.sensors_path)	

	def load_default(self):
		names_container_default = {'salon': 7, 'maly_pokoj': 12, 'kuchnia': 16, 'warsztat': 20, 'wc': 8,
								   'na_zewnatrz': 4}
		self.file_obj.save_to_json(self.sensors_path, names_container_default)

	def add_sensor(self, sensor_name, pin):
		self.file_obj.update_file(path=self.sensors_path, key=sensor_name, content= pin)
		return 'sensor {} was created'.format(sensor_name)

	def remove_sensor(self, sensor_name):
		self.file_obj.delete_data_from_file(self.sensors_path, sensor_name)
		return 'sensor {} was remove'.format(sensor_name)


class DHT_Handler(Container):
	'''This class is responsible for handle reading, 
		saving to file date from sensors'''
	
	sensorDHT11 = dht.DHT11
	sensorDHT22 = dht.DHT22
	names_container_default = {'salon': 7, 'maly_pokoj': 12, 'kuchnia': 16, 'WC':8, 'outside':4,}
	# errors = {'0': 'No sensor!! Check connection...', '1': 'Wrong read!!'}
	sensor_errors_header = 'sensor_errors'

	def __init__(self, data_path=p1_data, sensors_path=p2_sensors, errors_path=p3_errors_path, file_obj=obj_save_file):
		super().__init__(data_path, sensors_path, errors_path, file_obj)	


	def dict_with_keys_as_room_names_and_dict_as_value(self):
		# this method return dict include all room_names as key and dict as value where
		# key is temp and humidity and value is int 
		# e.g {'salon': {'temp':20, 'humidity'}, 'maly_pokoj': {'temp':20, 'humidity'}, itd.}
		data_from_sensor_file = self.file_obj.load_from_json(self.sensors_path)
		data_from_file = self.file_obj.load_from_json(self.data_path, 'temps')
		# print(data)
		dict_data_with_all_rooms_temp_and_humidity = {sensor_name: self.to_flask(pin=pin, sensor_name=sensor_name, data_from_file=data_from_file) 
		for sensor_name, pin in data_from_sensor_file.items()}
		return dict_data_with_all_rooms_temp_and_humidity

	def recognicion_device(self, pin:int=None, name:str=None, test_tuple1:tuple=None, test_tuple2:tuple=None):
		'''This method may return three value:
			- data in tuple,
			- 10 in int obj
			- False in bool obj'''		
		if test_tuple1:
			data_tuple = test_tuple1
		else:
			data_tuple = dht.read_retry(sensor = self.sensorDHT11, pin=pin, retries=7, delay_seconds=1)
		try:
			return self.logic(data_tuple=data_tuple, sensor_name=name, pin=pin, test_tuple=test_tuple2)
		except:
			raise MyExceptions(f'cos poszlo nie tak!! {sys.exc_info()[1]}')

	def logic(self, data_tuple, sensor_name=None, pin=None, test_tuple=None):
		try:
			# test for humidity
			if data_tuple[0] == None:
				print(f"{data_tuple} --> {sensor_name} can't read humidity properly!!")
				return 10
			# range test						 
			elif 20 < data_tuple[0] <= 100 and -30 < data_tuple[1] <= 60:				
				print(f'{data_tuple} --> {sensor_name}, device --> dht11')
				return data_tuple				
			else:
				# here we get tuple with two value temp and humidity if are in range or 
				# error code: 10 if one of value in tuple is our of range
				return self.secondary_logic_to_check(sensor_name=sensor_name, pin=pin, test_tuple=test_tuple)
		except:
			print('OTHER ERROR in logic', sys.exc_info()[1])
			return False

	def secondary_logic_to_check(self, sensor_name, pin, test_tuple=None):
		'''if logic method above cant recognize data from DHT11 sensor propertly try to
			read data from sensor DHT22 and return output depend on result:
			- data in tuple or
			- code error 10 int '''
		print(f'DHT22 method')
		if test_tuple:
			data = test_tuple		
		else:
			data = dht.read_retry(sensor=self.sensorDHT22, pin=pin, retries=7, delay_seconds=1)
		# range test		
		if data[0] != None and 20 < data[0] <= 100 and -30 < data[1] <= 60:
			print(f'{data} --> {sensor_name}, device --> dht22')
			return data
		else:
			# print(f'{data} --> {sensor_name} device --> dht11')
			print(f"{data} --> {sensor_name} can't read humidity properly!!")
			return 10

	
	def to_flask(self, pin:int, sensor_name:str, data_from_file:dict):
		'''method who create correct data form in allow range e.g 
		{temp: readed < 100, humidity: 20 < readed < 95) and return that data'''

		def remove_token_error(sensor_name:str):
			'''This method remove all tokens from sensor when reads is OK'''			
			# this variable represen how much we have tokens in sensor
			self.file_obj.update_file(path=self.errors_path, key=sensor_name, content=0)
			print(f'all tokens was remove from {sensor_name}')

		def add_token_error(sensor_name:str, sensor_token_int:int):
			''' This methon add one token to sensor when it's somthing wrong with reads '''
			# this variable represen how much we have tokens in sensor
			sensor_token_int += 1
			self.file_obj.update_file(path=self.errors_path, key=sensor_name, content=sensor_token_int)
			print(f'Token was added to {sensor_name} token info {sensor_token_int}!!')				
			if sensor_token_int >=10:
				print(f'błąd w {sensor_name}!!!!!!!')
				return f'{sensor_name} tu mamy błąd'

		readed_data = self.recognicion_device(pin=pin, name=sensor_name)

		if not readed_data or readed_data == 10:
			sensor_token_int = self.file_obj.load_from_json(path=self.errors_path)[sensor_name]
			add_token_error(sensor_name=sensor_name, sensor_token_int=sensor_token_int)
			print('from file!!!', data_from_file[sensor_name])
			return data_from_file[sensor_name]				
		else:									
			data = {name: round(value,1) if value != None else value for name, value in zip(['temp','humidity'], readed_data[::-1])}				
			self.file_obj.update_file(path=self.data_path, key='temps', key2=sensor_name, content=data)
			remove_token_error(sensor_name=sensor_name)
			# print('from sensor', data)			
			return data
	

	def update(self) -> dict:
		'''this method return dict include all room_names as key and dict as value where
			key is temp and humidity and value is int 
			e.g {'salon': {'temp':20, 'humidity'}, 'maly_pokoj': {'temp':20, 'humidity'}, itd.}
			AND create new dict object called 'sensor_errors_header' (for keep tokens to shows errors) 
			in main data file saved in .json '''			
		self.file_obj.create_container(path=self.errors_path, 
			content={name: 0 for name in self.names_container_default})			
		container = self.dict_with_keys_as_room_names_and_dict_as_value()
		return container

	
class SimpleyTesting(DHT_Handler):
	'''DESCRIPTION:
		Class created to test single sensors '''

	def single_sensor(self, sensor, pin, name='default'):
		print(f'{name} ---> {dht.read_retry(sensor=sensor, pin=pin, retries=3, delay_seconds=1)}')

	def loop_signle_sensor(self, sensor=11, pin=7, delay=3, name='salon'):
		'''Deafault Setings:
			sensor = 11
			pin = 7 tj. salon
			delay = 3
			name = salon
		'''
		while 1:
			time.sleep(delay)
			print(f'{name} ---> {dht.read_retry(sensor=sensor, pin=pin, retries=3, delay_seconds=1)}')
		

	def all_sensors_in_row(self, sensors_dict):			
		for name_sensor, pin in sensors_dict.items():
			# print(name_sensor, pin)
			if name_sensor == 'na_zewnatrz':
				print(f'{name_sensor}--->{[round(val,2) for val in dht.read_retry(sensor= self.sensorDHT22, pin= pin, retries= 15, delay_seconds= 1)]}')
			else:
				print(f'{name_sensor}--->{dht.read_retry(sensor= self.sensorDHT11, pin= pin, retries= 15, delay_seconds= 1)}')
		else:
			print('-'*10)

	def check_all_to_flask(self):		
		for name, pin in self.names_container_default.items():
			print(name, pin)
			print(self.to_flask(pin))


	def check_recognicion_device(self):
		for name, pin in self.names_container_default.items():
			print(f'{name} --> {self.recognicion_device(pin)}')
			sleep(5)	

if __name__ == '__main__':
	
	instance = DHT_Handler()
	instance.check_all_to_flask()
