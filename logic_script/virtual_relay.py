from logic_script import save_to_file
from time import sleep
import datetime, json, sys, RPi.GPIO as GPIO


save_to_file_obj = save_to_file.HandlerFile()

class MyExceptions(Exception):
	pass


class Dioda():
	'''Discription:
		this class handle GPIO library. '''

	test = {'salon': 21, 'mp':20, 'kuchnia': 26, 'sockets': 19}
	
	def set_pin_output(self, pin, signal):
	    '''Discription:
	    Set output pin to RPI controler
	    pin - output pin
	    signal - output signal (0,1) '''	    
	    GPIO.setmode(GPIO.BCM)	   
	    GPIO.setup(pin, GPIO.OUT)
	    GPIO.output(pin, signal)
	    print(pin, signal)
	    print('#'*30)

	def recive_input_from_decive(self, pin_device):
		'''Discription:
			pin_device - input signal comming to RPI pin'''
		GPIO.setmode(GPIO.BCM)	
		readed_status = GPIO.setup(pin_device, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		return True if readed_status else False

	def test_reviced_input_data(self, pin_device):
		while 1:
			sleep(.5)
			print(self.recive_input_from_decive(pin_device))

	def test_relays(self, data):
		'''arg "data" means input room names and pins '''
		count = 0
		while 1:
			for name, pin in data.items():
				print(f'{name}, {pin} --> signal {"low" if count % 2 == 0 else "high"}')
				if count % 2 == 0:
					self.set_pin_output(pin, 0)
				else:
					self.set_pin_output(pin,1)
				sleep(2)
			count += 1

	def turn_off_all_realays(self, data):
		for name, pin in data.items():
				print(f'{name}, {pin} --> signal {"high"}')			
				self.set_pin_output(pin, 1)
				
	def turn_on_all_realays(self, data):
		for name, pin in data.items():
				print(f'{name}, {pin} --> signal {"low"}')			
				self.set_pin_output(pin, 0)



class TimeConvertet():
    '''DISCRITION
        This class provides to convert input data e.g str to other format
        e.g datetime format'''
    
    def str_to_time(self, data):
        '''convert string to datetime'''
        process = data.split(':')
        hour, minute = process
        converted_time = datetime.time(hour=int(hour), minute=int(minute))
        return converted_time

    def convert_to_deltatime(self, input_time):
        '''convert datetime to timedelta. Allowe datetime input only!'''
        delta_time = datetime.timedelta(hours=input_time.hour, minutes=input_time.minute)
        return delta_time

    def convert_from_json_to_timedelta(self, binary_data):
        '''convert binary srting (json format) to timedelta'''
        decodet_req = binary_data.data.decode('ascii')
        data = json.loads(decodet_req)
        if type(data) == dict:
            for key, val in data.items():
                data[key] = self.convert_to_deltatime(self.str_to_time(val))
            return data
        else:
            print("Data is'n dict !! is {}".format(type(data)))
            for ele in data:
                print(ele)
            return False

    def convert_binary_to_str(self, binary):
        '''convert binary str (json) to dict'''
        decodet_req = binary.decode('ascii')
        return decodet_req


class Relays_class(Dioda, TimeConvertet):
	'''DISCRIPTION:
	'''

	def __init__(self, obj=save_to_file_obj):
		
		self.save_to_file = obj
		self.LIGHTING_PATH = obj.STATIC_LIGHTING_PATH
		self.data_path = obj.STATIC_PATH

	def relay(self, status, pin=None):
		if status:
			# print('jeden')
			self.set_pin_output(pin=pin, signal=status)
			return 1
		else:
			# print('zero')
			self.set_pin_output(pin=pin, signal=status)
			return 0


	def relay_configure(self, seted_time, current_time, pin=None, flag=False):
		'''this function configure relay. Argument is seted_time in is a dict e.g {'ON': '12:30', 'OFF': '20:12'}
			flag - if True method will turn on relay otherwise doesn't turn on relays'''

		status = {key: self.str_to_time(str_time)
				  for key, str_time in seted_time.items()}

		current_time = self.str_to_time(current_time)
		on, off = status['ON'], status['OFF']
		# print(status, current_time)
		
		if on > off:
			# print('reverse condition')
			print(f'{on} < {current_time} < {off}',
			 f'{True if on < current_time < off else False} ')			
			now = datetime.datetime.now() # import class and create method
			ct = datetime.datetime(year=now.year, month=now.month, day=now.day + 1, hour=now.hour, minute=now.minute)
			on = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=on.hour, minute=on.minute)
			off = datetime.datetime(year=now.year, month=now.month, day=now.day + 1, hour=off.hour, minute=off.minute)
			if on < ct < off:
				if flag:
					self.relay(status=1, pin=pin)
				else:
					return True
			else:
				if flag:
					self.relay(status=0,pin=pin)
				else:
					return False
		else:
			# print('Normal condition')
			print(f'{on} < {current_time} < {off}',
			 f'{True if on < current_time < off else False} ')
			if on < current_time < off:				
				if flag:
					self.relay(status=1, pin=pin)
				else:
					return True
			else:
				if flag:
					self.relay(status=0, pin=pin)
				else:
					return False

	def lighting_handler(self, request):
		'''Method to handle light switches'''		
		default_content = {'maly_pokoj': {'pin':18, 'status':0},
						'WC':{'pin':17, 'status':0}, 'PP':{'pin': 27, 'status':0},
						'salon':{'pin':23, 'status':0}, 'kuchnia':{'pin':24, 'status':0}}
		to_json_default_content = json.dumps(default_content)
		try:
			data_to_send = self.save_to_file.load_from_json(self.LIGHTING_PATH)
			return self.get_post_lightting(request=request,comunicate='lighting', data=data_to_send)
		except FileNotFoundError:
			self.save_to_file.create_container(self.LIGHTING_PATH)        
			self.save_to_file.save_to_json(self.LIGHTING_PATH, content=default_content)
			return self.get_post_lightting(request=request, comunicate='lighting', data=to_json_default_content)
		except:
			raise MyExceptions(f'Other error in lighting_relays_loader {sys.exc_info()[1]}')       
			


	def get_post_lightting(self, request, data=None, comunicate=None, test_data_to_send=None):
		'''this function handle requests data must be in dict object'''      
		if request.method == 'GET':			
			if test_data_to_send:           
				return test_data_to_send
			else:            
				return json.dumps(data)
		else:
			# here we recive from site json obj with room as key and status as int 0 or 1 (OFF, ON)
			data_from_site = json.loads(request.data.decode('ascii'))        
			for room_name, status in data_from_site.items():
				pass
			print(f'POST {room_name, status}')        
			dict_obj = data[room_name]       
			self.relay(status=status, pin=dict_obj['pin'])
			print(self.save_to_file.update_file(path=self.LIGHTING_PATH, key=room_name, key2='status', content=status))
			return 'OK'


	def switch_handler(self, current_time):
		'''This method handle turn on and off all relays
		   Note: Relays in module turn on when give them 0 in input
		args:
		current_time - current time form site'''
		def compare(arr, names_and_pins, reverse=False):
			'''this inner function compare seted temperature value with
			 readed temperature. 
			 Note: Relays in module turn on when give them 0 in input.
			 Args:
			 arr - data to compare'''

			#dict1 ustawione
			#dict2 odczytane

			unpack_f = lambda dict_obj: {name: content['temp'] for name, content in dict_obj.items()}
			dict1, dict2 = arr[0], unpack_f(arr[1])			
			for content1, content2 in zip(dict1.items(), dict2.items()):
				name1, temp1 = content1
				name2, temp2 = content2
				print(f'ustawiona: {temp1}, odczytana: {temp2}, {temp1 > temp2}, {name1}')
				if temp1 > temp2: # temp1 ustawiona, temp2 odczytana
					# turn on     		
					self.relay(status=0 if reverse else 1, pin=names_and_pins[name1.lower()])
				else:
					# turn off
					self.relay(status=1 if reverse else 0, pin=names_and_pins[name1.lower()])         

		# obj_relay = virtual_relay.Relays_class(obj=self.file_obj)
		test = {"sockets":19, "heat_switch":None, "heats":{'salon':21,'maly_pokoj':20,'kuchnia':26}, "temps":None}
		to_condition = []
		to_compare = []
		temporary_pin = ''
		for name, pin in test.items():
			data = self.save_to_file.load_from_json(path=self.data_path, key=name)
			# be careful here HARDCODING SCRIPT
			if name == 'heats' or name == 'temps':
				to_compare += [self.save_to_file.load_from_json(path=self.data_path, key=name)]
				if pin:
					temporary_pin = pin
			elif name == 'heat_switch':
				to_condition = data
			else:
				if pin:
					print('#'*10,'wyłączenie gniazd','#'*10)
					# print(data, current_time)
					self.relay_configure(seted_time=data, current_time=current_time, pin=pin, flag=True)
				
		else:
			print('#'*10,'wyłączenie heaters','#'*10)
			if self.relay_configure(seted_time=to_condition, current_time=current_time, pin=pin, flag=False):				
				compare(arr=to_compare, names_and_pins=temporary_pin)
			else:
				print('wyłącz przekaźniko od 1-3')				
				# [self.set_pin_output(pin=pin, signal=1) for pin in test['heats'].values()]



if __name__ == '__main__':
	pass