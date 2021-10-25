import psycopg2


class DataBase:

    def connect_to_db(self):
        conn = psycopg2.connect(dbname='test',
                                user='seba',
                                password='passwd',
                                host='172.18.0.2',
                                port='5432')
        print('we have connection to db')
        return conn
    
    def create_table(self, conn):
        cur = conn.cursor()
        command = """
                CREATE TABLE IF NOT EXISTS temperature (
                ID INT PRIMARY KEY, 
                DATE TEXT, 
                HOUR TEXT,
                SALON INT,
                MALY_POKOJ INT,
                KUCHNIA INT,
                WC INT,
                OUTSIDE INT);
                """
        print("table was created")
        cur.execute(command)
        conn.commit()
        cur.close()
        # conn.close()
        

    def send_data_to_db(self, conn):
        pass

    def add_fake_data(self, conn):
        cur = conn.cursor()
        data = (0, '01-12-2020', '09-30', 
                20,
                21,
                22,
                23,
                24,
                )
        id, data, hour, salon, m_pok, kuch, wc, outside = data
        command = f"""
        INSERT INTO temperature (ID,DATE,HOUR,SALON,
        MALY_POKOJ,KUCHNIA,WC, OUTSIDE)
        VALUES({id},{data},{hour},{salon},{m_pok},{kuch},{wc},{outside});
        """
        cur.execute(command, data)
        conn.commit()
        cur.close()
        conn.close()
        print('data was saved in database')
    
    def fetch_data_from_db(self):
        pass

inst = DataBase()
conn = inst.connect_to_db()
inst.create_table(conn=conn)
inst.add_fake_data(conn=conn)