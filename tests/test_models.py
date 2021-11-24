"""
Test cases for YourResourceModel Model

"""
import logging
import unittest
import os
from werkzeug.exceptions import NotFound
from service.models import Recommendations, DataValidationError, db
from service import app


######################################################################
#  <your resource name>   M O D E L   T E S T   C A S E S
######################################################################
class TestRecommendations(unittest.TestCase):
    """ Test Cases for Recommendation Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.logger.setLevel(logging.CRITICAL)
        Recommendations.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def setUp(self):
        """ This runs before each test """
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_recommendation(self):
        """ Create a recommendation and assert that it exists """
        recommendation = Recommendations(product_origin=1, product_target=2, relation=1, is_deleted=0)
        self.assertTrue(recommendation != None)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(recommendation.product_origin, 1)
        self.assertEqual(recommendation.product_target, 2)
        self.assertEqual(recommendation.relation, 1)
        self.assertEqual(recommendation.is_deleted, 0)
        recommendation = Recommendations(product_origin=1, product_target=3, relation=1, is_deleted=0)
        self.assertEqual(recommendation.product_target, 3)

    def test_add_a_recommendation(self):
        """ Create a recommendation and add it to the database """
        recommendations = Recommendations.all()
        self.assertEqual(recommendations, [])
        recommendation = Recommendations(product_origin=1, product_target=2, relation=1, dislike=0, is_deleted=0)
        self.assertTrue(recommendation != None)
        self.assertEqual(recommendation.id, None)
        recommendation.create()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(recommendation.id, 1)
        recommendations = recommendation.all()
        self.assertEqual(len(recommendations), 1)

    def test_update_a_recommendation(self):
        """ Update a Recommendation """
        recommendation = Recommendations(product_origin=1, product_target=2, relation=1, dislike=0, is_deleted=0)
        logging.debug(recommendation)
        recommendation.create()
        logging.debug(recommendation)
        self.assertEqual(recommendation.id, 1)
        # Change it an update it
        recommendation.relation = 2
        original_id = recommendation.id
        payload = {'product_origin': 1, 'product_target': 2, 'relation': 2, 'dislike': 0, 'is_deleted': 0}
        recommendation.update(payload)
        self.assertEqual(recommendation.id, original_id)
        self.assertEqual(recommendation.relation, 2)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        recommendations = Recommendations.all()
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].id, 1)
        self.assertEqual(recommendations[0].relation, 2)

    def test_find_by_id(self):
        """ Find a Recommendation by ID """
        recommendation1 = Recommendations(product_origin=1, product_target=2, relation=1, dislike=0, is_deleted=0)
        recommendation1.create()
        recommendation2 = Recommendations(product_origin=1, product_target=3, relation=1, dislike=0, is_deleted=0)
        recommendation2.create()
        recommendation3 = Recommendations(product_origin=1, product_target=4, relation=1, dislike=0, is_deleted=0)
        recommendation3.create()
        recommendations = [recommendation1, recommendation2, recommendation3]
        logging.debug(recommendations)
        # make sure they got updated
        self.assertEqual(len(Recommendations.all()), 3)
        # find the 2nd pet in the list
        recommendation = Recommendations.find_by_id(recommendations[1].id)
        self.assertIsNot(recommendation, None)
        self.assertEqual(recommendation.id, recommendations[1].id)
        self.assertEqual(recommendation.product_origin, recommendations[1].product_origin)
        self.assertEqual(recommendation.product_target, recommendations[1].product_target)
        self.assertEqual(recommendation.relation, recommendations[1].relation)
        self.assertEqual(recommendation.dislike, recommendations[1].dislike)
        self.assertEqual(recommendation.is_deleted, recommendations[1].is_deleted)

    def test_find_by_attribute(self):
        """ Find a Recommendation by Attributes """
        recommendation1 = Recommendations(product_origin=1, product_target=2, relation=1, dislike=0, is_deleted=0)
        recommendation1.create()
        recommendation2 = Recommendations(product_origin=1, product_target=3, relation=1, dislike=0, is_deleted=0)
        recommendation2.create()
        recommendation3 = Recommendations(product_origin=1, product_target=4, relation=1, dislike=0, is_deleted=0)
        recommendation3.create()
        recommendations = Recommendations.find_by_attributes(origin=1, target=2, relation=1)
        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0].product_origin, recommendation1.product_origin)
        self.assertEqual(recommendations[0].product_target, recommendation1.product_target)
        self.assertEqual(recommendations[0].relation, recommendation1.relation)
        self.assertEqual(recommendations[0].dislike, recommendation1.dislike)
        self.assertEqual(recommendations[0].is_deleted, recommendation1.is_deleted)

    def test_serialize_a_recommendation(self):
        """ Test serialization of a Recommendation """
        recommendation = Recommendations(product_origin=1, product_target=2, relation=1, is_deleted=0)
        data = recommendation.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], recommendation.id)
        self.assertIn("product_origin", data)
        self.assertEqual(data["product_origin"], recommendation.product_origin)
        self.assertIn("product_target", data)
        self.assertEqual(data["product_target"], recommendation.product_target)
        self.assertIn("relation", data)
        self.assertEqual(data["relation"], recommendation.relation)
        self.assertIn("is_deleted", data)
        self.assertEqual(data["is_deleted"], recommendation.is_deleted)

    def test_deserialize_a_recommendation(self):
        """ Test deserialization of a Recommendation """
        data = {
            "product_origin": 1,
            "product_target": 2,
            "dislike": 0,
            "relation": 1,
        }
        recommendation = Recommendations()
        recommendation.deserialize(data)
        self.assertNotEqual(recommendation, None)
        self.assertEqual(recommendation.id, None)
        self.assertEqual(recommendation.product_origin, 1)
        self.assertEqual(recommendation.product_target, 2)
        self.assertEqual(recommendation.relation, 1)
        self.assertEqual(recommendation.dislike, 0)
        self.assertEqual(recommendation.is_deleted, 0)

    def test_deserialize_missing_data(self):
        """ Test deserialization of a Recommendation with missing data """
        data = {"id": 1, "product_origin": 1, "product_target": 2}
        recommendation = Recommendations()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        recommendation = Recommendations()
        self.assertRaises(DataValidationError, recommendation.deserialize, data)

    def test_find_or_404_found(self):
        """ Find or return 404 found """
        test_recommendation = Recommendations(product_origin=1, product_target=2, relation=1, dislike=0, is_deleted=0)
        test_recommendation.create()

        recommendation = Recommendations.find_or_404(test_recommendation.id)
        self.assertIsNot(recommendation, None)
        self.assertEqual(recommendation.id, test_recommendation.id)
        self.assertEqual(recommendation.product_origin, test_recommendation.product_origin)
        self.assertEqual(recommendation.product_target, test_recommendation.product_target)
        self.assertEqual(recommendation.relation, test_recommendation.relation)
        self.assertEqual(recommendation.dislike, test_recommendation.dislike)
        self.assertEqual(recommendation.is_deleted, test_recommendation.is_deleted)

    def test_find_or_404_not_found(self):
        """ Find or return 404 NOT found """
        self.assertRaises(NotFound, Recommendations.find_or_404, 0)
