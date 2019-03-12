import psycopg2

from utils import utils
import constants


def connect_to_db():
    db_conn_str, db_user, db_password, db_name, db_scheme, db_table = utils.get_db_config_params()
    conn = psycopg2.connect(user=db_user,
                            dbname=db_name,
                            password=db_password,
                            host=db_conn_str)

    # cursor
    cur = conn.cursor()
    cur.execute("SET search_path TO " + db_scheme)
    return conn, cur, db_table


def get_tickets_from_db():
    conn, cur, table_name = connect_to_db()
    cur.execute("SELECT {}, {} FROM {}".format(constants.jira_id, constants.jira_last_update, table_name))

    rows = cur.fetchall()
    tickets_ids = []
    for row in rows:
        tickets_ids.append((row[0], row[1]))

    cur.close()
    conn.close()
    return tickets_ids


def write_ticket_to_db(ticket):
    conn, cur, table_name = connect_to_db()
    cur.execute(
        "INSERT INTO {} ({},{},{}) VALUES ({},{},{})".format(table_name, constants.jira_id, constants.teamgantt_id,
                                                             constants.jira_last_update, ticket.ticket_id, 1,
                                                             ticket.ticket_last_update))
    print("{} inserted".format(ticket.ticket_key))
    cur.close()
    conn.close()


def copy_csv_into_db():
    return None
