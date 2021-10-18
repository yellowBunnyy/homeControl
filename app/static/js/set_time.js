// console.log('in set time');

function view_hour_in_choosebox(id, start, stop) {
			var options = ''
			for (var hour = start; hour <= stop; hour++){
				for (var minutes = 0; minutes <= 59; minutes++){
					if (minutes % 10 == 0){
						if (hour < 10){
							tmp_opt = '<option>'+ `0${hour}:${minutes}`+'</option>';
							// options += '<option>'+ `0${hour}:${minutes}`+'</option>';
							if (minutes < 10){
								// options += '<option>'+ `0${hour}:0${minutes}`+'</option>';
								tmp_opt = '<option>'+ `0${hour}:0${minutes}`+'</option>';
								options += tmp_opt;					
							} else{
								options += tmp_opt;
							}							
						}else {
							tmp_opt = '<option>'+ `${hour}:${minutes}`+'</option>';
							if (minutes < 10){
								tmp_opt = '<option>'+ `${hour}:0${minutes}`+'</option>';
								options += tmp_opt;
							}else{
								options += tmp_opt;
							}
						
						}
						
					};
						
				};
				
			};
		document.getElementById(id).innerHTML = options;	
		};

view_hour_in_choosebox('ONchooseBox', 0, 23);
view_hour_in_choosebox('OFFchooseBox', 0, 23);
