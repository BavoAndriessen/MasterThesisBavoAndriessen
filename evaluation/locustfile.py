from locust import HttpUser, task

class productpage_user(HttpUser):
    @task
    def productpage(self):
        self.client.get("/productpage")

    