# Elasticsearch fields

    _index: news
    _docs: _doc
    _id: url
    {
        "mappings": {
            "properties": {
            "site": {"type": "text" },
            "text": {"type": "text"  },
            "title": {"type": "text" },  
            "crawled_at": {"type: "date"},
            "published_at": {"type: "date"},
            "category" : {"type: array}
            }
        }
    }