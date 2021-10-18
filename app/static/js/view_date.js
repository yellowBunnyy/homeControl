// window.onload = create_date;
// console.log('viewdaate')
var date_obj = {

	days: function(lp){
		var day_list = ['Niedziela', 'Poniedziałek', 'Wtorek', 'Środa', 'Czwartek','Piątek','Sobota']
		return day_list[lp]	
	},
	months: function(lp){
		var month_list = ['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec', 'Lipiec',
		'Sierpień', 'Wrzesień','Październik', 'Listopad', 'Grudzień']
		return month_list[lp]
	},


	frends_birthday: function(){
		//tu muszę pomyśleć :)
	}
}
function connect_to_server(){
	// console.log('date!!')
	var request = new XMLHttpRequest();
	request.open('GET','/current');	
	request.addEventListener('load', function(){				
		console.log(this.responseText);
		//show date on site
		document.getElementById('show_date').innerHTML = `${this.responseText}`;
})
	request.send();




}

function create_date() {
	var obj = new Date();
	var day = obj.getUTCDate();
	var month = obj.getMonth();
	var year = obj.getYear() + 2000 - 100;	
	
	
}

// create_date()
connect_to_server()