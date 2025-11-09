import os
from dotenv import load_dotenv
import oracledb
import json
import dotenv

load_dotenv()

wallet_path = os.getenv("WALLET_PATH")

class OracleDB:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.dsn = os.getenv("DSN")
        self.user = os.getenv("USER")
        self.password = os.getenv("PASSWORD")
        self.conn = None
        self.cur = None

    def connect(self):
        if not self.conn:
            self.conn = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=self.dsn,
                config_dir=wallet_path 
            )
            self.cur = self.conn.cursor()

    def get_ip_address_info(self, ip_address=None, tenant_id=None):
        if not ip_address and not tenant_id:
            raise ValueError("At least one of account_name or tenant_id must be provided")

        where_clauses = [
            "ip.tenant_id = account.tenant_id",
            "ip.tf_compartment_id = compartment.resource_id",
            "ip.tf_lifecycle_state ='AVAILABLE'"
        ]
        bind_vars = {}
            

        if ip_address:
            where_clauses.append("ip.ip_address = :ip_address_param")
            bind_vars["ip_address_param"] = ip_address

        if tenant_id:
            where_clauses.append("ip.tenant_id = :tenant_id_param")
            bind_vars["tenant_id_param"] = tenant_id

        where_sql = " AND ".join(where_clauses)
        sql = f"""SELECT JSON_ARRAYAGG(
                JSON_OBJECT(
                    'ip_address' VALUE ip_address,
                    'region' VALUE tf_region,
                    'compartment_name' VALUE compartment_name,
                    'phonebook' VALUE phonebook,
                    'ip_address_type' VALUE ip_address_type,
                    'lifecycle_state' VALUE tf_lifecycle_state,
                    'account_name' VALUE account_name,
                    'account_admin_email' VALUE admin_email,
                    'vnic' VALUE vnic,
                    'subnet' VALUE subnet_id
                )
            ) AS json_result
            FROM (
                select ip.ip_address, ip.tf_region, ip.ip_address_type, account.account_name, account.admin_email, compartment.compartment_name, 
                compartment.phonebook, ip.attached_resource_id as vnic, ip.subnet_id, ip.tf_lifecycle_state
                from tb_ip_latest ip, TB_COMPARTMENT_LATEST compartment, tb_account_latest account WHERE {where_sql}
                order by resource_creation_time desc FETCH FIRST 1 ROWS ONLY
            )"""
        self.cur.execute(sql, bind_vars)
        json_str = self.cur.fetchall()
        return json_str

    def get_ip_history(self, ip_address):
        sql = """
            SELECT JSON_ARRAYAGG(
                    JSON_OBJECT(
                        KEY 'resource_creation_time'       VALUE TO_CHAR(resource_creation_time, 'YYYY-MM-DD"T"HH24:MI:SS'),
                        KEY 'region'            VALUE tf_region,
                        KEY 'compartment_name'    VALUE compartment_name,
                        KEY 'account_name'      VALUE account_name,
                        KEY 'phonebook'          VALUE phonebook,
                        KEY 'lifecycle_state'   VALUE tf_lifecycle_state,
                        KEY 'ip_address_type' VALUE ip_address_type
                    )
                ) AS json_result
            FROM (
                select ip.tf_region, ip.ip_address_type, account.account_name, account.admin_email, compartment.compartment_name, 
                compartment.phonebook, ip.tf_lifecycle_state, ip.resource_creation_time
                from tb_ip_event ip, TB_COMPARTMENT_LATEST compartment, tb_account_latest account 
                WHERE ip.tenant_id = account.tenant_id and ip.tf_compartment_id = compartment.resource_id and ip_address = :ip_address
                order by resource_creation_time desc FETCH FIRST 10 ROWS ONLY          
            
            ) 
        """
        self.cur.execute(sql, ip_address=ip_address)
        json_str = self.cur.fetchall()
        return json_str
    

    def get_account_details(self, account_name=None, tenant_id=None):
        if not account_name and not tenant_id:
            raise ValueError("At least one of account_name or tenant_id must be provided")

        where_clauses = []
        bind_vars = {}
        if account_name:
            where_clauses.append("account_name = :account_name")
            bind_vars["account_name"] = account_name
        if tenant_id:
            where_clauses.append("tenant_id = :tenant_id")
            bind_vars["tenant_id"] = tenant_id

        where_sql = " AND ".join(where_clauses)

        sql = f"""
            SELECT JSON_ARRAYAGG(
                    JSON_OBJECT(
                        KEY 'account_name'           VALUE account_name,
                        KEY 'tenant_id'             VALUE tenant_id,                        
                        KEY 'customer_type'         VALUE customer_type,
                        KEY 'owner_email'           VALUE owner_email,
                        KEY 'admin_email' VALUE admin_email,
                        KEY 'phonebook'             VALUE phonebook,
                        KEY 'full_management_chain' VALUE full_management_chain,
                        KEY 'lifecycle_state' VALUE tf_lifecycle_state,
                        KEY 'home_region'           VALUE home_region,
                        KEY 'subscribed_regions' VALUE subscribed_regions                        
                    ) RETURNING CLOB
                ) AS json_result
            FROM tb_account_latest
            WHERE {where_sql}
        """
        self.cur.execute(sql, bind_vars)
        row = self.cur.fetchone()
        if not row or row[0] is None:
            return None

        json_result = row[0]
        try:
            return json_result.read()  # works if LOB object
        except AttributeError:
            return json_result
        
    def get_account_details_for_manager(self, manager_name, level):
        if not manager_name or not level:
            raise ValueError("Manager and level must be provided")

        # manager_level6_email
        col_name = f"manager_level{level}_email"
        sql = f"""
            SELECT JSON_ARRAYAGG(
                    JSON_OBJECT(
                        KEY 'account_name'          VALUE account_name,
                        KEY 'tenant_id'             VALUE tenant_id,
                        KEY 'customer_type'         VALUE customer_type,
                        KEY 'phonebook'             VALUE phonebook,
                        KEY 'USAGE_TYPE'            VALUE USAGE_TYPE
                    ) RETURNING CLOB
                ) AS json_result
            FROM (
                SELECT * FROM tb_account_latest
                WHERE {col_name} = :manager_name
                FETCH FIRST 25 ROWS ONLY
            )
        """

        self.cur.execute(sql, manager_name=manager_name)
        row = self.cur.fetchone()
        if not row or row[0] is None:
            return None

        json_result = row[0]
        try:
            return json_result.read()
        except AttributeError:
            return json_result
    

    def close_connection(self):
        self.cur.close()
        self.conn.close()
        
