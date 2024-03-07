from flask import Blueprint, request, jsonify, abort
from config.db_config import db
from models import ReviewsModel
from datetime import datetime

reviews_bp = Blueprint('reviews_bp', __name__)

@reviews_bp.route('/reviews', methods=['POST'])
def create_review():
    data = request.json
    try:
        new_review = ReviewsModel.from_json(data)
        db.session.add(new_review)
        db.session.commit()
        return jsonify({'message': 'Review created successfully', 'uuid': new_review.uuid}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating review: {}'.format(str(e))}), 500

@reviews_bp.route('/reviews', methods=['GET'])
def get_all_reviews():
    reviews = ReviewsModel.query.filter(ReviewsModel.deleted_at == None).all()
    reviews_data = [review.to_json() for review in reviews]
    return jsonify(reviews_data), 200

@reviews_bp.route('/reviews/<uuid>', methods=['GET'])
def get_review(uuid):
    review = ReviewsModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if review:
        return jsonify(review.to_json()), 200
    return jsonify({'message': 'Review not found'}), 404

@reviews_bp.route('/reviews/<uuid>', methods=['PUT'])
def update_review(uuid):
    review = ReviewsModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if review:
        data = request.json
        try:
            if 'rating' in data:
                review.rating = data['rating']
                if review.rating > 10 or review.rating < 1:
                    abort(400, description="The 'rating' must be an integer between 1 and 10.")
            if 'description' in data:
                review.description = data['description']
            db.session.commit()
            return jsonify({'message': 'Review updated successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Error updating review: {}'.format(str(e))}), 500
    return jsonify({'message': 'Review not found'}), 404

@reviews_bp.route('/reviews/<uuid>', methods=['DELETE'])
def delete_review(uuid):
    review = ReviewsModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if review:
        review.deleted_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Review deleted successfully'}), 200
    return jsonify({'message': 'Review not found'}), 404
