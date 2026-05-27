from locust import HttpUser, task, between

class ShopUser(HttpUser):
    wait_time = between(0.01, 0.1)

    @task
    def buy_product(self):
        self.client.post("/purchase", json={
            "user_id": 1,
            "product_id": 42,
            "purchased_count": 1
        })