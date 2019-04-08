from flask import Flask, render_template, request, redirect, Response
import sys
import random, json
app = Flask(__name__)
# from py_env.dj.src.rasp import blinking

@app.route('/')

def home():
    return render_template('home.html', name='cokolwiek')

# @app.route('/blink')
# def blink():
#     return render_template('blink.html')

# @app.route('/up')
# def get_data():
#     return render_template('home.html', varible='other content')

@app.route('/rec', methods = ['POST'])
def worker():
    print(request.args)
    # print(request.format)
    print(request.values)
    print(request.files)

    # for item in data:
    #     result += str(item['make']) + '\n'
    return 'cololwiek'

# @app.route('/process', methods=['GET'])
# def process():
#     return jsonify(turn_on=blinking.set_pin(20,1),
#                    text='wlaczono swiatlo')

if __name__ == '__main__':
    app.run(debug=1)