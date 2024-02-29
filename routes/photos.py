from flask import Blueprint, request, jsonify
from config.db_config import db
from models import PhotosModel, ProductsModel
import base64

photos_bp = Blueprint('photos_bp', __name__)

# Agregar una foto individual
@photos_bp.route('/photos', methods=['POST'])
def add_photo():
    data = request.json
    try:
        new_photo = PhotosModel.from_json(data)
        db.session.add(new_photo)
        db.session.commit()
        return jsonify({'message': 'Photo added successfully', 'uuid': new_photo.uuid}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error adding photo: {str(e)}'}), 500
    

# Obtener todas las fotos de un producto específico
@photos_bp.route('/photos/product/<uuid_product>', methods=['GET'])
def get_photos_by_product(uuid_product):
    photos = PhotosModel.query.filter_by(uuid_product=uuid_product).all()
    if photos:
        return jsonify([photo.to_json() for photo in photos]), 200
    else:
        return jsonify({'message': 'No photos found for this product'}), 404

# Agregar un lote de fotos
@photos_bp.route('/photos/batch', methods=['POST'])
def add_photos_batch():
    data = request.json
    uuid_product = data.get('uuid_product')
    photos = data.get('photos', [])
    
    if not uuid_product or not ProductsModel.query.filter_by(uuid=uuid_product).first():
        return jsonify({'message': 'Invalid or missing uuid_product'}), 400

    if not photos:
        return jsonify({'message': 'No photos provided'}), 400

    for photo_blob in photos:
        photo_decoded = base64.b64decode(photo_blob)
        new_photo = PhotosModel(uuid_product=uuid_product, blob=photo_decoded)
        db.session.add(new_photo)

    db.session.commit()
    return jsonify({'message': 'Photos batch added successfully'}), 201

# Eliminar una foto (borrado físico)
@photos_bp.route('/photos/<uuid>', methods=['DELETE'])
def delete_photo(uuid):
    photo = PhotosModel.query.filter_by(uuid=uuid).first()
    if photo:
        db.session.delete(photo)
        db.session.commit()
        return jsonify({'message': 'Photo deleted successfully'}), 200
    else:
        return jsonify({'message': 'Photo not found'}), 404
