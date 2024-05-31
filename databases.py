import sqlite3
from sqlite3 import Error

class DataBase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.unique_rows = None
        self.rows = None
        self.where_statement = None
        self.input_value = None
    
    def create_connection(self, db_file):
        """ create a database connection to a SQLite database """
        try:
            self.conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)
        return self.conn

    def create_table(self, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)
    
    def main_db(self):
        sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS projects (
                                        id integer PRIMARY KEY,
                                        fig_acc text NOT NULL,
                                        fig_curr text,
                                        fig_name text,
                                        fig_ipn text,
                                        fig_bank_code text,
                                        fig_bank_name text,
                                        contr_acc text,
                                        contr_name text,
                                        contr_ipn text,
                                        contr_bank_code text,
                                        contr_bank_name text,
                                        pay_purp text,
                                        doc_num text,
                                        doc_date integer,
                                        direction text,
                                        sum_ct integer,
                                        sum_dt integer,
                                        fill_up boolean
                                    ); """
        
        # create a database connection
        self.conn = self.create_connection(self.db_name)
        
        # create tables
        if self.conn is not None:
            # create projects table
            self.create_table(sql_create_projects_table)
        else:
            print("Error! cannot create the database connection.")
        return self.conn

    def create_project(self, project):
        """
        Create a new project into the projects table
        :param conn:
        :param project:
        :return: project id
        """
        sql = ''' INSERT INTO projects(
                fig_acc,fig_curr,fig_name,fig_ipn,fig_bank_code,fig_bank_name,
                contr_acc,contr_name,contr_ipn,contr_bank_code, contr_bank_name,
                pay_purp,doc_num,doc_date,direction,sum_ct,sum_dt,fill_up)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
        cur = self.conn.cursor()
        cur.execute(sql, project)
        self.conn.commit()
        return cur.lastrowid
        
    def write_db(self,fig_acc,fig_curr,fig_name,fig_ipn,fig_bank_code,fig_bank_name,contr_acc,contr_name,contr_ipn,contr_bank_code,contr_bank_name,pay_purp,doc_num,doc_date,direction,sum_ct,sum_dt,fill_up):
        with self.conn:
        # create a new project
            project = (fig_acc,fig_curr,fig_name,fig_ipn,fig_bank_code,fig_bank_name,contr_acc,contr_name,contr_ipn,contr_bank_code,contr_bank_name,pay_purp,doc_num,doc_date,direction,sum_ct,sum_dt,fill_up)
            self.create_project(project)

    def select_unique_acc_and_curr(self):
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("SELECT DISTINCT fig_acc, fig_curr, fill_up FROM projects WHERE LENGTH(fig_curr) = 3 OR fig_curr IS NULL")
            self.unique_rows = cur.fetchall()
            return self.unique_rows
    
    def select_transactions(self, fig_acc, fig_curr, fill_up):
        basic_statement = "WHERE (sum_ct_new is NOT NULL) AND (sum_dt_new is NOT NULL) AND (doc_date is NULL OR doc_date is NOT NULL AND (doc_date != 'ПРИЗНАЧЕННЯ:' AND doc_date != 'БАНК:' AND doc_date != 'КОРЕСПОНДЕНТ:'))"
        # 
        if fig_curr is None:
            self.where_statement = basic_statement + " AND fig_acc=?"
            self.input_value = (fig_acc,)
        else:
            self.where_statement =  basic_statement + " AND fig_acc=? AND fig_curr=?"
            self.input_value = (fig_acc,fig_curr,)
        with self.conn:
            cur = self.conn.cursor()
            if fill_up == 1:
                self.rows = cur.execute(f'''
                                            SELECT  
                                                    fig_acc,
                                                    fig_curr,
                                                    fig_name,
                                                    fig_ipn,
                                                    fig_bank_code,
                                                    fig_bank_name,
                                                    contr_acc,
                                                    contr_name_new as contr_name,
                                                    contr_ipn,
                                                    contr_bank_code,
                                                    contr_bank_name_new as contr_bank_name,
                                                    pay_purp_new as pay_purp,
                                                    doc_num,
                                                    doc_date,
                                                    direction_new as direction,
                                                    sum_ct_new,
                                                    sum_dt_new
                                            FROM 
                                            (SELECT *,
                                                        ROW_NUMBER() OVER (ORDER BY fig_acc) AS row_num_main
                                                FROM projects
                                            ) AS main
                                            Left JOIN (
                                                SELECT contr_name as contr_name_new, row_num_second
                                                FROM (
                                                    SELECT *,
                                                        ROW_NUMBER() OVER (ORDER BY fig_acc) AS row_num_second
                                                    FROM projects
                                                )
                                                WHERE contr_name_new IS NOT NULL
                                                                )
                                            AS second
                                            ON (second.row_num_second-main.row_num_main) BETWEEN 2 and 3

                                            Left JOIN (
                                                SELECT contr_bank_name as contr_bank_name_new, row_num_second
                                                FROM (
                                                    SELECT *,
                                                        ROW_NUMBER() OVER (ORDER BY fig_acc) AS row_num_second
                                                    FROM projects
                                                )
                                                WHERE contr_bank_name_new IS NOT NULL
                                                                )
                                            AS third
                                            ON (third.row_num_second-main.row_num_main) BETWEEN 1 and 2
                                            
                                            Left JOIN (
                                                SELECT pay_purp as pay_purp_new, row_num_second
                                                FROM (
                                                    SELECT *,
                                                        ROW_NUMBER() OVER (ORDER BY fig_acc) AS row_num_second
                                                    FROM projects
                                                )
                                                WHERE pay_purp_new IS NOT NULL
                                                                )
                                            AS fourth
                                            ON (fourth.row_num_second-main.row_num_main) BETWEEN 0 and 1

                                            Left JOIN (
                                                SELECT direction as direction_new, row_num_second
                                                FROM (
                                                    SELECT *,
                                                        ROW_NUMBER() OVER (ORDER BY fig_acc) AS row_num_second
                                                    FROM projects
                                                )
                                                WHERE direction_new IS NOT NULL
                                                                )
                                            AS fifth
                                            ON (fifth.row_num_second-main.row_num_main) BETWEEN 0 and 1
                                        
                                            Left JOIN (
                                                SELECT sum_ct as sum_ct_new, row_num_second
                                                FROM (
                                                    SELECT *,
                                                        ROW_NUMBER() OVER (ORDER BY fig_acc) AS row_num_second
                                                    FROM projects
                                                )
                                                WHERE sum_ct_new IS NOT NULL
                                                                )
                                            AS six
                                            ON (six.row_num_second-main.row_num_main) BETWEEN 0 and 1
                                        
                                            Left JOIN (
                                                SELECT sum_dt as sum_dt_new, row_num_second
                                                FROM (
                                                    SELECT *,
                                                        ROW_NUMBER() OVER (ORDER BY fig_acc) AS row_num_second
                                                    FROM projects
                                                )
                                                WHERE sum_dt_new IS NOT NULL
                                                                )
                                            AS seven
                                            ON (seven.row_num_second-main.row_num_main) BETWEEN 0 and 1
                                            
                                            {self.where_statement}
                                            ORDER BY fig_acc
                                        ''', 
                                        self.input_value)
            else:
                self.rows = cur.execute(f'''
                                            SELECT 
                                                fig_acc,
                                                fig_curr,
                                                fig_name,
                                                fig_ipn,
                                                fig_bank_code,
                                                fig_bank_name,
                                                contr_acc,
                                                contr_name,
                                                contr_ipn,
                                                contr_bank_code,
                                                contr_bank_name,
                                                pay_purp,
                                                doc_num,
                                                doc_date,
                                                direction,
                                                sum_ct,
                                                sum_dt
                                            FROM projects 
                                            {self.where_statement.replace("_new","")}
                                            ORDER BY fig_acc
                                        ''', 
                                        self.input_value)
            return self.rows

    def create_pt(self, fill_up):
        with self.conn:
            cur = self.conn.cursor()
            if fill_up == 1:
                self.rows = cur.execute(f'''
                                            SELECT  
                                                    MIN(doc_date) as doc_date_min,
                                                    MAX(doc_date) as doc_date_max,
                                                    COUNT(CASE WHEN sum_ct_new > 0 THEN sum_ct_new END) sum_ct_qty,
                                                    SUM(sum_ct_new) as sum_ct_qly,
                                                    COUNT(CASE WHEN sum_dt_new > 0 THEN sum_dt_new END) sum_dt_qty,
                                                    SUM(sum_dt_new) as sum_dt_qly,
                                                    contr_acc,
                                                    contr_name_new as contr_name, 
                                                    contr_ipn,
                                                    contr_bank_code,
                                                    contr_bank_name_new as contr_bank_name
                                            FROM 
                                            (SELECT *,
                                                        ROW_NUMBER() OVER (ORDER BY fig_acc) AS row_num_main
                                                FROM projects
                                            ) AS main
                                            Left JOIN (
                                                SELECT contr_name as contr_name_new, row_num_second
                                                FROM (
                                                    SELECT *,
                                                        ROW_NUMBER() OVER (ORDER BY fig_acc) AS row_num_second
                                                    FROM projects
                                                )
                                                WHERE contr_name_new IS NOT NULL
                                                                )
                                            AS second
                                            ON (second.row_num_second-main.row_num_main ) BETWEEN 2 and 3

                                            Left JOIN (
                                                SELECT contr_bank_name as contr_bank_name_new, row_num_second
                                                FROM (
                                                    SELECT *,
                                                        ROW_NUMBER() OVER (ORDER BY fig_acc) AS row_num_second
                                                    FROM projects
                                                )
                                                WHERE contr_bank_name_new IS NOT NULL
                                                                )
                                            AS third
                                            ON (third.row_num_second-main.row_num_main ) BETWEEN 1 and 2
                                            
                                            Left JOIN (
                                                SELECT pay_purp as pay_purp_new, row_num_second
                                                FROM (
                                                    SELECT *,
                                                        ROW_NUMBER() OVER (ORDER BY fig_acc) AS row_num_second
                                                    FROM projects
                                                )
                                                WHERE pay_purp_new IS NOT NULL
                                                                )
                                            AS fourth
                                            ON (fourth.row_num_second-main.row_num_main ) BETWEEN 0 and 1

                                            Left JOIN (
                                                SELECT direction as direction_new, row_num_second
                                                FROM (
                                                    SELECT *,
                                                        ROW_NUMBER() OVER (ORDER BY fig_acc) AS row_num_second
                                                    FROM projects
                                                )
                                                WHERE direction_new IS NOT NULL
                                                                )
                                            AS fifth
                                            ON (fifth.row_num_second-main.row_num_main ) BETWEEN 0 and 1
                                        
                                            Left JOIN (
                                                SELECT sum_ct as sum_ct_new, row_num_second
                                                FROM (
                                                    SELECT *,
                                                        ROW_NUMBER() OVER (ORDER BY fig_acc) AS row_num_second
                                                    FROM projects
                                                )
                                                WHERE sum_ct_new IS NOT NULL
                                                                )
                                            AS six
                                            ON (six.row_num_second-main.row_num_main ) BETWEEN 0 and 1
                                        
                                            Left JOIN (
                                                SELECT sum_dt as sum_dt_new, row_num_second
                                                FROM (
                                                    SELECT *,
                                                        ROW_NUMBER() OVER (ORDER BY fig_acc) AS row_num_second
                                                    FROM projects
                                                )
                                                WHERE sum_dt_new IS NOT NULL
                                                                )
                                            AS seven
                                            ON (seven.row_num_second-main.row_num_main ) BETWEEN 0 and 1

                                            {self.where_statement}
                                            GROUP BY contr_acc, contr_ipn, contr_bank_code
                                        ''', 
                                        self.input_value)
            else:
                self.rows = cur.execute(f'''
                                            SELECT
                                                MIN(doc_date) as doc_date_min,
                                                MAX(doc_date) as doc_date_max,
                                                COUNT(CASE WHEN sum_ct > 0 THEN sum_ct END) sum_ct_qty,
                                                SUM(sum_ct) as sum_ct_qly,
                                                COUNT(CASE WHEN sum_dt > 0 THEN sum_dt END) sum_dt_qty,
                                                SUM(sum_dt) as sum_dt_qly,
                                                contr_acc, 
                                                contr_name, 
                                                contr_ipn,
                                                contr_bank_code,
                                                contr_bank_name
                                            FROM projects 
                                            {self.where_statement.replace("_new","")}
                                            GROUP BY contr_acc, contr_ipn, contr_bank_code
                                        ''',
                                        self.input_value)
            return self.rows
					