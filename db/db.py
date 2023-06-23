import pymysql
import os


def get_database_connection():
    global connection
    try:
        DB_IP_addr = os.environ["DB_IP_ADDR"]
    except KeyError:
        DB_IP_addr = "10.0.0.16"
    try:
        # Connect to the database
        connection = pymysql.connect(host=DB_IP_addr, user="james", password="password", db="token")
        return connection
    except pymysql.err.OperationalError as e:
        print("Failed to connect to the database:", e)
        raise Exception("Failed to connect to the database:", e)


def get_api_key():
    api_key = {}
    connection = get_database_connection()
    with connection.cursor() as cursor:
        try:
            # Execute the SQL query
            cursor.execute("select * from api_key")
            res = cursor.fetchall()
            for a in res:
                api_key[a[0]] = a[1]

        except Exception as e:
            pass

    # Commit the changes and close the connection
    connection.commit()
    connection.close()
    return api_key


def insert_member_id(data):
    global connection
    try:
        DB_IP_addr = os.environ["DB_IP_ADDR"]
    except KeyError:
        DB_IP_addr = "10.0.0.16"

    DB_IP_addr = os.environ["DB_IP_ADDR"]
    connection = pymysql.connect(host=DB_IP_addr, user="james", password="password", db="slack")
    with connection.cursor() as cursor:
        for id, name in data.items():
            try:
                cursor.execute("INSERT INTO Members (ID, Name) VALUES (%s, %s)", (id, name))
                # Execute the SQL query

            except Exception as e:
                print(e)
                pass

    # Commit the changes and close the connection
    connection.commit()
    connection.close()


api_key = get_api_key()

palm_api_key = api_key["PALM_API_KEY"]
azure_api_key = api_key["AZURE_TRANSLATE_API"]
app_token = api_key["PALM_SLACK_APP_TOKEN"]
bot_token = api_key["PALM_SLACK_BOT_TOKEN"]
signing_secret = api_key["PALM_SLACK_SIGNING_SECRET"]
bard_api_key = api_key["BARD_API_KEY"]
