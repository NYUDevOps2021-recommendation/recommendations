"""
Models for YourResourceModel

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
    product_origin = db.Column(db.Integer)
    product_target = db.Column(db.Integer)
    relation = db.Column(db.Integer)  # 1 for cross-sell, 2 for up-sell, 3 for accessory
    is_deleted = db.Column(db.Integer)  # 0 is not deleted, 1 is deleted

    def __repr__(self):
        return "<Recommendations %s %s %s id=[%s]>" % (self.product_origin, self.product_target, self.relation, self.id)

    def create(self):
        """
        Creates a YourResourceModel to the database
        """
        # logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def save(self):
        """
        Updates a YourResourceModel to the database
        """
        logger.info("Saving %s %s %s", self.product_origin, self.product_target, self.relation)
        db.session.commit()

    def delete(self):
        """ Removes a YourResourceModel from the data store """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a YourResourceModel into a dictionary """
        return {"id": self.id, "product_origin": self.product_origin, "product_target": self.product_target,
                "relation": self.relation, "is_deleted": self.is_deleted}

    def deserialize(self, data):
        """
        Deserializes a YourResourceModel from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.product_origin = data["product_origin"]
            self.product_target = data["product_target"]
            self.relation = data["relation"]
            self.is_deleted = 0
        except KeyError as error:
            raise DataValidationError(
                "Invalid YourResourceModel: missing " + error.args[0]
            )
        except TypeError as error:
            raise DataValidationError(
                "Invalid YourResourceModel: body of request contained bad or no data"
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

        # cls.create(Recommendations(product_origin=1, product_target=2, relation=1))
        # cls.create(Recommendations(product_origin=2, product_target=1, relation=1))
        # cls.create(Recommendations(product_origin=1, product_target=3, relation=2))
        # cls.create(Recommendations(product_origin=2, product_target=3, relation=3))

    @classmethod
    def all(cls):
        """ Returns all of the Recommendations in the database """
        logger.info("Processing all Recommendations")
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
    # def find_by_attributes_for_read(cls):
    #     """ Find products by it's origin and relation """
    #     origin = request.args.get('product-id')
    #     relation = request.args.get('relation') 
    #     logger.info("Processing lookup for origin %s relation %s ...", origin, relation)
    #     result = cls.query
    #     if origin:
    #         result = result.filter(cls.product_origin == origin)
    #     if relation:
    #         result = result.filter(cls.relation == relation)
    #     result = result.filter(cls.is_deleted == 0)
    #     return result.all()
    
    @classmethod
    def find_by_attributes_for_delete(cls, product_id):
        """ Finds all YourResourceModels by product_id """
        logger.info("Processing lookup for all rows contain %s ...", product_id)
        result = cls.query
        result1 = result.filter(cls.product_origin == product_id)
        result2 = result.filter(cls.product_target == product_id)
        return result1.all()+result2.all()

    @classmethod
    def find_or_404(cls, by_id):
        """ Find a YourResourceModel by it's id """
        logger.info("Processing lookup or 404 for id %s ...", by_id)
        return cls.query.get_or_404(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all YourResourceModels with the given name

        Args:
            name (string): the name of the YourResourceModels you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
