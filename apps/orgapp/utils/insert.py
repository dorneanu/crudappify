from app.database import db_session as db, Base, engine
from app.models import App, Target, AppType, Organization, Department, Tag, Connection, Header 

def TagInsert(json_data):
	""" Inserts Tag objects into DB """
	result = []
	for r in json_data:
		t = Tag(id=r['id'], name=r['name'], desc=r['desc'])

		print("[-] tag: Insert %s ..." % r)
		db.merge(t)
		result.append(t)

	db.commit()
	return result

def ConnectionInsert(json_data):
	""" Inserts Connection objects into DB """
	result = []
	for r in json_data:
		tags = TagInsert(r['tags'])
		conn = Connection(
			id=int(r['id']), conn_type=r['conn_type'], url=r['url'], ip=r['ip'],
			answer=r['answer'], redirect=r['redirect'], port=r['port'], tags=tags
		)

		print("[-] connection: Insert %s ..." % r)
		db.merge(conn)
		result.append(conn)

	db.commit()
	return result

def HeaderInsert(json_data):
	""" Insert Header objects into DB """
	result = []
	for r in json_data:
		conn = ConnectionInsert([r['conn']])[0]		# one-to-many relationship
		header = Header(id=int(r['id']), conn=conn, header=r['header'], value=r['value'])

		print("[-] header: Insert %s ..." % r)
		db.merge(header)
		result.append(header)

	db.commit()
	return result

def OrganizationInsert(json_data):
	""" Insert Organization objects into DB """
	result = []
	for r in json_data:
		org = Organization(id=int(r['id']), desc=r['desc'])

		print("[-] organization: Insert %s ..." % r)
		db.merge(org)
		result.append(org)

	db.commit()
	return result

def DepartmentInsert(json_data):
	""" Insert Department objects into DB """
	result = []
	for r in json_data:
		org = OrganizationInsert([r['org']])[0]			# one-to-many relationship
		dpt = Department(id=int(r['id']), org=org, desc=r['desc'], contact=r['contact'])

		print("[-] department: Insert %s ..." % r)
		db.merge(dpt)
		result.append(dpt)

	db.commit()
	return result

def AppTypeInsert(json_data):
	""" Insert AppType objects into DB """
	result = []
	for r in json_data:
		apptype = AppType(id=int(r['id']), desc=r['desc'])

		print("[-] apptype: Insert %s ..." % r)
		db.merge(apptype)
		result.append(apptype)

	db.commit()
	return result

def AppInsert(json_data):
	""" Insert App objects into DB """
	result = []
	for r in json_data:
		apptype = AppTypeInsert([r['app_type']])		# one-to-many relationship
		dpt = DepartmentInsert([r['department']])[0]	# one-to-many relationship
		tags = TagInsert(r['tags'])

		app = App(
			app_id=int(r['app_id']), app_type=apptype[0], url=r['url'],
			desc=r['desc'], date_added=r['date_added'], department=dpt,
			version=r['version'], environment=r['environment'], platform=r['platform'],
			tags=tags
		)

		print("[-] application: Insert %s ..." % r)
		db.merge(app)
		result.append(app)

	db.commit()
	return result

def TargetInsert(json_data):
	""" Insert Target objects into DB """
	result = []
	for r in json_data:
		tags = TagInsert(r['tags'])
		target = Target(
			scheme = r['scheme'],
			user = r['user'],
			password = r['password'],
			netloc = r['netloc'],
			port = r['port'],
			path = r['path'],
			params = r['params'],
			query = r['query'],
			fragment = r['fragment'],
			comments = r['comments'],
			tags = tags
		)

		print("[-] target: Insert %s ..." % r)
		db.merge(target)
		result.append(target)

	db.commit()
	return result


