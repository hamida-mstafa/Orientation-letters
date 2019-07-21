from app import app
from  flask_migrate import Migrate, MigrateCommand
from app import db
from flask_script import Manager, Server
# from app.models import User

# app = create_app('development')


manager = Manager(app)
manager.add_command('server',Server)
migrate = Migrate(app,db)
manager.add_command('db',MigrateCommand)

# '''
# adds the databse instance and models to the shell session
# '''
@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
# @manager.shell
# def make_shell_context():
#     return dict(app = app, db = db, User = User, Pitches =Pitches,Comments=Comments )

if __name__ == '__main__':
    manager.run()


# if __name__ == '__main__':
#     app.run(debug=True)
