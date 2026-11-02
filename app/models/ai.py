import json
import numpy as np
from datetime import datetime
from app.extensions import db

class AiChunk(db.Model):
    __tablename__ = 'ai_chunk'

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(30), nullable=False, index=True)  # 'doc' | 'product'
    ref_id = db.Column(db.String(120), nullable=False, index=True)  # filename or product_id
    product_id = db.Column(db.Integer, db.ForeignKey('catalog_product.id', ondelete='CASCADE'), nullable=True, index=True)
    chunk_index = db.Column(db.Integer, default=0, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=False)
    embedding_json = db.Column(db.Text, nullable=True)  # JSON-encoded float array
    model = db.Column(db.String(80), default='', nullable=False)
    metadata_json = db.Column(db.Text, default='{}', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    product = db.relationship('Product', backref=db.backref('ai_chunks', cascade='all, delete-orphan', lazy='dynamic'))

    def set_embedding(self, vector):
        if vector is None:
            self.embedding_json = None
            return
        if isinstance(vector, np.ndarray):
            vector = vector.tolist()
        self.embedding_json = json.dumps(vector)

    def get_embedding(self):
        if not self.embedding_json:
            return None
        try:
            arr = np.array(json.loads(self.embedding_json), dtype=np.float32)
            return arr
        except Exception:
            return None

    def get_metadata(self):
        try:
            return json.loads(self.metadata_json or '{}')
        except Exception:
            return {}

    def set_metadata(self, data):
        self.metadata_json = json.dumps(data or {}, ensure_ascii=False)

    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source,
            'ref_id': self.ref_id,
            'product_id': self.product_id,
            'chunk_index': self.chunk_index,
            'title': self.title,
            'text': self.text,
            'model': self.model,
            'metadata': self.get_metadata(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<AiChunk id={self.id} source={self.source} ref={self.ref_id} index={self.chunk_index}>"

