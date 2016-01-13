
from rest_framework_extensions.key_constructor.constructors import DefaultListKeyConstructor
from rest_framework_extensions.key_constructor import bits


class PaginationKeyBit(bits.QueryParamsKeyBit):
    def get_data(self, **kwargs):
        kwargs['params'] = []
        if hasattr(kwargs['view_instance'], 'paginator'):
            if hasattr(kwargs['view_instance'].paginator, 'page_query_param'):
                kwargs['params'].append(kwargs['view_instance'].paginator.page_query_param)
            if hasattr(kwargs['view_instance'].paginator, 'page_size_query_param'):
                kwargs['params'].append(kwargs['view_instance'].paginator.page_size_query_param)
        return super(PaginationKeyBit, self).get_data(**kwargs)


class FixedListKeyConstructor(DefaultListKeyConstructor):
    list_sql_query = bits.ListSqlQueryKeyBit()
    pagination = PaginationKeyBit()


fixed_list_cache_key_func = FixedListKeyConstructor()
