import unittest, random, Adafruit_DHT as dht
from logic_script import convert_time, dht_handler




class Basic_tests(unittest.TestCase):
   # obj_convert_test = convert_time.TimeConvertet()
	obj_dht_handler = dht_handler.DHT_Handler()
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


	def test_random_test(self):
		# mixed random test with dht11 , dht22, error code 10
		# single sample creator		
		create_single_sample = lambda: {name: data for name, data in zip(['tup1', 'tup2'], 
			[random.choices(population=list(range(-100,200)) if random.randint(0,5)
				else (None, None), k=2), 
			random.choices(population=list(range(-100,200)) if random.randint(0,5)
				else (None, None), k=2)])}
		# create list with samples 
		samples = [create_single_sample() for _ in range(10000)]

		def answers(data):
			# we get here dict object with two key words tup1, tup2
			tup1, tup2 = data['tup1'], data['tup2']

			if tup1[0] == None:
				return 10			
			elif 20 < tup1[0] <= 100 and -30 < tup1[1] <= 60:
				return tup1
			elif tup2[0] == None:
				return 10			
			elif 20 < tup2[0] <= 100 and -30 < tup2[1] <= 60:
				return tup2
			else:
				return 10			

		for i, sample in enumerate(samples):
			print(f'{i} ----> {sample}')
			answer = answers(sample)
			f = self.obj_dht_handler.recognicion_device(test_tuple1=sample['tup1'], 
				test_tuple2=sample['tup2'])
			print('\n')
			self.assertEqual(answer, f, f'should be {answer} is --> {f}')





		




if __name__ == '__main__':
	unittest.main()



