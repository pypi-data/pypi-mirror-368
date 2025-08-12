from rapyuta_io.clients.project import Project, User
from rapyuta_io.utils import InvalidParameterException
from rapyuta_io.utils.object_converter import ObjBase, list_field


class UserGroup(ObjBase):
    """
    Usergroups in Rapyuta IO

    :ivar guid: Group ID
    :vartype guid: str
    :ivar name: Group Name
    :vartype name: str
    :ivar description: Description of the user group
    :vartype description: str
    :ivar creator: Creator's GUID
    :vartype creator: str
    :ivar members: Members who are part of the user group
    :vartype members: list(:py:class:`~rapyuta_io.clients.project.User`)
    :ivar admins: Admins of the user group
    :vartype admins: list(:py:class:`~rapyuta_io.clients.project.User`)
    :ivar projects: Projects that are part of the user group
    :vartype projects: list(:py:class:`~rapyuta_io.clients.project.Project`)
    """

    def __int__(self, guid=None, name=None, description=None,
                creator=None, members=None, admins=None, projects=None):

        self.validate(guid, name, description, creator, members, admins, projects)

        self.guid = guid
        self.name = name
        self.description = description
        self.creator = creator
        self.members = members
        self.admins = admins
        self.projects = projects
        self.role_in_projects = []

    @staticmethod
    def validate(self, guid, name, description, creator, members, admins, projects):
        if not isinstance(name, str) or not len(name):
            raise InvalidParameterException('name must be a non-empty string')

        if members and (not isinstance(members, list) or [m for m in members if not isinstance(m, User)]):
            raise InvalidParameterException('members must be a list of GroupMembers')

        if admins and (not isinstance(admins, list) or [a for a in admins if not isinstance(a, User)]):
            raise InvalidParameterException('members must be a list of GroupMembers')

        if projects and (not isinstance(projects, list) or [p for p in projects if not isinstance(p, Project)]):
            raise InvalidParameterException('members must be a list of GroupMembers')

    def get_serialize_map(self):
        return {
            'guid': 'guid',
            'name': 'name',
            'description': 'description',
            'creator': 'creator',
            'members': 'members',
            'admins': 'admins',
            'projects': 'projects',
            'userGroupRoleInProjects': 'role_in_projects',
        }

    def get_deserialize_map(self):
        return {
            'guid': 'guid',
            'name': 'name',
            'description': 'description',
            'creator': 'creator',
            'members': list_field('members', User),
            'admins': list_field('admins', User),
            'projects': list_field('projects', Project),
            'role_in_projects': 'userGroupRoleInProjects'
        }
