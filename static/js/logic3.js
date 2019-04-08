console.log('logic3.js');

var cars = [
	{ "make":"Porsche", "model":"911S" },
	{ "make":"Mercedes-Benz", "model":"220SE" },
	{ "make":"Jaguar","model": "Mark VII" }
];
var text = 'simple text';
window.onload = function() {
	// setup the button click
	document.getElementById("btn").onclick = function() {
		doWork();
	};
}

function doWork() {
	console.log('in doWork')
	// ajax the JSON to the server
	$.post("rec", text, function(){

	});
	// stop link reloading the page
 event.preventDefault();
}