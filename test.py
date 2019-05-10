from app import app
from app.search import add_to_index, remove_from_index, query_index, remove_index

@app.shell_context_processor
def make_shell_context():
    return {
        'add_to_index': add_to_index,
        'remove_from_index': remove_from_index,
        'query_index': query_index,
        'remove_index': remove_index
    }