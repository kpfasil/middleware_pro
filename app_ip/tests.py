from django.test import TestCase, Client
from django.core.cache import cache
from django.http import JsonResponse
import time

class RateLimitingMiddlewareTests(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        # Clear the cache
        cache.clear()

    def test_within_limit(self):
        """Test that requests within the limit pass through."""
        for _ in range(99):
            response = self.client.get("/ip_block/")
            self.assertEqual(response.status_code, 200)
        #check response ok
        response = self.client.get("/ip_block/")
        self.assertEqual(response.status_code, 200)
        print("test_within_limit passed")
        
    
    def test_exceeds_limit(self):
        """Test that exceeding the limit returns 429."""
        for _ in range(100):
            response = self.client.get("/ip_block/")
            self.assertEqual(response.status_code, 200)

        # Exceed the limit
        response = self.client.get("/ip_block/")
        self.assertEqual(response.status_code, 429)
        print("test_exceeds_limit passed")

    def test_ip_tracking_separately(self):
        """Ensure requests from different IPs are tracked independently."""
        client_1 = Client(REMOTE_ADDR="192.168.1.1")
        client_2 = Client(REMOTE_ADDR="192.168.1.2")

        for _ in range(100):
            response = client_1.get("/ip_block/")
            self.assertEqual(response.status_code, 200)

        # IP 1 exceeds limit
        response = client_1.get("/ip_block/")
        self.assertEqual(response.status_code, 429)

        # IP 2 still within limit
        response = client_2.get("/ip_block/")
        self.assertEqual(response.status_code, 200)
        print("test_ip_tracking_separately passed")