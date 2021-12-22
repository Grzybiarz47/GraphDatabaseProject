from neo4j import GraphDatabase
from os import environ

##################################
#        NEO4J CONNECTION        #
##################################

uri = environ["CLOUDS_URI"]
user = environ["CLOUDS_USER"]
password = environ["CLOUDS_PASSWORD"]

class Connection:

    def __init__(self, uri=uri, user=user, password=password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()
    
    def __del__(self):
        self.driver.close()

    @staticmethod
    def __make_dict(result):
        ans = []
        for row in result:
            ans.append(dict(row))
        return ans

    ##################################
    #        MANAGE RELATIONS        #
    ##################################
    def add_relation(self, boss_id, emp_id):
        with self.driver.session() as session:
            session.read_transaction(self._create_relation, boss_id, emp_id)

    @staticmethod
    def _create_relation(tx, boss_id, emp_id):
        query = (
            "MATCH (b:Employee { card_id: $boss_id }) "
            "MATCH (e:Employee { card_id: $emp_id }) "
            "CREATE (e)-[:IS_SUBJECT_TO]->(b) "
        )
        tx.run(query, boss_id=boss_id, emp_id=emp_id)

    def remove_relation(self, boss_id, emp_id):
        with self.driver.session() as session:
            session.read_transaction(self._delete_relation, boss_id, emp_id)

    @staticmethod
    def _delete_relation(tx, boss_id, emp_id):
        query = (
            "MATCH (b:Employee { card_id: $boss_id }) "
            "MATCH (e:Employee { card_id: $emp_id }) "
            "DELETE (e)-[:IS_SUBJECT_TO]->(b) "
        )
        tx.run(query, boss_id=boss_id, emp_id=emp_id)

    ##################################
    #      ADD AND DELETE NODE       #
    ##################################
    def add_employee(self, properties : dict):
        with self.driver.session() as session:
            session.read_transaction(self._create_employee, properties)

    @staticmethod
    def _create_employee(tx, p : dict):
        query = (
            "CREATE (n:Employee { "
            "card_id:$id, "
            "firstname:$first, "
            "lastname:$last, "
            "born:$year, "
            "title:$title, "
            "nationality:$nation, "
            "job_started:$start "
            "})"
        )
        tx.run(query, id=p.get("card_id"), 
                      first=p.get("first"), 
                      last=p.get("last"),
                      year=p.get("born"),
                      title=p.get("title"),
                      nation=p.get("nation"),
                      start=p.get("start"))

    def remove_employee(self, card_id):
        with self.driver.session() as session:
            session.read_transaction(self._remove_employee_by_id, card_id)

    @staticmethod
    def _remove_employee_by_id(tx, card_id):
        query = (
            "MATCH (e:Employee {card_id: $id}) "
            "DETACH DELETE e"
        )
        tx.run(query, id=card_id)

    def change_title(self, card_id, title):
        with self.driver.session() as session:
            session.read_transaction(self._set_title, card_id, title)

    @staticmethod
    def _set_title(tx, card_id, title):
        query = (
            "MATCH (e:Employee {card_id: $id}) "
            "SET e.title=$title"
        )
        tx.run(query, id=card_id, title=title)

    ##################################
    #          SELECT NODES          #
    ##################################
    def list_all(self):
        with self.driver.session() as session:
            return session.read_transaction(self._return_all_employees)
    
    @staticmethod
    def _return_all_employees(tx):
        query = (
            "MATCH (e:Employee) "
            "RETURN properties(e) AS prop "
            "ORDER BY e.lastname, e.firstname, e.card_id"
        )
        result = tx.run(query)
        return [row["prop"] for row in result]

    def find_employees_by_name(self, emp_firstname, emp_lastname):
        with self.driver.session() as session:
            return session.read_transaction(self._return_employees_by_name, emp_firstname, emp_lastname)

    @staticmethod
    def _return_employees_by_name(tx, emp_firstname, emp_lastname):
        query = (
            "MATCH (e:Employee {firstname: $emp_first, lastname:$emp_last}) "
            "RETURN properties(e) AS prop"
        )
        result = tx.run(query, emp_first=emp_firstname, emp_last=emp_lastname)
        return [row["prop"] for row in result]

    def find_employee_by_id(self, card_id):
        with self.driver.session() as session:
            return session.read_transaction(self._return_employee_by_id, card_id)

    @staticmethod
    def _return_employee_by_id(tx, card_id):
        query = (
            "MATCH (e:Employee {card_id: $card_id}) "
            "RETURN properties(e) AS prop"
        )
        result = tx.run(query, card_id=card_id)
        return [row["prop"] for row in result]

    def check_if_exists(self, card_id):
         with self.driver.session() as session:
            return session.read_transaction(self._count_employees, card_id) > 0

    @staticmethod
    def _count_employees(tx, card_id):
        query = (
            "MATCH (e:Employee) "
            "WHERE e.card_id=$id "
            "RETURN count(*) AS count"
        )
        result = tx.run(query, id=card_id)
        result = Connection.__make_dict(result)
        return result[0]["count"]

    def next_card_id(self):
        with self.driver.session() as session:
            return session.read_transaction(self._max_id) + 1

    @staticmethod
    def _max_id(tx):
        query = (
            "MATCH (e:Employee) "
            "RETURN max(e.card_id) AS max_id"
        )
        result = tx.run(query)
        result = Connection.__make_dict(result)
        return result[0]["max_id"]

    def list_supervisors(self, card_id):
        with self.driver.session() as session:
            return session.read_transaction(self._return_supervisors, card_id)
    
    @staticmethod
    def _return_supervisors(tx, card_id):
        query = (
            "MATCH (e:Employee { card_id:$card_id })-[:IS_SUBJECT_TO *1..]->(b: Employee) "
            "RETURN b.card_id AS id, b.firstname AS first, b.lastname AS last, b.title AS title"
        )
        result = tx.run(query, card_id=card_id)
        result = Connection.__make_dict(result)
        return result

    def list_subordinates(self, card_id):
        with self.driver.session() as session:
            return session.read_transaction(self._return_subordinates, card_id)
    
    @staticmethod
    def _return_subordinates(tx, card_id):
        query = (
            "MATCH (s:Employee)-[:IS_SUBJECT_TO *1..]->(e: Employee { card_id:$card_id }) "
            "RETURN s.card_id AS id, s.firstname AS first, s.lastname AS last, s.title AS title"
        )
        result = tx.run(query, card_id=card_id)
        result = Connection.__make_dict(result)
        return result

    def list_direct_subordinates(self, card_id):
        with self.driver.session() as session:
            return session.read_transaction(self._return_direct_subordinates, card_id)

    @staticmethod
    def _return_direct_subordinates(tx, card_id):
        query = (
            "MATCH (s:Employee)-[:IS_SUBJECT_TO *1..1]->(e: Employee { card_id:$card_id }) "
            "RETURN s.card_id AS id, s.firstname AS first, s.lastname AS last, s.title AS title"
        )
        result = tx.run(query, card_id=card_id)
        result = Connection.__make_dict(result)
        return result