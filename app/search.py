from app import app

def add_to_index(index, key, doc):
    if not app.elasticsearch:
        return
    app.elasticsearch.index(index=index, doc_type=index, id=key, body=doc)

def remove_from_index(index, key):
    if not app.elasticsearch:
        return
    app.elasticsearch.delete(index=index, doc_type=index, id=key)

def remove_index(index):
    if not app.elasticsearch:
        return
    app.elasticsearch.delete(index=index)

def query_index(index, query, page, per_page):
    if not app.elasticsearch:
        return [], 0
    search = app.elasticsearch.search(
        index=index,
        body={'query': {'multi_match': {'query': query, 'fields': ['*']}},
              'from': (page - 1) * per_page, 'size': per_page})
    ids = [hit['_id'] for hit in search['hits']['hits']]
    return ids, search['hits']['total']