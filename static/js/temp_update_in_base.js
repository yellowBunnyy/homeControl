
function update_data_temp(){
	console.log('all temps was update in base_update_temp');
    //console.log('in  update_data')    
    var my_read = new XMLHttpRequest();
	my_read.open('GET', '/updatetemp');
	my_read.send();
	my_read.onload = function(){console.log(my_read.responseText)};
	setTimeout(update_data_temp, 60000);
} 

update_data_temp();