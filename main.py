#!/usr/bin/python
# encoding=utf8  
import sys
import os
from flask import Flask, abort, request, Response, redirect, jsonify
import mysql.connector # pylint: disable=F0401
import cgi
import logging
import requests
import json

header = open('./datas/header.html','r').read()
footer = open('./datas/footer.html','r').read()

reload(sys)
sys.setdefaultencoding('utf8')

def getentry(code):
  try :
    mydb = mysql.connector.connect(
      host=os.environ.get('BARCODE_MYSQL_HOST'),
      user=os.environ.get('BARCODE_MYSQL_USER'),
      passwd=os.environ.get('BARCODE_MYSQL_PASS'),
      database=os.environ.get('BARCODE_MYSQL_DBNAME')
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id, code, description FROM info where code = '{}'".format(code))
    result = mycursor.fetchall()[0]
    mydb.close()
    return {
      'id' : result[0],
      'code' : result[1],
      'description' : result[2],
    }
  except IndexError:
    return {
      'error': 404,
      'text' : "Le code n'a pas été trouvé dans la base de donnée"
    }
  except Exception as e:
    print(e)
    return {
      'error': 500,
      'text' : "Il y a une erreur dans la base de donnée, merci de reessayer plus tard."
    }



def addentry(code, description):
  try:
    mydb = mysql.connector.connect(
      host=os.environ.get('BARCODE_MYSQL_HOST'),
      user=os.environ.get('BARCODE_MYSQL_USER'),
      passwd=os.environ.get('BARCODE_MYSQL_PASS'),
      database=os.environ.get('BARCODE_MYSQL_DBNAME')
    )
    mycursor = mydb.cursor()
    sql = "INSERT INTO info (code, description) VALUES (%s, %s)"
    val = (code, description)
    mycursor.execute(sql, val)
    mydb.commit()
    mydb.close()
  except Exception as e:
    print(e)
    return 1
  print(mycursor.rowcount, "record inserted.")



def dbsearch_page():
  query = request.args.get('code', None)

  if not query:
    fh = open('./datas/database/searchform.html', 'r')  
    return header + fh.read() + footer

  answer = getentry(query)
  error = answer.get('error',False)
  
  if error:
    errortext=answer.get('text','Unknow error')
    fh = open('./datas/database/searchresult.err.html')
    return header + fh.read().format(error=errortext) + footer
  
  fh = open('./datas/database/searchresult.html')
  return header + fh.read().format(**answer) + footer



def dbadd_page():
  code = request.form.get('code', None)
  description = request.form.get('description', None)

  print("code : {} | desc : {}".format(code, description))
  if (not code) or (not description):
    fh = open('./datas/database/addform.html', 'r')  
    return header + fh.read() + footer

  description = cgi.escape(description)
  print('adding code and description to database')
  print('code : {} | desc : {}'.format(code, description))
  addentry(code, description)
  return redirect("/")



def stockadd_page():
  code = request.form.get('code', None)
  qty = request.form.get('quantity', None)

  print("code : {} | qty : {}".format(code, qty))
  if (not code) or (not qty):
    fh = open('./datas/stock/addform.html', 'r')  
    return header + fh.read() + footer

  description = cgi.escape(description)
  print('adding {qty} items to stock')
  print('code : {} | qty : {}'.format(code, qty))
  
  return redirect("/")

def apigetinfos_page():
  query = request.form.get('code', None)

  if not query:  
    return jsonify(
      error=400,
      text="Malformed request: missing code"
    )

  answer = getentry(query)
  
  return json.dumps(answer)

app = Flask(__name__)
@app.route('/', defaults={'path': 'index.html'}, methods=['GET','POST'])
@app.route('/<path:path>', methods=['GET','POST'])
def catch_all(path):  
  if path == "index.html":
    catapi = requests.get("https://api.thecatapi.com/v1/images/search").json()[0]
    fh = open('./datas/index.html', 'r')
    return header + fh.read().format(**catapi) + footer
  
  if path == "db/search":
    return dbsearch_page()
  if path == "db/add":
    return dbadd_page()

  if path == "stock/add":
    return stockadd_page()

  if path == "api/getinfos":
    return apigetinfos_page()

  try:
    fh = open('./datas/'+path, 'r')
    if path[-5:] == '.html':
      return header + fh.read() + footer
    return fh.read()
  except IOError  :
    fh = open('./datas/404.html', 'r')
    return header + fh.read() + footer



if __name__ == '__main__':
  logging.basicConfig(filename=os.environ.get('BARCODE_HTTP_LOG','/dev/null'),level=logging.INFO)
  app.run(host=os.environ.get('BARCODE_HTTP_HOST',"127.0.0.1"),port=int(os.environ.get('BARCODE_HTTP_PORT',5050)))