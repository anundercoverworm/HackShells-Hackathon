import unittest

from fastapi.testclient import TestClient

from backend.main import app


class BackendIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_products_endpoint_returns_data(self):
        response = self.client.get("/api/products")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_inventories_endpoint_returns_data(self):
        response = self.client.get("/api/inventories")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)

    def test_default_products_have_price_history(self):
        products = self.client.get("/api/products").json()
        self.assertGreater(len(products), 0)

        for product in products:
            history = self.client.get(f"/api/products/{product['id']}/price-history").json()
            self.assertIsInstance(history, list)
            self.assertGreaterEqual(len(history), 1)

    def test_marketplace_history_does_not_overwrite_current_price(self):
        products = self.client.get("/api/products").json()
        product_id = products[0]["id"]
        original = products[0]["current_price"]

        self.client.get(f"/api/products/{product_id}/price-history").json()
        refreshed = self.client.get("/api/products").json()
        updated = next(item for item in refreshed if item["id"] == product_id)

        self.assertEqual(updated["current_price"], original)

    def test_marketplace_history_has_multiple_distinct_values(self):
        from backend import data_generation

        item_data = data_generation.get_item_data("Test Product")
        values = [entry.estimated_market_value for entry in item_data]

        self.assertGreater(len(set(values)), 1)

    def test_market_history_values_are_realistic(self):
        from backend import data_generation

        history = data_generation.get_market_history("Test Product", base_value=500.0)
        values = [entry.estimated_market_value for entry in history]

        self.assertEqual(len(history), 7)
        self.assertLess(max(values) - min(values), 100.0)
        self.assertNotAlmostEqual(values[-1], 500.0, places=2)

    def test_product_history_stays_tied_to_user_price(self):
        from backend import prices

        product_id = 1
        current_price = 500.0
        history = prices.build_realistic_history(product_id, current_price)
        values = [entry["price"] for entry in history]

        self.assertEqual(len(history), 7)
        self.assertEqual(len(set(values)), 1)
        self.assertEqual(values[0], current_price)

    def test_invalid_price_history_is_rebuilt(self):
        from backend import prices

        product_id = 1
        prices.price_history = [
            {"product_id": product_id, "price": 10000.0, "date": "2024-01-01T00:00:00"},
            {"product_id": product_id, "price": 9999.0, "date": "2024-01-02T00:00:00"},
        ]

        rebuilt = self.client.get(f"/api/products/{product_id}/price-history").json()

        self.assertIsInstance(rebuilt, list)
        self.assertTrue(all(0 < entry["price"] < 10000 for entry in rebuilt))
        self.assertLess(max(entry["price"] for entry in rebuilt) - min(entry["price"] for entry in rebuilt), 1000)

    def test_price_history_endpoint_tracks_updates(self):
        products = self.client.get("/api/products").json()
        product_id = products[0]["id"]

        response = self.client.post(
            f"/api/products/{product_id}/price",
            json={"price": 150.0},
        )
        self.assertEqual(response.status_code, 200)
        history = self.client.get(f"/api/products/{product_id}/price-history").json()
        self.assertIsInstance(history, list)
        self.assertGreaterEqual(len(history), 1)


if __name__ == "__main__":
    unittest.main()
