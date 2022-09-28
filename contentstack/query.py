"""
Contentstack provides certain queries that you can use to fetch filtered results
"""

import enum
import json
import logging
from urllib import parse

import deprecation
import empty

from contentstack.basequery import BaseQuery
from contentstack.entryqueryable import EntryQueryable

# ************* Module query.py **************
# Your code has been rated at 10.00/10  by pylint

log = logging.getLogger(__name__)


class QueryType(enum.Enum):
    """
    Get entries that satisfy all the conditions provided by enum(AND, OR)
    enum ([AND, OR]): Get entries that satisfy all the conditions provided by enum
    AND: Get entries that satisfy all the conditions provided in the '$and' query
    OR: Get entries that satisfy all the conditions provided in the '$or' query
    """
    AND = "$and"
    OR = '$or'


class Query(BaseQuery, EntryQueryable):
    """
    Contentstack provides certain queries that you can use to fetch filtered results.
    You can use queries for Entries API requests.
    [API Reference]:https://www.contentstack.com/docs/developers/apis/content-delivery-api/#queries]

    ---------------------------------------
    Example:
            >>> import contentstack
            >>> stack = contentstack.Stack('api_key', 'delivery_token', 'environment')
            >>> query = stack.content_type('content_type_uid').query()
            >>> result = query.locale('locale-code').excepts('field_uid').limit(4).skip(5).find()
    """

    def __init__(self, http_instance, content_type_uid):
        super().__init__()
        EntryQueryable.__init__(self)
        self.content_type_uid = content_type_uid
        self.http_instance = http_instance
        if self.content_type_uid is None:
            raise PermissionError(
                'You are not allowed here without content_type_uid')
        self.base_url = f'{self.http_instance.endpoint}/content_types/{self.content_type_uid}/entries'
        self.base_url = self.__get_base_url()

    def __get_base_url(self, endpoint=''):
        if endpoint is not None and not empty:
            self.http_instance.endpoint = endpoint
        if None in (self.http_instance, self.content_type_uid):
            raise KeyError(
                'Provide valid http_instance, content_type_uid or entry_uid')
        url = f'{self.http_instance.endpoint}/content_types/{self.content_type_uid}/entries'

        return url

    def query_operator(self, query_type: QueryType, *query_objects):
        """
        Get entries that satisfy all the conditions provided in the '$and' query.
        Arguments:
            query_objects {Query} -- query_objects for variable number
            of arguments of type Query Object.
        Raises:
            ValueError: If query_objects is None
        Returns:
            Query -- Query object, so you can chain this call.
        ---------------------------------
        [Example]:
            >>> import contentstack
            >>> from contentstack.basequery import QueryOperation
            >>> stack = contentstack.Stack('api_key', 'delivery_token', 'environment')
            >>> query = stack.content_type('content_type1').query()
            >>> self.query1 = stack.content_type('content_type2').query()
            >>> self.query2 = stack.content_type('content_type3').query()
            >>> query1 = self.query1.where("price", QueryOperation.IS_LESS_THAN, fields=90)
            >>> query2 = self.query2.where("discount", QueryOperation.INCLUDES, fields=[20, 45])
            >>> query = query.query_operator(query1, query2)
            >>> result = query.find()
        ---------------------------------
        """
        __container = []
        if len(query_objects) > 0:
            for query in query_objects:
                __container.append(query.parameters)
        if len(self.parameters) > 0:
            self.parameters.clear()
        self.query_params["query"] = json.dumps(
            {query_type.value: __container})
        return self

    def tags(self, *tags):
        """
        Include tags with which to search entries accepts variable-length argument lists
        Arguments:
            tags {list of str} -- tags accepts variable-length argument lists to search entries.
        Returns:
            [Query] -- Query object, so you can chain this call.

        ----------------------------------
        Example:
            >>> import contentstack
            >>> stack = contentstack.Stack('api_key', 'delivery_token', 'environment')
            >>> content_type = stack.content_type('content_type_uid')
            >>> query = content_type.query()
            >>> query = query.tags('black', 'gold', 'silver')
            >>> result = query.find()
        ----------------------------------
        """
        if tags is not None:
            self.query_params["tags"] = ",".join(tags)
        return self

    @deprecation.deprecated(
        deprecated_in="1.7.0",
        current_version='1.8.0',
        details="Use regex function instead")
    def search(self, value: str):
        """
        This method provides only the entries matching
        the specified value.
        @Deprecated deprecated in 1.7.0, Use #regex instaead
        Arguments:
            value {str} -- value used to match or compare
        Raises:
            ValueError: If value is None
            ValueError: If type od value is not str
        Returns:
            [Query] -- Query object, so you can chain this call.
        -------------------------------------
        [Example]
            >>> import contentstack
            >>> stack = contentstack.Stack('api_key', 'delivery_token', 'environment')
            >>> content_type = stack.content_type('content_type_uid')
            >>> query = content_type.query()
            >>> query = query.search("search_keyword")
            >>> result = query.find()
        -------------------------------------
        """
        if value is not None:
            self.query_params["typeahead"] = value
        return self

    def where_in(self, key: str, query_object):
        """Get entries having values based on referenced fields.
        This query retrieves all entries that satisfy the query
        conditions made on referenced fields.
        Arguments:
            key {str} -- The key to be constrained
        Raises:
            ValueError: If key is None
            ValueError: If key is not str type
        Returns:
            [Query] -- Query object, so you can chain this call.
        -------------------------------------
        [Example]
            >>> import contentstack
            >>> stack = contentstack.Stack('api_key', 'delivery_token', 'environment')
            >>> content_type = stack.content_type('content_type_uid')
            >>> query = content_type.query()
            >>> query = query.where_in("brand")
            >>> result = query.find()
        -------------------------------------
        :param key:
        :type query_object: object
        """
        if isinstance(key, str) and query_object is not None and isinstance(query_object, Query):
            self.query_params["query"] = {
                key: {"$in_query": query_object.parameters}}
        else:
            raise ValueError('Invalid Key or Value provided')
        return self

    def where_not_in(self, key, query_object):
        """Get entries having values based on referenced fields.
        This query works the opposite of $in_query and
        retrieves all entries that does not satisfy query
        conditions made on referenced fields.
        Arguments:
            key {str} -- The key to be constrained
        Raises:
            ValueError: If key is None
            ValueError: If key is not str type
        Returns:
            [Query] -- Query object, so you can chain this call.
        -------------------------------------
        [Example]
            >>> import contentstack
            >>> stack = contentstack.Stack('api_key', 'delivery_token', 'environment')
            >>> content_type = stack.content_type('content_type_uid')
            >>> query = content_type.query()
            >>> query = query.where_not_in("brand")
            >>> result = query.find()
        -------------------------------------
        """
        # pylint: disable=W0212
        if isinstance(key, str) and query_object is not None and isinstance(query_object, Query):
            self.query_params["query"] = {
                key: {"$nin_query": query_object.parameters}}
        else:
            raise ValueError('Invalid Key or Value provided')
        return self

    def include_fallback(self):
        """Retrieve the published content of the fallback locale if an
        entry is not localized in specified locale.

        :return: Query, so we can chain the call

        ----------------------------
        Example:

            >>> import contentstack
            >>> stack = contentstack.Stack('api_key', 'delivery_token', 'environment')
            >>> content_type = stack.content_type('content_type_uid')
            >>> query = content_type.query()
            >>> query = query.include_fallback()
            >>> result = query.find()
        ----------------------------
        """
        self.query_params['include_fallback'] = "true"
        return self

    def include_branch(self):
        """Retrieve the published pranch in the response
        :return: Entry, so we can chain the call
        ----------------------------
        Example::

            >>> import contentstack
            >>> stack = contentstack.Stack('api_key', 'delivery_token', 'environment')
            >>> content_type = stack.content_type('content_type_uid')
            >>> query = content_type.query()
            >>> query = query.include_branch()
            >>> result = query.find()
        ----------------------------
        """
        self.query_params['include_branch'] = 'true'
        return self

    def include_embedded_items(self):
        """include_embedded_items instance of Query
        include_embedded_objects (Entries and Assets) along with entry/entries details.
        :return: Query, so we can chain the call

        ----------------------------
        Example:

            >>> import contentstack
            >>> stack = contentstack.Stack('api_key', 'delivery_token', 'environment')
            >>> content_type = stack.content_type('content_type_uid')
            >>> query = content_type.query()
            >>> query = query.include_embedded_items()
            >>> result = query.find()
        ----------------------------
        """
        self.query_params['include_embedded_items[]'] = "BASE"
        return self

    def find(self):
        """It fetches the query result.
        List of :class:`Entry <contentstack.entry.Entry>` objects.
        Raises:
            ValueError: If content_type_id is None
            ValueError: If content_type_id is empty or not str type
        Returns:
            list[Entry] -- List of <contentstack.entry.Entry>
        -------------------------------------
        [Example]:
            >>> import contentstack
            >>> stack = contentstack.Stack('api_key', 'delivery_token', 'environment')
            >>> content_type = stack.content_type('content_type_uid')
            >>> query = content_type.query()
            >>> result = query.find()
        -------------------------------------
        """
        return self.__execute_network_call()

    def find_one(self):
        """It returns only one result.
        Returns:
            list[Entry] -- List of <contentstack.entry.Entry>
        -------------------------------------
        [Example]:
            >>> import contentstack
            >>> stack = contentstack.Stack('api_key', 'delivery_token', 'environment')
            >>> content_type = stack.content_type('content_type_uid')
            >>> query = content_type.query()
            >>> result = query.find_one()
        -------------------------------------
        """
        self.query_params["limit"] = 1
        return self.__execute_network_call()

    def __validate_live_preview(self):
        live_preview = self.http_instance.live_preview
        if 'enable' in live_preview and live_preview['enable'] \
                and self.content_type_uid == live_preview['content_type_uid']:
            if 'live_preview' in live_preview:
                self.query_params['live_preview'] = live_preview['live_preview']
            else:
                self.query_params['live_preview'] = 'init'  # initialise

    def __execute_network_call(self):
        if len(self.entry_queryable_param) > 0:
            self.query_params.update(self.entry_queryable_param)
        if len(self.parameters) > 0:
            self.query_params["query"] = json.dumps(self.parameters)
        if 'environment' in self.http_instance.headers:
            self.query_params['environment'] = self.http_instance.headers['environment']
        self.__validate_live_preview()
        encoded_string = parse.urlencode(self.query_params, doseq=True)
        url = f'{self.base_url}?{encoded_string}'
        if self.http_instance.live_preview['content_type_uid'] == self.content_type_uid:
            _rq = self.http_instance.get(url)['entries']
            _preview = self.http_instance.live_preview['resp']
            return self._merge_preview(_rq, _preview)
        return self.http_instance.get(url)

    def _merge_preview(self, qresp, _preview):
        if isinstance(qresp, dict):
            if 'uid' in qresp and qresp['uid'] == _preview['uid']:
                merged = {**qresp, **_preview}  # TODO: Check merging is properly written or not
            else:
                for key in dict.keys():
                    qresp[key] = self._merge_preview(qresp[key])
        elif isinstance(qresp, list):
            for index, it in enumerate(qresp):
                qresp[index] = self._merge_preview(it, _preview)
        return qresp
