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
    cur.execute("SELECT * FROM {}".format(table_name))

    rows = cur.fetchall()
    tickets_ids = {}
    for row in rows:
        tickets_ids[row[0]] = {"teamgantt_id": row[1],
                               "jira_last_update": row[2]}

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
    conn, cur, table_name = connect_to_db()
    with open('gantt_ticket.csv', mode='r') as gantt_csv:
        cur.copy_from(gantt_csv, table_name, sep=',')
        conn.commit()

    cur.close()
    conn.close()
    print('copy')

    # cmd = 'COPY {}({},{},{} FROM STDIN WITH (FORMAT CSV, HEADER FALSE)'.format(table_name, constants.jira_id,
    #                                                                            constants.teamgantt_id,
    #                                                                            constants.jira_last_update)
    # cur.copy_expert(cmd, gantt_csv)
    # conn.commit()
