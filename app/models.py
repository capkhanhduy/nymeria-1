from config import *
from elasticsearch import Elasticsearch
es = Elasticsearch(host = E_HOST, port = E_PORT)

#Users handle
def m_login(username,password):
    try:
        _username = es.search(index='hackathon', doc_type='users', q='admin')['hits']['hits'][0]['_source']['username']
        _password = es.search(index='hackathon', doc_type='users', q='admin')['hits']['hits'][0]['_source']['password']
        _gid = es.search(index='hackathon', doc_type='users', q='admin')['hits']['hits'][0]['_source']['gid']
    except:
        print 'Some error!'
    if username == _username and password == _password:
        return _gid
    else:
        return 0

def m_add_user(username,password,gid):
    try:
        es.index(index='hackathon', doc_type='users',  body={
            'username': username,
            'password': password,
            'gid' : gid
        })
    except:
        print 'Some error!'

def m_count_users():
    try:
        result = es.search(index='hackathon', doc_type='users')['hits']['total']
    except:
        print 'Some error!'
    return result

#URLs handle
def m_add_site(domain,ip,port):
    try:
        es.index(index='hackathon', doc_type='sites',  body={
        'domain': domain,
        'ip': ip,
        'port': port
    })
        #Add cau hinh

    except:
        print 'Some error!'

def m_list_sites():
    try:
        result = es.search(index='hackathon', doc_type='sites')['hits']['hits']
    except:
        print 'Some error!'
    return result

def m_count_sites():
    try:
        result = es.search(index='hackathon', doc_type='sites')['hits']['total']
    except:
        print 'Some error!'
    return result

#Blacklist
def m_add_blacklist(target):
    try:
        es.index(index='hackathon', doc_type='blacklist',  body={
        'target': target
    })
    except:
        print 'Some error!'

def m_list_blacklist():
    try:
        result = es.search(index='hackathon', doc_type='blacklist')['hits']['hits']
    except:
        print 'Some error!'
    return result

def m_count_blacklist():
    try:
        result = es.search(index='hackathon', doc_type='blacklist')['hits']['total']
    except:
        print 'Some error!'
    return result

#Log antiddos
def m_list_log(site):
    site = str(site).replace('http://','')

    result = es.search(index='log', doc_type='antiddos', body={
  'query': {
    'match': {
      'site': site,
     }
  }
})['hits']['hits']

    return result

def m_count_antiddos_log():
    try:
        result = es.search(index='log', doc_type='antiddos')['hits']['total']
    except:
        print 'Some error!'
    return result

#Log WAF
def m_list_waf_log(site):
    site = str(site).replace('http://','')
    site = site+'_error_log'
    try:
        result = es.search(index='logstash-2016.09.24', doc_type='apacheerror', body={
      'query': {
        'match': {
          'path': site,
         }
      }
    })['hits']['hits']
    except:
        print 'Some error!'

    return result
def m_count_waf_log():
    try:
        result = es.search(index='logstash-2016.09.24', doc_type='apacheerror')['hits']['total']
    except:
        print 'Some error!'
    return result