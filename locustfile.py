from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)  # Users will wait 1 to 3 seconds between requests

    @task
    def load_homepage(self):
        self.client.get("/")  # Test the home page

    @task
    def load_dash(self):
        self.client.get("/dash")  # Test the dash page

    @task
    def load_search(self):
        self.client.get("/search")  # Test the search page

    @task
    def load_history(self):
        self.client.get("/history_and_details")  # Test history and details page


# ----------------------------------------
# Directions for use (in terminal):
# 1. Run locust -f locustfile.py
# 2. If it can't handle 10,000 users, run locust -f locustfile.py --master,
#          then locust -f locustfile.py --worker --master-host=<MASTER_IP>
# 3. Replace with the url of our website: self.client.get("http://yourwebsite.com/")
# ----------------------------------------------
# Reading Locust outputs:
# Response time: How long it takes for the server to respond
# Failures: Number of failed requests
# RPS (Requests per second): Throughput of the server (how often does it succeed within a given time?)
# ^^^ looking for the RPS to be 10000/second
