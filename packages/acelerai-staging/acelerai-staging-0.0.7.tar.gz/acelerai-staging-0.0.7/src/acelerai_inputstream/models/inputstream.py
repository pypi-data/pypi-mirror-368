import copy
from datetime import datetime
from enum import Enum
from uuid import UUID

# Enums
class FileIndexFieldType(Enum):
    Datetime = 0
    String = 1
    Number = 2
    Integer = 3

class DateBucketSize(Enum):
    Minute = 0
    Hour = 1
    Day = 2
    Week = 3
    Month = 4
    Year = 5

class InputstreamStatus(Enum):
    ToDiscover = 0
    Undiscovered = 1
    Exposed = 2
    ToDiscoverAgain = 3

class InputstreamStorage(Enum):
    Collection = 0
    TimeSeriesCollection = 1
    File = 2

class InputstreamProtocol(Enum):
    MQTT = 0
    HTTP = 1
    BOTH = 2

class RealTimeMode(Enum):
    OFF = 0
    ON = 1

class IndexType(Enum):
    Unique = 0
    Search = 1

class SortType(Enum):
    Ascending = 0
    Descending = 1

class SourceType(Enum):
    MySQL=0
    MongoDB=1
    SQLServer=2
    Snowflake=3
    Oracle=4
    PostgresSQL=5
    Firebase=6
    BigQuery=7

class DataType(Enum):
    TypeNumber = 0
    TypeBoolean = 1
    TypeString = 2
    TypeDateType = 3
    TypeDate = 4
    TypeList = 5

class InputstreamType(Enum):
    InSystem = 0
    Native = 1

# Models
class DynamicField:
    DataType: DataType
    Field: str
    ValueDefault: str

    def __init__(self, **kwargs) -> None:
        kwargs["DataType"] = DataType(kwargs.pop('DataType'))
        self.__dict__ = kwargs

    def get_dict(self):
        data = copy.deepcopy(self.__dict__)
        return data 

class DataConnection:
    ConnectionString: str
    DataSourceName: str
    Query : str
    SourceType: SourceType
    DynamicFields: list[DynamicField]
    DatabaseName: str

    def __init__(self,**kwargs)-> None:
        kwargs["SourceType"] = SourceType(kwargs.pop('SourceType'))
        self.__dict__ = kwargs
    
    def get_dict(self):
        data = copy.deepcopy(self.__dict__)
        return data


class IndexField:
    Name: str
    FieldType: FileIndexFieldType
    DoubleBucketSize: float
    DateBucketSize: DateBucketSize

    def __init__(self, from_response=False, **kwargs):
        if from_response:
            kwargs["Name"] = kwargs.pop('name')
            kwargs["DoubleBucketSize"] = kwargs.pop('doubleBucketSize')
            kwargs["FieldType"] = FileIndexFieldType(kwargs.pop('fieldType'))
            kwargs["DateBucketSize"] = DateBucketSize(kwargs.pop('dateBucketSize'))
        else:
            kwargs["FieldType"] = FileIndexFieldType(kwargs.pop('FieldType'))
            kwargs["DateBucketSize"] = DateBucketSize(kwargs.pop('DateBucketSize'))
        self.__dict__ = kwargs

    def get_dict(self):
        data = copy.deepcopy(self.__dict__)
        return data


class CollectionIndexField:
    Name: str
    SortType: SortType

    def __init__(self, from_response=False, **kwargs):
        if from_response:
            kwargs["Name"] = kwargs.pop('name')
            kwargs["SortType"] = SortType(kwargs.pop('sortType'))
        else:
            kwargs["SortType"] = SortType(kwargs["SortType"])
        self.__dict__ = kwargs

    def get_dict(self):
        data = copy.deepcopy(self.__dict__)
        return data


class CollectionIndex:
    Name: str
    Fields: list[CollectionIndexField]
    Size: int
    IndexUse: int
    SinceUse: datetime
    IndexType: IndexType
    DateCreated: datetime
    IsCompound: bool

    def __init__(self, from_response=False, **kwargs):
        if from_response:
            kwargs["Name"] = kwargs.pop('name')
            kwargs["DateCreated"] = kwargs.pop('dateCreated')
            kwargs["Fields"] = [CollectionIndexField(from_response=True, **x) for x in kwargs.pop('fields')]
            kwargs["IndexType"] = IndexType(kwargs.pop('indexType'))
        else:
            kwargs["DateCreated"] = kwargs.pop('DateCreated')
            kwargs["Fields"] = [CollectionIndexField(**x) for x in kwargs["Fields"]]
            kwargs["IndexType"] = IndexType(kwargs.pop('IndexType'))
        self.__dict__ = kwargs

    def get_dict(self):
        data = copy.deepcopy(self.__dict__)
        data["Fields"] = [x.get_dict() for x in self.Fields]
        return data
    
class ExternalDataConnectionDTO:
    Id: UUID 
    ConnectionKey: str 
    Name: str 
    DataSourceName: str 
    DatabaseName: str 
    Tags: list[str] 
    DatabaseType: SourceType 
    CreatedOn: datetime 
    Removed: bool 
    
    def __init__(self, from_response = False, **kwargs):
        if from_response: self.from_response(**kwargs)
        else:
            kwargs["Id"] = UUID(kwargs.pop('Id'))
            kwargs["ConnectionKey"] = kwargs.pop('ConnectionKey')
            kwargs["Name"] = kwargs.pop('Name')
            kwargs["DataSourceName"] = kwargs.pop('DataSourceName')
            kwargs["DatabaseName"] = kwargs.pop('DatabaseName')
            kwargs["Tags"] = kwargs.pop('Tags')
            kwargs["DatabaseType"] = SourceType(kwargs.pop('DatabaseType'))
            kwargs["CreatedOn"] = kwargs.pop('CreatedOn')

            self.__dict__ = kwargs
            
    def from_response(self, **kwargs) -> None:
        kwargs["Id"] = UUID(kwargs.pop('id'))
        kwargs["ConnectionKey"] = kwargs.pop('connectionKey')
        kwargs["Name"] = kwargs.pop('name')
        kwargs["DatabaseName"] = kwargs.pop('databaseName')
        kwargs["DatabaseType"] = SourceType(kwargs.pop('databaseType'))
        kwargs["CreatedOn"] = kwargs.pop('createdOn')

        self.__dict__ = kwargs
        
    def get_dict(self):
        data = copy.deepcopy(self.__dict__)
        data["Id"] = str(data["Id"])
        return data

class Inputstream:
    Id: UUID
    SubscriptionId: UUID
    Name: str
    CollectionName: str
    CollectionMongo: str | None
    Schema: str
    SchemaSample: str
    SampleDate: datetime
    Status: InputstreamStatus
    InputstreamType: InputstreamType
    DataConnection: DataConnection
    ExternalDataConnId: UUID
    Tags: list[str]
    Ikey: str
    CollectionIndexes: list[CollectionIndex]
    FilesIndex: list[IndexField]
    Storage: InputstreamStorage
    Protocol: InputstreamProtocol
    RealTimeMode: RealTimeMode
    Size: int
    MaxNDocsByFile: int
    AllowAnyOrigin: bool
    FileConsolidatorCron: str
    Removed: bool
    CreatedOn: datetime
    RemovedOn: datetime | None


    def __init__(self, from_response = False, **kwargs):
        if from_response: self.from_response(**kwargs)
        else:
            kwargs["Id"] = UUID(kwargs.pop('Id'))
            """ kwargs["ExternalDataConnId"] = UUID(kwargs.pop('ExternalDataConnId')) """
            kwargs["ExternalDataConnId"] = UUID(kwargs.pop('ExternalDataConnId')) if kwargs.get('ExternalDataConnId') else None
            
            kwargs["Status"]       = InputstreamStatus(kwargs.pop('Status'))
            kwargs["DataConnection"] = DataConnection(**kwargs["DataConnection"])
            kwargs["InputstreamType"] = InputstreamType(kwargs.pop('InputstreamType'))
            kwargs["Storage"]      = InputstreamStorage(kwargs.pop('Storage'))
            kwargs["Protocol"]     = InputstreamProtocol(kwargs.pop('Protocol'))
            kwargs["RealTimeMode"] = RealTimeMode(kwargs.pop('RealTimeMode'))

            kwargs["FilesIndex"]        = [IndexField(**x) for x in kwargs["FilesIndex"]]
            kwargs["CollectionIndexes"] = [CollectionIndex(**x) for x in kwargs["CollectionIndexes"]]

            self.__dict__ = kwargs

    
    def from_response(self, **kwargs) -> None:
        kwargs["Id"]           = UUID(kwargs.pop('id'))
        kwargs["SubscriptionId"]            = UUID(kwargs.pop('subscriptionId'))
        kwargs["ExternalDataConnId"]        = UUID(kwargs.pop('externalDataConnId')) if kwargs.get('externalDataConnId') else None

        kwargs["Name"]                      = kwargs.pop('name')
        kwargs["CollectionName"]            = kwargs.pop('collectionName')
        kwargs["CollectionMongo"]           = kwargs.pop('collectionMongo')
        kwargs["Schema"]                    = kwargs.pop('schema')
        kwargs["SchemaSample"]              = kwargs.pop('schemaSample')
        kwargs["Tags"]                      = kwargs.pop('tags')
        kwargs["Ikey"]                      = kwargs.pop('ikey')
        kwargs["Size"]                      = kwargs.pop('size')
        kwargs["MaxNDocsByFile"]            = kwargs.pop('maxNDocsByFile')
        kwargs["AllowAnyOrigin"]            = kwargs.pop('allowAnyOrigin')
        kwargs["FileConsolidatorCron"]      = kwargs.pop('fileConsolidatorCron')
        kwargs["Removed"]                   = kwargs.pop('removed')

        kwargs["Status"]       = InputstreamStatus(kwargs.pop('status'))
        kwargs["Storage"]      = InputstreamStorage(kwargs.pop('storage'))
        kwargs["Protocol"]     = InputstreamProtocol(kwargs.pop('protocol'))
        kwargs["RealTimeMode"] = RealTimeMode(kwargs.pop('realTimeMode'))
        kwargs["InputstreamType"] = InputstreamType(kwargs.pop('inputstreamType'))

        kwargs["FilesIndex"]        = [IndexField(from_response=True,**x) for x in kwargs.pop("filesIndex")]
        kwargs["CollectionIndexes"] = [CollectionIndex(from_response=True, **x) for x in kwargs.pop("collectionIndexes")]

        kwargs["SampleDate"]  = kwargs.pop('sampleDate')
        kwargs["CreatedOn"]   = kwargs.pop('createdOn') 
        kwargs["RemovedOn"]   = kwargs.pop('removedOn') 

        self.__dict__ = kwargs

    def get_dict(self):
        data = copy.deepcopy(self.__dict__)
        data["Id"] = str(data["Id"])
        data["FilesIndex"] = [x.get_dict() for x in self.FilesIndex]
        data["CollectionIndexes"] = [x.get_dict() for x in self.CollectionIndexes]
        return data


class INSERTION_MODE(Enum):
    """
    Enum for insertion modes, available modes: 
    REPLACE: if a document collides with an existing document by a unique index, the existing document is replaced with the new document. Otherwise, the new document is inserted.
    INSERT_UNORDERED: insert all documents that did not have a collision with an existing document by a unique index.
    TRANSACTION: insert all documents in a transaction, if a document collides with an existing document by a unique index, the transaction is aborted and no document is inserted.
    """
    REPLACE = 0
    INSERT_UNORDERED = 1
    TRANSACTION = 2
    
class TYPE_OF_RETRY(Enum):
    """
    Enum for type of retry, available modes:
    NONE: no retry is performed.
    RETRY_ON_ERROR: retry on error, if an error occurs, the operation is retried.
    RETRY_ON_TIMEOUT: retry on timeout, if a timeout occurs, the operation is retried.
    """
    RETRY_FROM_BEGINNING = 0
    RETRY_FROM_ERROR = 1