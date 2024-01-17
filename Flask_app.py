import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, create_app
from app.models import Usuario, Post

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so':so, 'db': db, 'Usuario': Usuario, 'Post':Post}