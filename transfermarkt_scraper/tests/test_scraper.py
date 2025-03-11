
import unittest
from value_prediction.api.app import get_player_from_db, predict_value

class TestPlayerValuePrediction(unittest.TestCase):

    def test_get_player_from_db_found(self):
        # Assuming there is a player named 'Lionel Messi' in the database
        player_data = get_player_from_db('Lionel Messi')
        self.assertIsNotNone(player_data)
        self.assertEqual(player_data['name'], 'Lionel Messi')

    def test_get_player_from_db_not_found(self):
        player_data = get_player_from_db('Nonexistent Player')
        self.assertIsNone(player_data)

    def test_predict_value(self):
        player_data = {
            'name': 'Cristiano Ronaldo',
            'market_value': 100000000,
            'currency': 'EUR',
            'last_update': '2023-01-01'
        }
        predicted_value = predict_value(player_data)
        self.assertEqual(predicted_value, 110000000)  # 10% increase

if __name__ == '__main__':
    unittest.main()
