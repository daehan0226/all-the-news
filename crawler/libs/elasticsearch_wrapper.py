import json
from elasticsearch import Elasticsearch, client
from elasticsearch import helpers

class ElasticsearchWrapper:

    def __init__(self, config):
        if config['is_es_cloud']:
            self.es = Elasticsearch(cloud_id=config['es_cloud_host'], http_auth=(config['username'], config['password']))
        else:
            self.es = Elasticsearch(host=config['es_host'], port=config['es_port'])

        self.indicesClient = client.IndicesClient(self.es)

    def exist_index(self, index):
        return self.indicesClient.exists(index)  # True / False

    def create_index(self, index, mappings):
        return self.indicesClient.create(index=index, ignore=400, body={'mappings' : mappings})

    # update with id
    def update_doc(self, index, doc_type, doc_id, body_dict):
        result = self.es.update(index=index,
                               doc_type=doc_type,
                               id=doc_id,
                               body={
                                   'doc': body_dict,
                                   'doc_as_upsert':True
                               })
        return result['_id']

    def insert_doc(self, index, body):
        result = self.es.index(index, body)
        print(result)

        return result['_id']
    
    def has_url_parsed(self, index, url):
        result = self.es.search(index=index,  body={"query": {"match": { "url": url}}})
        hits = result['hits']['hits']

        if len(hits) == 0:
            return False
        else: 
            return True