import itertools
from locust import HttpUser, task, between

USER_EMAILS = [f"loadtest{i}@example.com" for i in range(1, 101)]
PASSWORD = "12345678X"

_email_iter = itertools.cycle(USER_EMAILS)

class LedgerUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.email = next(_email_iter)
        r = self.client.post("/login", json={"email": self.email, "password": PASSWORD}, name="/login")
        if r.status_code != 200:
            raise RuntimeError(f"Login failed for {self.email}: {r.status_code} {r.text}")

    @task
    def list_transactions(self):
        self.client.get("/transactions", name="GET /transactions")
