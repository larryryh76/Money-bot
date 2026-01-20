from faker import Faker

class PersonaManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.fake = Faker()

    def create_persona(self, account_id):
        profile = self.fake.profile()
        persona = {
            "account_id": account_id,
            "name": profile['name'],
            "address": profile['address'],
            "birthdate": str(profile['birthdate']),
            "sex": profile['sex'],
            "mail": profile['mail']
        }
        self.db_manager.add_persona(persona)
        return persona

    def get_persona(self, account_id):
        return self.db_manager.get_persona(account_id)

    def get_answer(self, account_id, question):
        return self.db_manager.get_persona_answer(account_id, question)

    def store_answer(self, account_id, question, answer):
        self.db_manager.add_persona_answer(account_id, question, answer)
