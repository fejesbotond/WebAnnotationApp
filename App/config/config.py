from pymongo import MongoClient

mongo_client = MongoClient('mongodb://127.0.0.1:27017/')
db = mongo_client['Onlab']
documents_collection = db['Documents']
annotations_collection = db['Annotations']
relations_collection = db['Relations']
tags_annotations_collection = db['Entity_tags']
tags_relations_collection = db['Relational_tags']