class Mailbox:
    def __init__(self, store):
        self.messages = store

    def send(self, to, body):
        # unrelated to LLMs: a decoy for the scanner
        return self.messages.create(to=to, body=body)
