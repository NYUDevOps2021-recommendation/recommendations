"""
Models for Recommendation

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy
from flask import request

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass


class Recommendations(db.Model):
    """
    Class that represents a <your resource model name>
    """

    app = None

    # Table Schema

    id = db.Column(db.Integer, primary_key=True)
    product_origin = db.Column(db.Integer, nullable=False)
    product_target = db.Column(db.Integer, nullable=False)
    relation = db.Column(db.Integer, nullable=False)  # 1 for cross-sell, 2 for up-sell, 3 for accessory
    dislike = db.Column(db.Integer, nullable=False)   # the counter of the times customers click "dislike"
    is_deleted = db.Column(db.Integer, nullable=False, default = 0)  # 0 is not deleted, 1 is deleted

    def __repr__(self):
        return "<Recommendations %s %s %s id=[%s]>" % (self.product_origin, self.product_target, self.relation, self.id)

    def create(self):
        """
        Creates a Recommendation to the database
        """
        # logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()
    
    def update(self, payload):
        """
        Update a Recommendation to the database
        """
        # logger.info("Creating %s", self.name)
        if "product_origin" in payload:
            self.product_origin = payload["product_origin"]
        if "product_target" in payload:
            self.product_target = payload["product_target"]
        if "relation" in payload:
            self.relation = payload["relation"]
        if "is_deleted" in payload:
            self.is_deleted = payload["is_deleted"] 
        db.session.add(self)
        db.session.commit()

    def save(self):
        """
        Updates a Recommendation to the database
        """
        logger.info("Saving %s %s %s", self.product_origin, self.product_target, self.relation)
        db.session.commit()

    # def delete(self):
    #     """ Removes a Recommendation from the data store """
    #     logger.info("Deleting %s", self.name)
    #     db.session.delete(self)
    #     db.session.commit()

    def serialize(self):
        """ Serializes a Recommendation into a dictionary """
        return {"id": self.id, "product_origin": self.product_origin, "product_target": self.product_target,
                "relation": self.relation, "dislike":self.dislike, "is_deleted": self.is_deleted}

    def deserialize(self, data):
        """
        Deserializes a Recommendation from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.relation = data["relation"]
            self.is_deleted = 0

            if isinstance(data["product_origin"], int):
                self.product_origin = data["product_origin"]
            else:
                raise DataValidationError("Invalid type for int [product_origin]: " + type(data["product_origin"]))

            if isinstance(data["product_target"], int):
                self.product_target = data["product_target"]
            else:
                raise DataValidationError("Invalid type for int [product_target]: " + type(data["product_target"]))

            if isinstance(data["relation"], int):
                self.relation = data["relation"]
            else:
                raise DataValidationError("Invalid type for int [relation]: " + type(data["relation"]))

            if isinstance(data["dislike"], int):
                self.dislike = data["dislike"]
            else:
                raise DataValidationError("Invalid type for int [dislike]: " + type(data["dislike"]))

        except KeyError as error:
            raise DataValidationError(
                "Invalid Recommendation: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid Recommendation: body of request contained bad or no data"
            )
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Recommendation in the database """
        logger.info("Processing all Recommendation")
        return cls.query.all()

    @classmethod
    def find_by_id(cls, by_id):
        """ Finds a Recommendation by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_attributes(cls, origin, target, relation):
        """ Finds a Recommendation by it's ID """
        logger.info("Processing lookup for origin %s target %s relation %s ...", origin, target, relation)
        result = cls.query
        if origin:
            result = result.filter(cls.product_origin == origin)
        if target:
            result = result.filter(cls.product_target == target)
        if relation:
            result = result.filter(cls.relation == relation)
        return result.all()
    
    # @classmethod
    # def find_by_attributes_for_delete(cls, product_id):
    #     """ Finds all YourResourceModels by product_id """
    #     logger.info("Processing lookup for all rows contian %s ...", product_id)
    #     result = cls.query
    #     result1 = result.filter(cls.product_origin == product_id)
    #     result2 = result.filter(cls.product_target == product_id)
    #     return result1.all()+result2.all()

    @classmethod
    def find_or_404(cls, by_id):
        """ Find a Recommendation by it's id """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)

    @classmethod
    def remove_all(cls):
        """ Removes all documents from the database """
        cls.query.delete()
        db.session.commit()
