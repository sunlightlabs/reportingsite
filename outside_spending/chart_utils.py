from django.db import connection

""" Get weekly spending amount using mysql's week functions. More here: http://dev.mysql.com/doc/refman/5.5/en/date-and-time-functions.html#function_week """
def get_weekly_spending(committee_fec_id):
    
    cursor = connection.cursor()
    
    
    # Data modifying operation - commit required
    cursor.execute("UPDATE bar SET foo = 1 WHERE baz = %s", [self.baz])


    # Data retrieval operation - no commit required
    cursor.execute("SELECT foo FROM bar WHERE baz = %s", [self.baz])
    row = cursor.fetchone()

    return row