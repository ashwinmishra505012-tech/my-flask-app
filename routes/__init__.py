"""
Routes module for blueprint registration and organization.
"""

from flask import Blueprint

# Create blueprints
public_bp = Blueprint('public', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import route handlers AFTER blueprint definition to avoid circular imports
from . import public, admin
