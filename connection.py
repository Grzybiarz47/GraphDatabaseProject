from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable

##################################
#      NEO4J CONNECTION       #
##################################

class Connection:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    @staticmethod
    def __make_dict(result):
        ans = []
        for row in result:
            ans.append(dict(row))
        return ans

    def create_relation(self, person1_name, person2_name):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_and_return_friendship, person1_name, person2_name)
            for row in result:
                print("Created friendship between: {p1}, {p2}".format(p1=row['p1'], p2=row['p2']))

    @staticmethod
    def _create_and_return_friendship(tx, person1_name, person2_name):
        # To learn more about the Cypher syntax, see https://neo4j.com/docs/cypher-manual/current/
        # The Reference Card is also a good resource for keywords https://neo4j.com/docs/cypher-refcard/current/
        query = (
            "CREATE (p1:Person { name: $person1_name }) "
            "CREATE (p2:Person { name: $person2_name }) "
            "CREATE (p1)-[:KNOWS]->(p2) "
            "RETURN p1, p2"
        )
        result = tx.run(query, person1_name=person1_name, person2_name=person2_name)
        try:
            return [{"p1": row["p1"]["name"], "p2": row["p2"]["name"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def add_employee(self, properties : dict):
        with self.driver.session() as session:
            return session.read_transaction(self._create_employee, properties)

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
        result = tx.run(query, id=p.get("card_id"), 
                               first=p.get("first"), 
                               last=p.get("last"),
                               year=p.get("born"),
                               title=p.get("title"),
                               nation=p.get("nation"),
                               start=p.get("start"))

    def remove_employee(self, card_id):
        with self.driver.session() as session:
            return session.read_transaction(self._remove_employee_by_id, card_id)

    @staticmethod
    def _remove_employee_by_id(tx, card_id):
        query = (
            "MATCH (e:Employee {card_id: $id}) "
            "DELETE e"
        )
        result = tx.run(query, id=card_id)

    def list_all(self):
        with self.driver.session() as session:
            return session.read_transaction(self._return_all_employees)
    
    @staticmethod
    def _return_all_employees(tx):
        query = (
            "MATCH (e:Employee) "
            "RETURN properties(e) AS prop"
        )
        result = tx.run(query)
        return [row["prop"] for row in result]

    def find_employees_by_name(self, emp_firstname, emp_lastname):
        with self.driver.session() as session:
            return session.read_transaction(self._return_employees_by_name, emp_firstname, emp_lastname)

    @staticmethod
    def _return_employees_by_name(tx, emp_firstname, emp_lastname):
        query = (
            "MATCH (e:Employee) "
            "WHERE e.firstname = $emp_first AND e.lastname = $emp_last "
            "RETURN properties(e) AS prop"
        )
        result = tx.run(query, emp_first=emp_firstname, emp_last=emp_lastname)
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