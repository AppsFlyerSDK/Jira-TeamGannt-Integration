import psycopg2

import config.config as config
import constants


def connect_to_db():
    db_conn_str = config.db_string
    db_user = config.db_user
    db_password = config.db_password
    db_name = config.db_name
    db_scheme = config.db_schema
    db_table = config.db_table_name
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
        cur.copy_from(gantt_csv, table_name, sep=';')
        conn.commit()

    cur.close()
    conn.close()
    print('copy')


def update_ticket_timestamp(jira_id, timestamp):
    conn, cur, table_name = connect_to_db()
    cur.execute(
        "UPDATE {} SET jira_last_update = %s WHERE jira_id = %s".format(table_name), (timestamp, jira_id))
    conn.commit()

    cur.close()
    conn.close()


def update_ticket(param, ticket):
    conn, cur, table_name = connect_to_db()
    query_str = "UPDATE {} SET jira_last_update = '{}', name = '{}', team = '{}', status = '{}', type = '{}', epic = '{}', estimation_time = '{}', assignee = '{}' WHERE jira_id = '{}'".format(
        table_name, str(ticket.ticket_jira_last_update), str(ticket.ticket_summary), str(ticket.team_name),
        str(ticket.ticket_status),
        str(ticket.ticket_type), str(ticket.epic), str(ticket.ticket_estimation_time), str(ticket.assignee), str(ticket.ticket_jira_id))

    cur.execute(query_str)
    conn.commit()

    cur.close()
    conn.close()
