
window.onload = init;

function init() {
	var ONdata = document.getElementById('ONchooseBox');
	var OFFdata = document.getElementById('OFFchooseBox');
	var btn_layout = document.getElementById('save');
	ONdata.setAttribute('class','choose_box');
	OFFdata.setAttribute('class','choose_box');
	btn_layout.setAttribute('class', "btn btn-primary my-save-btn");		
	grab_seted_time_from_file_using_python('seted_time');
	// console.log('init w socket')
	var box = document.getElementById('save');
	grab_data_lighting();
	box.onclick = button_save;
}

function button_save() {
	console.log('Click')
	var ONdata = document.getElementById('ONchooseBox');
	var OFFdata = document.getElementById('OFFchooseBox');			
	times = {
		ON: ONdata.value,
		OFF: OFFdata.value,
	};	
	change_status_on_site('seted_time', times.ON, times.OFF);
	send_seted_time_on_server(times);
}

function send_seted_time_on_server(data){
	var post_to_python = new XMLHttpRequest();
	post_to_python.open('POST', '/settimeSockets');
	var format_to_json = JSON.stringify(data);
	console.log(`data was sended to server: ${format_to_json}`);
	post_to_python.send(format_to_json);

}

function change_status_on_site(id, start, stop) {
	var element = document.getElementById(id);
	element.innerHTML = `Gniazda Off on ${start} and On at ${stop}`;
}

function grab_seted_time_from_file_using_python(id){
	// console.log('loaded data form file using python');
	var element = document.getElementById(id);
	var req = new XMLHttpRequest();
	req.open('GET','/settimeSockets');	
	req.onload = function(){
		console.log(req.responseText);
		var data = JSON.parse(req.responseText);		
		element.innerHTML = `Zasilanie OFF o godz. ${data['ON']} ON o godz ${data['OFF']}`;
		};
	req.send();		
}

function grab_data_lighting(){
	//wczytanie strony oraz załadowanie klawiszy
	console.log('in grab_data_lighting');
	var request = new XMLHttpRequest();
	request.open('GET','/lighting')
	//############ lepszed od onload ############\\
	// paremetr 'load' odpowiada za typ nasłuchu w tym przypadku po załadowaniu strony
	// wykona się zdarzenie
	request.addEventListener('load', function(){		
		var data = JSON.parse(this.responseText);
		generate_buttons(data_from_server=data)
		console.log(data);
	//###########################################\\
	})	
	request.send();		
}

function generate_buttons(data_from_server){
	
	function str_on_off(status){
		//set str name in button\\
		if (status){
			return 'ON'
		}else{
			return 'OFF'
		}
	}
	var parrent = document.getElementById('parrent')	
	for (var key in data_from_server){
		console.log(key, data_from_server.key);
		var room_name = document.createElement('h5');
		// stworzenie elementu <button>
		var button = document.createElement('button');				
		room_name.textContent = key;
		room_name.setAttribute('class','room_names')
		// dodanie nazwy do elementu. Posiłkujemy się funkcją on_off
		button.textContent = str_on_off(data_from_server[key]['status']);
		// ustawienie klasy wygladu css
		button.setAttribute('class', "btn btn-primary my-btn");
		button.setAttribute('id',`${key}`)
		// button.setAttribute('status', `${data_from_server[key]['status']}`)

		// dodanie eventu przysisku po kiknięciu
		button.onclick = event_button;
		parrent.appendChild(room_name);
		//dodanie elementu do rodzica
		parrent.appendChild(button);
	}

}

function convert_str_to_int(input_str){
	if (input_str == 'ON'){
			return 0;
		}else if(input_str == 'OFF'){
			return 1;
		}else{
			console.log('error');
			return false
	}

}

function event_button(event){	
	var target = event.target;
	var room_name = target.id;
	// console.log(room_name,'|||');
	// właściwość innerHTML  w obiekcie target.
	// W tym wypadku zawiera wartość 'ON' lub 'OFF'
	var str_status = target.innerHTML;
	//zmienna przechowujaca status po nacisnieciu klawisza aby wysłać na server
	var status_to_send = convert_str_to_int(str_status);

	console.log(`click ${room_name} send to server ${str_status}`);
	//### pobieranie informacj z servera o stanie danego klawisza po jego wcisnieciu\\
	send_recive_data(room_name, target);	
}


function send_recive_data(room_name, element_obj){
	// console.log('in send_recive_data')	
	var request = new XMLHttpRequest();
	var status_to_send;	
	request.open('GET','/lighting');
	request.addEventListener('load', function(){		
		var data = JSON.parse(this.responseText);
		// console.log(data);
		// console.log(room_name);
		// console.log(data.room_name);
		var status = data[room_name]['status'];
		console.log(`status in send_revive_data ${status}`)
		if (status == 1){
			status_to_send = 0;
			element_obj.innerHTML = 'OFF';
		} else if (status == 0){
			status_to_send = 1;
			element_obj.innerHTML = 'ON';
		}else{
			console.log('error in send_revive_data');
		}

		var req2 = new XMLHttpRequest();
		req2.open('POST','/lighting');
		// dict room_name and status jak dajemy nawiasy wowczas wrzuca wartosc zmiennej
		var data = {[room_name]: status_to_send}
		var json_data_to_server = JSON.stringify(data);
		console.log(room_name);
		console.log(`wysłano dane ${status_to_send}`);	
		req2.send(json_data_to_server);
	})
	// console.log(`sended status ${status_to_send}`)	
	request.send();


}

