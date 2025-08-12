from rapyuta_io.clients.project import Project, User
from rapyuta_io.clients.user_group import UserGroup
from rapyuta_io.utils.utils import prepend_bearer_to_auth_token, create_auth_header, get_api_response_data
from rapyuta_io.utils.rest_client import HttpMethod
from rapyuta_io.utils import RestClient
from rapyuta_io.utils.settings import METRICS_API_QUERY_PATH, LIST_METRICS_API_QUERY_PATH, \
    LIST_TAGS_KEY_API_QUERY_PATH, LIST_TAGS_VALUE_API_QUERY_PATH, GET_USER_PATH


class CoreAPIClient:
    def __init__(self, auth_token, project, core_api_host):
        self._core_api_host = core_api_host
        self._auth_token = prepend_bearer_to_auth_token(auth_token)
        self._project = project

    def set_project(self, project):
        self._project = project

    def _add_header_fields(self, obj):
        setattr(obj, '_core_api_host', self._core_api_host)
        setattr(obj, '_auth_token', self._auth_token)
        if type(obj) is not Project:
            setattr(obj, '_project', self._project)

    def _add_auth_token_to_routes(self, routes):
        for route in routes:
            self._add_header_fields(route)

    def query_metrics(self, metrics_query):
        url = self._core_api_host + METRICS_API_QUERY_PATH
        headers = create_auth_header(self._auth_token, self._project)
        payload = metrics_query.serialize()
        response = RestClient(url).method(HttpMethod.POST).headers(headers).execute(payload)
        return get_api_response_data(response, parse_full=False)

    def list_metrics(self, list_metrics_query):
        url = self._core_api_host + LIST_METRICS_API_QUERY_PATH.format(list_metrics_query.entity,
                                                                       list_metrics_query.entity_id)
        headers = create_auth_header(self._auth_token, self._project)
        params = {
            'start_date': list_metrics_query.start_date.isoformat(),
            'end_date': list_metrics_query.end_date.isoformat()
        }
        response = RestClient(url).method(HttpMethod.GET).query_param(params).headers(headers).execute()
        return get_api_response_data(response, parse_full=False)

    def list_tag_keys(self, list_tag_keys_query):
        url = self._core_api_host + LIST_TAGS_KEY_API_QUERY_PATH.format(list_tag_keys_query.entity,
                                                                        list_tag_keys_query.entity_id)
        headers = create_auth_header(self._auth_token, self._project)
        params = {
            'start_date': list_tag_keys_query.start_date.isoformat(),
            'end_date': list_tag_keys_query.end_date.isoformat()
        }
        response = RestClient(url).method(HttpMethod.GET).query_param(params).headers(headers).execute()
        return get_api_response_data(response, parse_full=False)

    def list_tag_values(self, list_tag_values_query):
        url = self._core_api_host + LIST_TAGS_VALUE_API_QUERY_PATH.format(list_tag_values_query.entity,
                                                                          list_tag_values_query.entity_id,
                                                                          list_tag_values_query.tag)
        headers = create_auth_header(self._auth_token, self._project)
        params = {
            'start_date': list_tag_values_query.start_date.isoformat(),
            'end_date': list_tag_values_query.end_date.isoformat()
        }
        response = RestClient(url).method(HttpMethod.GET).query_param(params).headers(headers).execute()
        return get_api_response_data(response, parse_full=False)

    def get_user(self):
        url = self._core_api_host + GET_USER_PATH
        headers = create_auth_header(self._auth_token, self._project)
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()
        data = get_api_response_data(response, parse_full=True)
        return User.deserialize(data)

    def get_user_organizations(self):
        url = self._core_api_host + GET_USER_PATH
        headers = create_auth_header(self._auth_token, self._project)
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()
        data = get_api_response_data(response, parse_full=True)
        user = User.deserialize(data)
        return user.organizations

    def list_usergroups(self, org_guid):
        url = '{}/api/group/list'.format(self._core_api_host)
        headers = create_auth_header(self._auth_token, self._project)
        headers['organization'] = org_guid
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()
        data = get_api_response_data(response, parse_full=True)
        usergroups = []
        for usergroup_data in data:
            usergroup = UserGroup.deserialize(usergroup_data)
            self._add_header_fields(usergroup)
            usergroups.append(usergroup)

        return usergroups

    def get_usergroup(self, org_guid, group_guid):
        url = '{}/api/group/{}/get'.format(self._core_api_host, group_guid)
        headers = create_auth_header(self._auth_token, self._project)
        headers['organization'] = org_guid
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()
        data = get_api_response_data(response, parse_full=True)
        usergroup = UserGroup.deserialize(data)
        self._add_header_fields(usergroup)
        return usergroup

    def delete_usergroup(self, org_guid, group_guid):
        url = '{}/api/group/delete'.format(self._core_api_host)
        headers = create_auth_header(self._auth_token, self._project)
        headers['organization'] = org_guid
        payload = {'guid': group_guid}
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute(payload)
        return get_api_response_data(response, parse_full=True)

    def create_usergroup(self, org_guid, usergroup_payload):
        url = '{}/api/group/create'.format(self._core_api_host)
        headers = create_auth_header(self._auth_token, self._project)
        headers['organization'] = org_guid
        response = RestClient(url).method(HttpMethod.POST).headers(headers).execute(usergroup_payload)
        data = get_api_response_data(response, parse_full=True)
        usergroup = UserGroup.deserialize(data)
        self._add_header_fields(usergroup)
        return usergroup

    def update_usergroup(self, org_guid, group_guid, usergroup_payload):
        url = '{}/api/group/{}/update'.format(self._core_api_host, group_guid)
        headers = create_auth_header(self._auth_token, self._project)
        headers['organization'] = org_guid
        response = RestClient(url).method(HttpMethod.PUT).headers(headers).execute(usergroup_payload)
        data = get_api_response_data(response, parse_full=True)
        usergroup = UserGroup.deserialize(data)
        self._add_header_fields(usergroup)
        return usergroup
