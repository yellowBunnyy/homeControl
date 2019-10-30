// console.log('jestes w js')
window.onload = init;

function init(){
	var celcius_sing = String.fromCharCode(176) + 'C';
	var my_read = new XMLHttpRequest();
	my_read.open('GET', '/temp_logic');
	my_read.onload = function() {
		var json_data = JSON.parse(my_read.responseText);
		var errors_obj = json_data['sensor_errors'];
		var temps_data = json_data['temps'];		
		var sensor_names = Object.keys(temps_data);
		var parrent = document.getElementById('parrent');
		for(var i = 0; i < sensor_names.length; i++){
			var header = document.createElement('h2');
			var room_element = document.createElement('h1');
			header.setAttribute('id',`header_${sensor_names[i]}`)										
			// console.log(header);			
			header.textContent = sensor_names[i];
			room_element.textContent = 'nothing'
			parrent.appendChild(header);			
			parrent.appendChild(room_element);
	}}
	my_read.send();
	read_data();

}

function read_data() {	
	var my_read = new XMLHttpRequest();
	my_read.open('GET', '/temp_logic');
	my_read.onload = function() {  // onload wczytuje dane zamieszzone w funkcji anonimowej pradopodobnie domyslnie jest null
		var json_data = JSON.parse(my_read.responseText);
		var temps_data = json_data['temps'];
		var sensor_errors = json_data['sensor_errors'];
		var sensor_names = Object.keys(temps_data); // this obj and method return array with key names 
		unzip_dict(names=sensor_names, data=temps_data);
		show_error_status(sensor_errors=sensor_errors);
		clean_error_status(sensor_errors=sensor_errors);
		read_from_db_file()
	};
	my_read.send();	
	setTimeout(read_data, 67000); // pierwszy arg to wywoływana funkcja, zas drugi to czas odswierzania podanu w ms
}


function unzip_dict(names, data){
	var tag_list_sensor = document.getElementsByTagName('h1');		
	var celcius_sing = String.fromCharCode(176) + 'C';
	for(var i = 0; i < names.length; i++){		
		if(data[names[i]]['temp'] >= 30){
			tag_list_sensor[i].setAttribute('class', 'high_temp');
		}
		else{
			tag_list_sensor[i].setAttribute('class', 'normal');
		}
		tag_list_sensor[i].innerHTML = `${data[names[i]]['temp']} ${celcius_sing} ${data[names[i]]['humidity']}%`		
	}
}
function is_int(input_val){
	//check if input_val can convert to int. true if yes otherwise false
	if(!isNaN(parseInt(input_val))){
			return true
		}else{return false}
}

function show_error_status(sensor_errors){
	var get_room_name_tags = document.getElementsByTagName('h2');
	// console.log(get_room_name_tags)		
	var l = [];
	for (room_name in sensor_errors){
		if (sensor_errors[room_name] >= 10){			
			l.push(`header_${room_name}`);			
		}
	}
				
	for(obj_element in get_room_name_tags){		
		if (is_int(obj_element)){
			// console.log(obj_element, get_room_name_tags[obj_element]);
			var element = get_room_name_tags[obj_element];
			var obj = element.children;
			// console.log(obj, obj.length);				
			if (obj.length <= 0 && l.includes(element.id)){											
				var error_status = document.createElement('h3');
				var error_id = element.id.replace('header_','error_');
				console.log(`element h3 created for ${element.id}`);
				error_status.setAttribute('id',`${error_id}`);
				error_status.setAttribute('class','sensor_problem');
				error_status.textContent = 'Check connection!';
				// console.log(error_status);
				element.appendChild(error_status);
				console.log('Status added');
			}else{
				console.log('skip status')}

		}		

	}
	
}

function read_from_db_file(){
	console.log('jestesmy w read_from_db_file')
	var connection = new XMLHttpRequest();
	connection.open('GET','/dbupdate');
	connection.send();
	//############ lepszed od onload ############\\
	// paremetr 'load' odpowiada za typ nasłuchu w tym przypadku po załadowaniu strony
	// wykona się zdarzenie
	// request.addEventListener('load', function(){		
	// 	var data = JSON.parse(this.responseText);
	// 	generate_buttons(data_from_server=data)
	// 	console.log(data);
	// //###########################################\\
	// })	
//blank func

}

function change_text_name(element_id, tag_obj, text_content){
	//search element in tag an change text name
	var new_text_content = search_element_in_tag(element_id, tag_obj, element_id_flag=true)
	return new_text_content.textContent = text_content;
}

function search_element_in_tag(element_id, tag_obj, element_id_flag=false){
	console.log(tag_obj, 'NOW');
	for(key in tag_obj){
		console.log(key, tag_obj[key], 'in search_element_in_tag')
		if(tag_obj[key].id == element_id){
			console.log('znaleziono');
			if (return_element_id_flag){
				return tag_obj[key];
			}else{
			return true}

	} return false
	}
}

function clean_error_status(sensor_errors){
	var tag_sensor_errors_status = document.getElementsByTagName('h3');	
	// console.log(tag_sensor_errors_status);
	// ! - negacja logiczna :)
	//jesli nic nie ma w tag_sensor_errors_status to czysci wszystkie errory.
	var count = 0;	
	for (room_name in sensor_errors){
		console.log(`${room_name} tokens ${sensor_errors[room_name]}`);
		// if true (we don't have any errors) we reset all errors code on site
		if (sensor_errors[room_name] >= 10){
			count += 1;			
		}
	}	
	if (!count){		
		for(key in tag_sensor_errors_status){
			if(is_int(key)){
				var element = tag_sensor_errors_status[key];
				console.log(`reset errors from ${element.id}`);
				element.remove();
				// console.log(element,'po if-ie');
				// element.textContent = '';
			}
			
		}
	}
	
}
	
