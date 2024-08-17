class ODSException(Exception):
    pass
class ODSPermissionException(ODSException):
    pass
class FiwareException(ODSException):
    pass
class DataCatalogExists(ODSException):
    pass
class DataCatalogNotFound(ODSException):
    pass
class DataCatalogUpdateError(ODSException):
    pass
