from elasticsearch import Elasticsearch
from elasticsearch import helpers

class ElasticsearchWrapper:

    def __init__(self, config):
        self.es = Elasticsearch(cloud_id=config['cloud_id'], http_auth=(config['username'], config['password']))

    def insert_doc(self, index, doc_type, doc_id, body_dict):
        result = self.es.update(index=index,
                               doc_type=doc_type,
                               id=doc_id,
                               body={
                                   'doc': body_dict,
                                   'doc_as_upsert':True
                               })
        return result['_id']
