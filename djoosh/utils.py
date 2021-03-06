# -*- coding: utf-8 -*-
from django.utils.encoding import smart_unicode
from django.conf import settings
from whoosh import index, qparser
import os

def create_index(search_model):
    ixpath = search_model.get_path()
    if not os.path.exists(ixpath):
        os.makedirs(ixpath)
    ix = index.create_in(ixpath, search_model.schema)

def update_index(search_model, obj=None, created=True):
    ixpath = search_model.get_path()
    ix = index.open_dir(ixpath)
    
    if obj:
        objects = [obj]
    else:
        objects = search_model.model.objects.all()
    
    writer = ix.writer()
    
    for obj in objects:
        fields = {}
        for field in search_model.fields:
            try:
                fields[field] = smart_unicode(getattr(obj, field, ''))
            except:
                continue
        if created:
            try:
                writer.update_document(**fields)
            except:
                pass
        else:
            try:
                writer.add_document(**fields)
            except:
                pass
            
    writer.commit()
    ix.close()

def search_index(search_model, query, fields=[], limit=None):
    ix = index.open_dir(search_model.get_path())
    fields = fields or search_model.fields
    hits = []
    query = smart_unicode(query)
    
    limit = limit or getattr(settings, 'DJOOSH_SEARCH_LIMIT', 100)
    
    if query and fields:
        query = query.replace('+', ' AND ').replace('|', ' OR ')
        parser = qparser.MultifieldParser(fields, schema=ix.schema)
        qry = parser.parse(query)
        
        try:
            qry = parser.parse(query)
        except:
            qry = None
        
        if qry:
            searcher = ix.searcher()
            try:
                hits = searcher.search(qry, limit=limit)
            except:
                hits = []
    
    ix.close()
    return hits

def delete(search_model, obj):
    ixpath = search_model.get_path()
    ix = index.open_dir(ixpath)
    
    try:
        ix.delete_by_term(search_model.pk, getattr(obj, search_model.pk))
    except:
        pass
    
    ix.close()
