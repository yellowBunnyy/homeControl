<snippet>
  <content><![CDATA[
# ${1:Home Control System}
This project monitor:
    - temperature
    - humidity
    we use here DHT11 and DHT22 sensors. This last is used outside.
Regulate temperature on heaters using termostated regulator:
    - SALUS T30NC 24V (24V for safty)
Turn on and off circuit AC 230V.
Above regulation we can set on time scope.
Data from sensors we aggregate and store in database where can 
plot grahps.
## Installation
pip install -r requirements.txt
## Usage
python3 flask_home.py
## License
TODO: Write license
]]></content>
  <tabTrigger>readme</tabTrigger>
</snippet>