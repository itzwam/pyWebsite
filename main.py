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
    mycursor.execute("SELECT id, code, description, quantity FROM info where code = '{}'".format(code))
    result = mycursor.fetchall()[0]
    mydb.close()
    return {
      'id' : result[0],
      'code' : result[1],
      'description' : result[2],
      'quantity' : result[3],
    }
  except IndexError:
    return {
      'error': 404,
      'text' : "Le code n'a pas été trouvé dans la base de donnée"
    }
  except Exception as e:
    logging.error(e)
    return {
      'error': 500,
      'text' : "Il y a une erreur dans la base de donnée, merci de reessayer plus tard."
    }

def getallentries():
  try :
    mydb = mysql.connector.connect(
      host=os.environ.get('BARCODE_MYSQL_HOST'),
      user=os.environ.get('BARCODE_MYSQL_USER'),
      passwd=os.environ.get('BARCODE_MYSQL_PASS'),
      database=os.environ.get('BARCODE_MYSQL_DBNAME')
    )
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id, code, description, quantity FROM info")
    result = mycursor.fetchall()
    output = []
    mydb.close()
    for x in result:
      output += [{
      'id' : x[0],
      'code' : x[1],
      'description' : x[2],
      'quantity' : x[3],
    }]
    print(json.dumps(output, indent=2))
    return output
  except IndexError:
    return {
      'error': 404,
      'text' : "Le code n'a pas été trouvé dans la base de donnée"
    }
  except Exception as e:
    logging.error(e)
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
    sql = "INSERT INTO info (code, description) VALUES (%s, %s) ON DUPLICATE KEY UPDATE description=%s"
    val = (code, description, description)
    mycursor.execute(sql, val)
    mydb.commit()
    mydb.close()
  except Exception as e:
    logging.error(e)
    return 1

def updatestock(code, qty):
  try:
    mydb = mysql.connector.connect(
      host=os.environ.get('BARCODE_MYSQL_HOST'),
      user=os.environ.get('BARCODE_MYSQL_USER'),
      passwd=os.environ.get('BARCODE_MYSQL_PASS'),
      database=os.environ.get('BARCODE_MYSQL_DBNAME')
    )
    mycursor = mydb.cursor()
    sql = "UPDATE info SET quantity = quantity + %s WHERE code = %s"
    val = (qty, code)
    mycursor.execute(sql, val)
    mydb.commit()
    mydb.close()
  except Exception as e:
    logging.error(e)
    return 1



def dbsearch_page():
  query = request.args.get('code', None)

  if not query:
    fh = open('./datas/database/searchform.html', 'r')  
    return header + fh.read() + footer

  answer = getallentries()
  error = None
  try:
    error = answer.get('error', None)
  except AttributeError, TypeError:
    pass

  if error:
    errortext=answer.get('text','Unknow error')
    fh = open('./datas/error.html')
    return header + fh.read().format(error=str(error)+" - "+errortext) + footer  

  table = ""
  for x in answer:
    table += "<tr>"
    table += "<th scope='row'>{code}</th>".format(**x)
    table += "<td>{description}</td>".format(**x)
    table += "<td>{quantity}</td>".format(**x)
    table += "</tr>"
  
  fh = open('./datas/database/searchresult.html')
  return header + fh.read().format(entries=table) + footer



def dbadd_page():
  code = request.form.get('code', None)
  description = request.form.get('description', None)

  if (not code) or (not description):
    fh = open('./datas/database/addform.html', 'r')  
    return header + fh.read() + footer

  description = cgi.escape(description)
  addentry(code, description)
  return redirect("/")



def stock_page(remove=False):
  code = request.form.get('code', None)
  try:
    qty = int(request.form.get('qty', 0))
  except ValueError:
    qty = 1

  if not request.form.get('go', None) == '':
    file = "addform.html" if not remove else "remform.html"
    fh = open('./datas/stock/'+ file, 'r')
    return header + fh.read() + footer

  qty = qty if not remove else -qty  # if remove => qty = -qty

  updatestock(code, qty)

  return redirect("/")

def apigetinfos_page():
  query = request.form.get('code', None)

  if not query:  
    return json.dumps({
      'error': 400,
      'text': "Malformed request: missing code"
    })

  answer = getentry(query)
  
  return json.dumps(answer)

app = Flask(__name__)
@app.route('/', defaults={'path': 'index.html'}, methods=['GET','POST'])
@app.route('/<path:path>', methods=['GET','POST'])
def catch_all(path):  
  if path == "index.html":
    fh = open('./datas/index.html', 'r')
    return header + fh.read() + footer
  
  if path == "db/search":
    return dbsearch_page()
  if path == "db/add":
    return dbadd_page()

  if path == "stock/add":
    return stock_page()
  if path == "stock/rem":
    return stock_page(remove=True)

  if path == "api/getinfos":
    return apigetinfos_page()

  try:
    fh = open('./datas/'+path, 'r')
    if path[-5:] == '.html':
      return header + fh.read() + footer
    return fh.read()
  except IOError  :
    fh = open('./datas/error.html', 'r')
    return header + fh.read().format(error="404 - Page not found") + footer



if __name__ == '__main__':
  logging.basicConfig(filename=os.environ.get('BARCODE_HTTP_LOG','/dev/null'),level=logging.INFO)
  app.run(host=os.environ.get('BARCODE_HTTP_HOST',"127.0.0.1"),port=int(os.environ.get('BARCODE_HTTP_PORT',5050)))