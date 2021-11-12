"""Initial migration

Migration ID: a89e14c5883b
Revises: 
Creation Date: 2021-11-12 17:31:11.703421

"""

from emmett.orm import migrations


class Migration(migrations.Migration):
    revision = 'a89e14c5883b'
    revises = None

    def up(self):
        self.create_table(
            'users',
            migrations.Column('id', 'id'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('updated_at', 'datetime'),
            migrations.Column('email', 'string', length=255),
            migrations.Column('password', 'password', length=512),
            migrations.Column('registration_key', 'string', default='', length=512),
            migrations.Column('reset_password_key', 'string', default='', length=512),
            migrations.Column('registration_id', 'string', default='', length=512))
        self.create_table(
            'auth_groups',
            migrations.Column('id', 'id'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('updated_at', 'datetime'),
            migrations.Column('role', 'string', default='', length=255),
            migrations.Column('description', 'text'))
        self.create_table(
            'auth_memberships',
            migrations.Column('id', 'id'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('updated_at', 'datetime'),
            migrations.Column('user', 'reference users', ondelete='CASCADE'),
            migrations.Column('auth_group', 'reference auth_groups', ondelete='CASCADE'))
        self.create_table(
            'auth_permissions',
            migrations.Column('id', 'id'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('updated_at', 'datetime'),
            migrations.Column('name', 'string', default='default', notnull=True, length=512),
            migrations.Column('table_name', 'string', length=512),
            migrations.Column('record_id', 'integer', default=0),
            migrations.Column('auth_group', 'reference auth_groups', ondelete='CASCADE'))
        self.create_table(
            'auth_events',
            migrations.Column('id', 'id'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('updated_at', 'datetime'),
            migrations.Column('client_ip', 'string', length=512),
            migrations.Column('origin', 'string', default='auth', notnull=True, length=512),
            migrations.Column('description', 'text', default='', notnull=True),
            migrations.Column('user', 'reference users', ondelete='CASCADE'))
        self.create_table(
            'identities',
            migrations.Column('id', 'id'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('updated_at', 'datetime'),
            migrations.Column('key', 'string', length=512),
            migrations.Column('user', 'reference users', ondelete='CASCADE'))
        self.create_index('identities_widx__key_uniq', 'identities', ['key'], expressions=[], unique=True)
        self.create_table(
            'states',
            migrations.Column('id', 'id'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('updated_at', 'datetime'),
            migrations.Column('name', 'string', notnull=True, length=512),
            migrations.Column('lock_id', 'string', length=36),
            migrations.Column('locked_at', 'datetime'),
            migrations.Column('lock_owner', 'reference users', ondelete='SET NULL'))
        self.create_index('states_widx__name_uniq', 'states', ['name'], expressions=[], unique=True)
        self.create_table(
            'state_versions',
            migrations.Column('id', 'id'),
            migrations.Column('created_at', 'datetime'),
            migrations.Column('updated_at', 'datetime'),
            migrations.Column('version', 'bigint', default=0, notnull=True),
            migrations.Column('object_store_path', 'string', notnull=True, length=512),
            migrations.Column('state', 'reference states', ondelete='CASCADE'),
            migrations.Column('publisher', 'reference users', ondelete='SET NULL'))
        self.create_index('state_versions_widx__uniq_version', 'state_versions', ['state', 'version'], expressions=[], unique=True)

    def down(self):
        self.drop_index('state_versions_widx__uniq_version', 'state_versions')
        self.drop_table('state_versions')
        self.drop_index('states_widx__name_uniq', 'states')
        self.drop_table('states')
        self.drop_index('identities_widx__key_uniq', 'identities')
        self.drop_table('identities')
        self.drop_table('auth_events')
        self.drop_table('auth_permissions')
        self.drop_table('auth_memberships')
        self.drop_table('auth_groups')
        self.drop_table('users')
