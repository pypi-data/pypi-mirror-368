import unittest
from loutilities.loutilities import tables
from loutilities.tests.models import User, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask, json
from flask.views import MethodView

class TestTablesUtils(unittest.TestCase):
    def test_is_jsonable(self):
        self.assertTrue(tables.is_jsonable({'a': 1, 'b': 2}))
        self.assertTrue(tables.is_jsonable([1, 2, 3]))
        self.assertTrue(tables.is_jsonable('string'))
        self.assertFalse(tables.is_jsonable(set([1, 2, 3])))

    def test_copyopts(self):
        d = {'a': 1, 'b': [2, 3], 'c': {'d': 4}}
        result = tables.copyopts(d)
        self.assertEqual(result, d)
        # Non-serializable value becomes str
        d2 = {'a': set([1, 2])}
        result2 = tables.copyopts(d2)
        self.assertIsInstance(result2['a'], str)

    def test_get_dbattr(self):
        class Dummy:
            class Inner:
                value = 42
            inner = Inner()
        dummy = Dummy()
        self.assertEqual(tables.get_dbattr(dummy, 'inner.value'), 42)

    def test_get_request_action(self):
        form = {'action': 'create'}
        self.assertEqual(tables.get_request_action(form), 'create')
        self.assertIsNone(tables.get_request_action({}))

    def test_get_request_data(self):
        form = {'data[1][name]': 'Alice', 'data[1][age]': '30', 'data[2][name]': 'Bob'}
        data = tables.get_request_data(form)
        self.assertEqual(data['1']['name'], 'Alice')
        self.assertEqual(data['1']['age'], '30')
        self.assertEqual(data['2']['name'], 'Bob')

class TestTablesDbIntegration(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite://', echo=False)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.user = User(name='TestUser')
        self.session.add(self.user)
        self.session.commit()

    def tearDown(self):
        self.session.close()

    def test_get_dbattr_with_sqlalchemy(self):
        user = self.session.query(User).first()
        self.assertEqual(tables.get_dbattr(user, 'name'), 'TestUser')

class DummyCrudApi(tables.CrudApi):
    def open(self):
        raise tables.NotImplementedError
    def nexttablerow(self):
        raise tables.NotImplementedError
    def close(self):
        raise tables.NotImplementedError
    def permission(self):
        raise tables.NotImplementedError
    def createrow(self, formdata):
        raise tables.NotImplementedError
    def refreshrows(self, ids):
        raise tables.NotImplementedError
    def updaterow(self, thisid, formdata):
        raise tables.NotImplementedError
    def deleterow(self, thisid):
        raise tables.NotImplementedError

class TestCrudApiAbstract(unittest.TestCase):
    def setUp(self):
        self.api = DummyCrudApi()
    def test_open_not_implemented(self):
        with self.assertRaises(tables.NotImplementedError):
            self.api.open()
    def test_nexttablerow_not_implemented(self):
        with self.assertRaises(tables.NotImplementedError):
            self.api.nexttablerow()
    def test_close_not_implemented(self):
        with self.assertRaises(tables.NotImplementedError):
            self.api.close()
    def test_permission_not_implemented(self):
        with self.assertRaises(tables.NotImplementedError):
            self.api.permission()
    def test_createrow_not_implemented(self):
        with self.assertRaises(tables.NotImplementedError):
            self.api.createrow({})
    def test_refreshrows_not_implemented(self):
        with self.assertRaises(tables.NotImplementedError):
            self.api.refreshrows('')
    def test_updaterow_not_implemented(self):
        with self.assertRaises(tables.NotImplementedError):
            self.api.updaterow(1, {})
    def test_deleterow_not_implemented(self):
        with self.assertRaises(tables.NotImplementedError):
            self.api.deleterow(1)

# Minimal Flask app and test DbCrudApi subclass
class UserApi(tables.DbCrudApi):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dte = tables.DataTablesEditor(self.dbmapping, self.formmapping)
    def permission(self):
        return True

class TestDbCrudApiIntegration(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        engine = create_engine('sqlite://')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.app.session = self.session
        self.client = self.app.test_client()
        # Setup API
        dbmapping = {'name': 'name'}
        formmapping = {'name': 'name'}
        clientcolumns = [
            {'data': 'name', 'name': 'name', 'label': 'Name', '_unique': True}
        ]
        self.api = UserApi(
            app=self.app,
            endpoint='userapi',
            rule='/users',
            db=self.session,
            model=User,
            dbmapping=dbmapping,
            formmapping=formmapping,
            clientcolumns=clientcolumns,
        )
        self.api.register()

    def tearDown(self):
        self.session.close()

    def test_create_and_get_user(self):
        # Create user
        with self.app.test_request_context():
            resp = self.client.post('/users/rest', data={'action': 'create', 'data[0][name]': 'Alice'})
            self.assertEqual(resp.status_code, 200)
            data = json.loads(resp.data)
            self.assertTrue(any('Alice' in str(v) for v in str(data)))
        # Get users
        with self.app.test_request_context():
            resp = self.client.get('/users/rest')
            self.assertEqual(resp.status_code, 200)
            data = json.loads(resp.data)
            self.assertTrue(any('Alice' in str(v) for v in str(data)))

    def test_unique_validation(self):
        # Create user
        with self.app.test_request_context():
            self.client.post('/users/rest', data={'action': 'create', 'data[0][name]': 'Bob'})
            # Try to create duplicate
            resp = self.client.post('/users/rest', data={'action': 'create', 'data[0][name]': 'Bob'})
            self.assertEqual(resp.status_code, 400)

# Mock user for role permissions
def make_mock_user(has_roles):
    class MockUser:
        def has_role(self, role):
            return role in has_roles
    return MockUser()

class RoleApi(tables.DbCrudApiRolePermissions):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dte = tables.DataTablesEditor(self.dbmapping, self.formmapping)
    @property
    def current_user(self):
        return self._mock_user
    def set_mock_user(self, user):
        self._mock_user = user

class TestDbCrudApiRolePermissions(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        engine = create_engine('sqlite://')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.app.session = self.session
        dbmapping = {'name': 'name'}
        formmapping = {'name': 'name'}
        clientcolumns = [
            {'data': 'name', 'name': 'name', 'label': 'Name'}
        ]
        self.api = RoleApi(
            app=self.app,
            endpoint='roleapi',
            rule='/roles',
            db=self.session,
            model=User,
            dbmapping=dbmapping,
            formmapping=formmapping,
            clientcolumns=clientcolumns,
            roles_accepted=['admin']
        )
        self.api.set_mock_user(make_mock_user(['admin']))

    def tearDown(self):
        self.session.close()

    def test_permission_granted(self):
        self.api.set_mock_user(make_mock_user(['admin']))
        self.assertTrue(self.api.permission())
    def test_permission_denied(self):
        self.api.set_mock_user(make_mock_user(['user']))
        self.assertFalse(self.api.permission())

if __name__ == '__main__':
    unittest.main() 