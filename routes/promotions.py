from datetime import datetime
from flask import Blueprint, request, jsonify, abort
from config.db_config import db
from models import PromotionsModel, ProductsModel, PromotionProductModel

promotions_bp = Blueprint('promotions_bp', __name__)

@promotions_bp.route('/promotions', methods=['POST'])
def create_promotion():
    data = request.json
    try:
        new_promotion = PromotionsModel.from_json(data)
        db.session.add(new_promotion)
        db.session.commit()
        return jsonify({'message': 'Promotion created successfully', 'uuid': new_promotion.uuid}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error creating promotion: {}'.format(str(e))}), 500

@promotions_bp.route('/promotions', methods=['GET'])
def get_all_promotions():
    promotions = PromotionsModel.query.filter(PromotionsModel.deleted_at == None).all()
    promotions_data = [promotion.to_json() for promotion in promotions]
    return jsonify(promotions_data), 200

@promotions_bp.route('/promotions/<uuid>', methods=['GET'])
def get_promotion(uuid):
    promotion = PromotionsModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if promotion:
        return jsonify(promotion.to_json()), 200
    return jsonify({'message': 'Promotion not found'}), 404

@promotions_bp.route('/promotions/<uuid>', methods=['PUT'])
def update_promotion(uuid):
    promotion = PromotionsModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if promotion:
        data = request.json
        try:
            # Actualizar campos permitidos
            if 'name' in data:
                promotion.name = data['name']
            if 'description' in data:
                promotion.description = data['description']
            try:
                if 'start_date' in data:
                    promotion.start_date = datetime.fromisoformat(data['start_date'])
                if 'end_date' in data:
                    promotion.end_date = datetime.fromisoformat(data['end_date'])
                    
                if promotion.start_date >= promotion.end_date:
                    abort(400, description="The 'start_date' must be before the 'end_date'.")
            except ValueError:
                abort(400, description="Invalid date format. Please use ISO format for 'start_date' and 'end_date'.")
            db.session.commit()
            return jsonify({'message': 'Promotion updated successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Error updating promotion: {}'.format(str(e))}), 500
    return jsonify({'message': 'Promotion not found'}), 404

@promotions_bp.route('/promotions/<uuid>', methods=['DELETE'])
def delete_promotion(uuid):
    promotion = PromotionsModel.query.filter_by(uuid=uuid, deleted_at=None).first()
    if promotion:
        promotion.deleted_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Promotion deleted successfully'}), 200
    return jsonify({'message': 'Promotion not found'}), 404

@promotions_bp.route('/promotions/<promotion_uuid>/add-product', methods=['POST'])
def add_product_to_promotion(promotion_uuid):
    data = request.json
    product_uuid = data.get('product_uuid')
    discount_rate = data.get('discount_rate')

    # Verificar la existencia de la promoción y del producto
    promotion = PromotionsModel.query.filter_by(uuid=promotion_uuid).first()
    product = ProductsModel.query.filter_by(uuid=product_uuid).first()
    if not promotion or not product:
        return jsonify({'message': 'Promotion or product not found'}), 404

    try:
        # Crear y añadir la nueva asociación entre producto y promoción
        new_promotion_product = PromotionProductModel(
            promotion_uuid=promotion_uuid,
            product_uuid=product_uuid,
            discount_rate=discount_rate
        )
        db.session.add(new_promotion_product)
        db.session.commit()
        return jsonify({'message': 'Product added to promotion successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error adding product to promotion: {str(e)}'}), 500

@promotions_bp.route('/promotions/<promotion_uuid>/remove-product/<product_uuid>', methods=['DELETE'])
def remove_product_from_promotion(promotion_uuid, product_uuid):
    try:
        # Encontrar y eliminar la asociación específica entre producto y promoción
        promotion_product = PromotionProductModel.query.filter_by(
            promotion_uuid=promotion_uuid,
            product_uuid=product_uuid
        ).first()
        if promotion_product:
            db.session.delete(promotion_product)
            db.session.commit()
            return jsonify({'message': 'Product removed from promotion successfully'}), 200
        else:
            return jsonify({'message': 'Association between promotion and product not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error removing product from promotion: {str(e)}'}), 500