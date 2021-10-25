import psycopg2
conn = psycopg2.connect(dbname='test',
                        user='seba',
                        password='passwd',
                        host='0.0.0.0',
                        port='5432')
print('we have connection to db')