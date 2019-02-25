import sys
import os
import json
import logging
import itertools
import pymysql
from alphorn import Alphorn

# rds settings
rds_endpoint = os.environ.get('rds_endpoint', 'localhost:3306')
rds_database = os.environ.get('rds_database', 'poc')
rds_username = os.environ.get('rds_username', 'dbo')
rds_password = os.environ.get('rds_password')
rds_host, rds_port = rds_endpoint.split(":")

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info("Try connect to mysql endpoint %s:%s database %s as user %s ..." % (rds_host, rds_port, rds_database, rds_username))
try:
  conn = pymysql.connect(rds_host, user=rds_username, passwd=rds_password, db=rds_database, connect_timeout=5) # , cursorclass=pymysql.cursors.DictCursor
except:
  logger.error("Could not connect to mysql instance!")
  sys.exit()
logger.info("Mysql instance connected")

# stupid scheme initialization, has to be done somehow earlier
logger.info("Init database")
with conn.cursor() as cur:
  cur.execute(
    "CREATE TABLE IF NOT EXISTS application (id INTEGER AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL);")
  cur.execute(
    "CREATE TABLE IF NOT EXISTS cluster (id INTEGER AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL);")
  cur.execute("CREATE TABLE IF NOT EXISTS application_clusters (application_id INTEGER NOT NULL, cluster_id INTEGER NOT NULL, FOREIGN KEY (application_id) REFERENCES application (id) ON DELETE RESTRICT ON UPDATE CASCADE, FOREIGN KEY (cluster_id) REFERENCES cluster (id) ON DELETE RESTRICT ON UPDATE CASCADE, PRIMARY KEY (application_id, cluster_id));")
  conn.commit()
logger.info("Database ready")

def to_list(iterable):
  return list(itertools.chain.from_iterable(iterable)) 

#
# REST API 
#

app = Alphorn()

@app.route('/')
def root():
  return ({
    'message': 'I am the Root!'
  }, 200)

@app.route('/app')
def get_app_list():
  with conn.cursor() as cur:
    sql = "SELECT name FROM application"
    cur.execute(sql)
    result = cur.fetchall()
  return (to_list(result), 200)

@app.route('/app/{app}')
def get_app(app):
  with conn.cursor() as cur:
    sql = "SELECT name FROM application WHERE name = %s"
    cur.execute(sql, app)
    result = cur.fetchone()
  return (result[0], 200) if result != None else ('Not Found', 404) 

@app.route('/app/{app}', methods=['PUT'])
def put_app(app):
  with conn.cursor() as cur:
    sql = "SELECT id FROM application WHERE name = %s"
    cur.execute(sql, app)
    result = cur.fetchone()
    if result != None:
      return ('Conflict', 409) 
    sql = "INSERT INTO application (name) VALUES (%s)"
    cur.execute(sql, app)
    conn.commit()
  return ('Created', 201)

@app.route('/app/{app}', methods=['DELETE'])
def del_app(app):
  with conn.cursor() as cur:
    sql = "SELECT id FROM application WHERE name = %s"
    cur.execute(sql, app)
    result = cur.fetchone()
    if result == None:
      return ('Not Found', 404) 
    sql = "DELETE FROM application WHERE id = %s"
    cur.execute(sql, result[0])
    conn.commit()
  return ('No Content', 204)

@app.route('/app/{app}/cluster')
def get_app_cluster_list(app):
  with conn.cursor() as cur:
    sql = "SELECT id FROM application WHERE name = %s"
    cur.execute(sql, app)
    result = cur.fetchone()
    if result == None:
      return ('Not Found', 404)
    sql = """
      SELECT name 
      FROM cluster 
      JOIN application_clusters 
      ON application_clusters.cluster_id = cluster.id 
      WHERE application_id = %s
    """
    cur.execute(sql, result[0])
    result = cur.fetchall()
  return (to_list(result), 200)  

@app.route('/app/{app}/cluster/{cluster}')
def get_app_cluster(app, cluster):
  with conn.cursor() as cur:
    sql = "SELECT id FROM application WHERE name = %s"
    cur.execute(sql, app)
    result = cur.fetchone()
    if result == None:
      return ('Not Found', 404)
    sql = """
      SELECT name 
      FROM cluster 
      JOIN application_clusters 
      ON application_clusters.cluster_id = cluster.id 
      WHERE application_id = %s and name = %s
    """
    cur.execute(sql, (result[0], cluster))
    result = cur.fetchone()
  return (result[0], 200) if result != None else ('Not Found', 404) 

@app.route('/app/{app}/cluster/{cluster}', methods=['PUT'])
def put_app_cluster(app, cluster):
  with conn.cursor() as cur:
    # app id
    sql = "SELECT id FROM application WHERE name = %s"
    cur.execute(sql, app)
    result = cur.fetchone()
    if result == None:
      return ('Not Found', 404)
    app_id = result[0]
    # cluster id
    sql = "SELECT id FROM cluster WHERE name = %s"
    cur.execute(sql, cluster)
    result = cur.fetchone()
    if result == None:
      return ('Not Found', 404)
    cluster_id = result[0]

    sql = "REPLACE application_clusters (application_id, cluster_id) VALUES (%s, %s)"
    cur.execute(sql, (app_id, cluster_id))
    conn.commit()
  return ('Created', 201)  

@app.route('/app/{app}/cluster/{cluster}', methods=['DELETE'])
def del_app_cluster(app, cluster):
  with conn.cursor() as cur:
    # app id
    sql = "SELECT id FROM application WHERE name = %s"
    cur.execute(sql, app)
    result = cur.fetchone()
    if result == None:
      return ('Not Found', 404)
    app_id = result[0]
    # get cluster id
    sql = "SELECT id FROM cluster WHERE name = %s"
    cur.execute(sql, cluster)
    result = cur.fetchone()
    if result == None:
      return ('Not Found', 404)
    cluster_id = result[0]

    sql = "DELETE FROM application_clusters WHERE application_id = %s AND cluster_id = %s"
    cur.execute(sql, (app_id, cluster_id))
    deleted = cur.rowcount > 0
    conn.commit()
  return ('No Content', 204) if deleted else ('Not Found', 404)

@app.route('/cluster')
def get_cluster_list():
  with conn.cursor() as cur:
    sql = "SELECT name FROM cluster"
    cur.execute(sql)
    result = cur.fetchall()
  return (to_list(result), 200)  

@app.route('/cluster/{cluster}')
def get_cluster(cluster):
  with conn.cursor() as cur:
    sql = "SELECT name FROM cluster WHERE name = %s"
    cur.execute(sql, cluster)
    result = cur.fetchone()
  return (result[0], 200) if result != None else ('Not Found', 404) 

@app.route('/cluster/{cluster}', methods=['PUT'])
def put_cluster(cluster):
  with conn.cursor() as cur:
    sql = "SELECT id FROM cluster WHERE name = %s"
    cur.execute(sql, cluster)
    result = cur.fetchone()
    if result != None:
      return ('Conflict', 409) 
    sql = "INSERT INTO cluster (name) VALUES (%s)"
    cur.execute(sql, cluster)
    conn.commit()
  return ('Created', 201)

@app.route('/cluster/{cluster}', methods=['DELETE'])
def del_cluster(cluster):
  with conn.cursor() as cur:
    sql = "SELECT id FROM cluster WHERE name = %s"
    cur.execute(sql, cluster)
    result = cur.fetchone()
    if result == None:
      return ('Not Found', 404) 
    sql = "DELETE FROM cluster WHERE id = %s"
    cur.execute(sql, result[0])
    conn.commit()
  return ('No Content', 204) 

@app.route('/cluster/{cluster}/app')
def get_cluster_app_list(cluster):
  with conn.cursor() as cur:
    sql = "SELECT id FROM cluster WHERE name = %s"
    cur.execute(sql, cluster)
    result = cur.fetchone()
    if result == None:
      return ('Not Found', 404)
    sql = """
      SELECT name 
      FROM application 
      JOIN application_clusters 
      ON application_clusters.application_id = application.id 
      WHERE cluster_id = %s
    """
    cur.execute(sql, result[0])
    result = cur.fetchall()
  return (to_list(result), 200)  

@app.route('/cluster/{cluster}/app/{app}')
def get_cluster_app(cluster, app):
  with conn.cursor() as cur:
    sql = "SELECT id FROM cluster WHERE name = %s"
    cur.execute(sql, cluster)
    result = cur.fetchone()
    if result == None:
      return ('Not Found', 404)
    sql = """
      SELECT name 
      FROM application 
      JOIN application_clusters 
      ON application_clusters.application_id = application.id 
      WHERE cluster_id = %s and name = %s
    """
    cur.execute(sql, (result[0], app))
    result = cur.fetchone()
  return (result[0], 200) if result != None else ('Not Found', 404) 

@app.route('/cluster/{cluster}/app/{app}', methods=['PUT'])
def put_cluster_app(cluster, app):
  return put_app_cluster(app, cluster)

@app.route('/cluster/{cluster}/app/{app}', methods=['DELETE'])
def del_cluster_app(cluster, app):
  return del_app_cluster(app, cluster)

#
# LAMBDA HANDLER
#
def handler(event, context):
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '/')
    logger.info("Handle: %s %s" % (method, path))
    return app.handle(event)