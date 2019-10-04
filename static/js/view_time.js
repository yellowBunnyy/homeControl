// console.log('view time');

function update_time(){
	// console.log('interval')
	var current_datetime = new Date();
	var show_time = document.getElementById('show_time');
	send_current_time_to_server(current_datetime);
	show_time.innerHTML = `${add_zero_in_front(current_datetime.getHours())}:${add_zero_in_front(current_datetime.getMinutes())}:${add_zero_in_front(current_datetime.getSeconds())}`;

	var time_in_json = {
		time: function () {
				var obj = {
					hour: current_datetime.getHours(),
					minute: current_datetime.getMinutes(),
				};
				var json_obj = JSON.stringify(obj);
				console.log(json_obj);
				return json_obj
			},
		date: function current_date() {
				var obj = {
					day: current_datetime.getDate(),
					month: current_datetime.getMonth() + 1,
					year: 2000 + current_datetime.getYear() - 100,

				};
				var json_obj = JSON.stringify(obj);
				console.log(json_obj);
				return json_obj
			},
};

	setTimeout(update_time, 1000);

}
function add_zero_in_front(data){	
	if (data < 10){
		return `0${data}`
	}else{return data.toString()}

}

function send_current_time_to_server(current_time, delay=60) {
	// sending current time (time and data // czas i datę) to python server 
	// with delay (default dealay 10min * 60s = 600s)

//	console.log(Math.round(current_time/1000) % 600)
	if(Math.round(current_time/1000) % delay == 0){
        var date = new Date();
        var obj_time_to_send = convert_to_json_obj(date).str_time()
	    var send_current_time = new XMLHttpRequest();
	    send_current_time.open('POST','/current');
//	    json_obj = JSON.stringify(obj_time_to_send)
	    send_current_time.send(obj_time_to_send)
		console.log('POSZŁO!!');

	}

}
function convert_to_json_obj(current_datetime) {
	var time_in_json_obj = {
		time: function () {
				var obj = {
					hour: current_datetime.getHours(),
					minute: current_datetime.getMinutes(),
				};
				var json_obj = JSON.stringify(obj);
				console.log(json_obj);
				return json_obj
			},
		date: function current_date() {
				var obj = {
					day: current_datetime.getDate(),
					month: current_datetime.getMonth() + 1,
					year: 2000 + current_datetime.getYear() - 100,

				};
				var json_obj = JSON.stringify(obj);
				console.log(json_obj);
				return json_obj
			},
		str_time: function (){
		       //body
		       return `${current_datetime.getHours()}:${current_datetime.getMinutes()}`

		    },
	}; return time_in_json_obj	
}
update_time()