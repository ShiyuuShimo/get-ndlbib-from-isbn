import requests
import xml.etree.ElementTree as ET
import lxml
import sys
import os
import json


ns = {
	'dc' : 'http://purl.org/dc/elements/1.1/', 
	'dcterms' : 'http://purl.org/dc/terms/', 
	'dcndl' : 'http://ndl.go.jp/dcndl/terms/', 
	'dcmitype' : 'http://purl.org/dc/dcmitype/', 
	'xsi' : 'http://www.w3.org/2001/XMLSchema-instance', 
	'rdf' : 'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 
	'rdfs' : 'http://www.w3.org/2000/01/rdf-schema#', 
	'openSearch' : 'http://a9.com/-/spec/opensearchrss/1.0/'
}


if not os.path.exists('output'):
	os.mkdir('output')


isbn_target = input('enter ISBN. ')
url_api = 'https://ndlsearch.ndl.go.jp/api/opensearch?isbn='

# access NDLsearch via OpenSearch API
result = requests.get(url_api + isbn_target)

# perse xml
root = ET.fromstring(result.text)


# main process: make json and html table
if root.find('.//item', ns) is None:

	print('there is no data about ' + isbn_target)
	sys.exit()

else:

	d = {}
	li = []

	# get title
	tit = root.find('.//item/title', ns).text
	d.update(title=tit)
	elem = '<tr>\n\t<th>' + tit

	# get author name
	if root.find('.//dc:creator', ns) is None:
		auth = ''
		d.update(author=auth)
	elif len(root.findall('.//dc:creator', ns)) == 1:
		auth = root.find('.//dc:creator', ns).text
		d.update(author=auth)
	else:
		auth_row = ''
		for authors in root.findall('.//dc:creator', ns):
			auth_row = auth_row + authors.find('.').text + '<br>'
			li.append(authors.find('.').text)
		auth = auth_row.rstrip('<br>')
		d.update(author=li)
	elem = elem + '</th><th>' + auth

	# get series name
	if root.find('.//dcndl:seriesTitle', ns) is None:
		ser = ''
		d.update(series=ser)
	else:
		ser = root.find('.//dcndl:seriesTitle', ns).text
		d.update(series=ser)
	elem = elem + '</th><th>' + ser

	# get publisher name
	pub = root.find('.//dc:publisher', ns).text
	d.update(publisher=pub)
	elem = elem + '</th><th>' + pub

	# get date issued
	date = root.find('.//dcterms:issued', ns).text
	d.update(date_issued=date)
	elem = elem + '</th><th>' + date

	# get isbn
	d.update(isbn=isbn_target)
	elem = elem + '</th><th>' + isbn_target + '</th>\n</tr>'

	print('achieved to get data!')

# save json
with open('output/test.json', 'w') as j:
	json.dump(d, j, ensure_ascii=False, indent='\t')

# save html table
with open('output/test.html', 'w') as h:
	h.write(elem)
