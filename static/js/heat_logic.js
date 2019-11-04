console.log('heat_logic')

window.onload = init;
var names = ['Salon', 'maly_pokoj', 'kuchnia']
var b_list = document.getElementsByTagName('b');
var b_sliced_list = slice_list(b_list, 0, 3);

function init(){
	console.log('in init');
	//get seted times from server using GET method
	request_function('GET', '/settimeHeat', null,'saved_time')
	request_function('GET','/settempHeat',null, null)
    var btn = document.getElementById('save');
    var save_temp = document.getElementById('save_temps');    
    btn.onclick = eventTime;
    save_temp.onclick = eventTemps;
}

function request_function(method, url, data, id){
	var conection_to_python_server = new XMLHttpRequest();
	if (method === 'POST'){		
		conection_to_python_server.open(method, url);
		var json_data = JSON.stringify(data);
		console.log(`data was sended: ${json_data}`);
		conection_to_python_server.send(json_data);
	}else if(method === 'GET'){		
		conection_to_python_server.open(method, url);
		conection_to_python_server.send();
		if (id){
			var status = document.getElementById(id);
			conection_to_python_server.onload = function(){
			var text = conection_to_python_server.responseText;
			console.log(text);
			var parsed_data = JSON.parse(text);
			status.innerHTML = `ogrzewanie NO ${parsed_data.ON} a OFF ${parsed_data.OFF}`;
			} 
		} else {
				conection_to_python_server.onload = function(){
					var data = conection_to_python_server.responseText;					
					var parsed_data = JSON.parse(data);
					console.log(parsed_data, typeof(parsed_data));
					for (i=0; i < names.length; i++){
						b_list[i].innerHTML = parsed_data[names[i]]
					}


				}
			}
		
		
	} else{
		console.log('BLAD!!!!')
	}
	
}


function eventTime(){
	//TIME
	console.log('click');
	var ON = document.getElementById('ONchooseBox');
	var OFF = document.getElementById('OFFchooseBox');
	var times = {
		ON: ON.value,
		OFF: OFF.value,
	};
	request_function('POST','/settimeHeat',times);
	change_status_time('saved_time', times.ON, times.OFF);	
}

function eventTemps(objEvent){
	//TEMP
	//console.log(objEvent);
	var select_list = document.getElementsByTagName('select');
    // var b_list = document.getElementsByTagName('b');    
    var select_sliced_list = slice_list(select_list, 2, select_list.length);
    // var b_sliced_list = slice_list(b_list, 0, 3);
	var readed_temps = get_seted_temp_from_site(names, select_sliced_list, b_sliced_list);
	request_function('POST', '/settempHeat', readed_temps);
	change_status_temps(select_sliced_list, b_sliced_list)


}

function change_status_time(id, ON, OFF){
	document.getElementById(id).innerHTML = `ogrzewanie NO ${ON} a OFF ${OFF}`;

}

function change_status_temps(id_s,b_list){
	for (i=0; i < id_s.length; i++){
		console.log(id_s[i].value);
		b_list[i].innerHTML = id_s[i].value;
	}

}


function get_seted_temp_from_site(names, select, b){
	console.log('in get seteted temp from server');	
	var saved_temp_container = {}	    
   	for (i = 0; i < names.length; i++){   		
   		saved_temp_container[names[i]] = parseInt(select[i].value);
   		console.log(saved_temp_container);  		
   	}   	
   	return saved_temp_container

}



function slice_list(list, start, stop){
	var l = []
	for (i=start; i < stop; i++){
		l.push(list[i])

	} return l 

}