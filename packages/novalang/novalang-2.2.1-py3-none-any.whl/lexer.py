#!/usr/bin/env python3
"""
NovaLang Advanced Lexer with Complete Feature Set
Supports all enterprise, AI, blockchain, cloud-native, and performance features
"""

import re
import enum
from typing import List, NamedTuple, Optional, Dict, Set
from dataclasses import dataclass

class TokenType(enum.Enum):
    # Basic tokens
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    
    # Keywords - Basic
    CLASS = "class"
    INTERFACE = "interface"
    FUNCTION = "function"
    LET = "let"
    CONST = "const"
    VAR = "var"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    FOR = "for"
    RETURN = "return"
    IMPORT = "import"
    EXPORT = "export"
    TRUE = "true"
    FALSE = "false"
    NULL = "null"
    NEW = "new"
    
    # Visibility modifiers
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"
    UNDEFINED = "undefined"
    
    # Advanced Type System
    TYPE = "type"
    UNION = "union"
    MATCH = "match"
    WHEN = "when"
    OPTIONAL = "Optional"
    RESULT = "Result"
    SOME = "Some"
    NONE = "None"
    SUCCESS = "Success"
    FAILURE = "Failure"
    SEALED = "sealed"
    TRAIT = "trait"
    IMPL = "impl"
    EXTENDS = "extends"
    IMPLEMENTS = "implements"
    GENERIC = "generic"
    WHERE = "where"
    
    # Enterprise Annotations
    COMPONENT = "@Component"
    SERVICE = "@Service"
    REPOSITORY = "@Repository"
    CONTROLLER = "@Controller"
    ENTITY = "@Entity"
    CONFIGURATION = "@Configuration"
    BEAN = "@Bean"
    INJECT = "@Inject"
    AUTOWIRED = "@Autowired"
    VALUE = "@Value"
    PROFILE = "@Profile"
    
    # Cloud-Native & Microservices
    MICROSERVICE = "@MicroService"
    LOADBALANCER = "@LoadBalancer"
    CIRCUITBREAKER = "@CircuitBreaker"
    APIGATEWAY = "@ApiGateway"
    SERVICEDISCOVERY = "@ServiceDiscovery"
    HEALTHCHECK = "@HealthCheck"
    METRICS = "@Metrics"
    TRACED = "@Traced"
    CACHED = "@Cached"
    RATELIMIT = "@RateLimit"
    TIMEOUT = "@Timeout"
    RETRY = "@Retry"
    FALLBACK = "@Fallback"
    BULKHEAD = "@Bulkhead"
    
    # Kubernetes & Container
    KUBERNETESDEPLOYMENT = "@KubernetesDeployment"
    DOCKERIMAGE = "@DockerImage"
    CONFIGMAP = "@ConfigMap"
    SECRET = "@Secret"
    INGRESS = "@Ingress"
    PERSISTENTVOLUME = "@PersistentVolume"
    CRONJOB = "@CronJob"
    
    # Modern APIs
    GRAPHQLSCHEMA = "@GraphQLSchema"
    QUERY = "@Query"
    MUTATION = "@Mutation"
    SUBSCRIPTION = "@Subscription"
    GRPCSERVICE = "@GrpcService"
    RPCMETHOD = "@RpcMethod"
    SERVERSTREAMING = "@ServerStreaming"
    CLIENTSTREAMING = "@ClientStreaming"
    BIDIRECTIONALSTREAMING = "@BidirectionalStreaming"
    WEBSOCKET = "@WebSocket"
    SSE = "@ServerSentEvents"
    WEBRTC = "@WebRTC"
    
    # Reactive Programming
    OBSERVABLE = "Observable"
    PUBLISHER = "Publisher"
    SUBSCRIBER = "Subscriber"
    STREAM = "Stream"
    FLUX = "Flux"
    MONO = "Mono"
    REACTIVE = "@Reactive"
    ASYNC = "@Async"
    AWAIT = "await"
    BACKPRESSURE = "@Backpressure"
    
    # AI & Machine Learning
    MLMODEL = "@MLModel"
    TENSORFLOWMODEL = "@TensorFlowModel"
    PYTORCHMODEL = "@PyTorchModel"
    AUTOML = "@AutoML"
    PREDICT = "@Predict"
    BATCHPREDICT = "@BatchPredict"
    PREPROCESSING = "@PreProcess"
    POSTPROCESSING = "@PostProcess"
    TRAINING = "@Training"
    INFERENCE = "@InferenceMode"
    HUGGINGFACEMODEL = "@HuggingFaceModel"
    NAMEDENTITYRECOGNITION = "@NamedEntityRecognition"
    SENTIMENTANALYSIS = "@SentimentAnalysis"
    TEXTGENERATION = "@TextGeneration"
    COMPUTERVISION = "@ComputerVision"
    YOLOMODEL = "@YOLOModel"
    SEGMENTATIONMODEL = "@SegmentationModel"
    FACERECOGNITION = "@FaceRecognition"
    REINFORCEMENTLEARNING = "@ReinforcementLearning"
    FEDERATEDLEARNING = "@FederatedLearning"
    
    # Security & Authentication
    SECURED = "@Secured"
    PREAUTHORIZE = "@PreAuthorize"
    POSTAUTHORIZE = "@PostAuthorize"
    ROLESALLOWED = "@RolesAllowed"
    OAUTH2 = "@OAuth2"
    WEBAUTHN = "@WebAuthn"
    SAML2 = "@SAML2"
    JWT = "@JWT"
    ENCRYPT = "@Encrypt"
    DECRYPT = "@Decrypt"
    HASH = "@Hash"
    SIGN = "@Sign"
    VERIFY = "@Verify"
    AUDITLOG = "@AuditLog"
    DATAMASKING = "@DataMasking"
    ZEROTRUSTSECURITY = "@ZeroTrustSecurity"
    MULTIFACTOR = "@MultiFactorAuth"
    
    # Blockchain & Cryptocurrency
    SMARTCONTRACT = "@SmartContract"
    SOLIDITYFUNCTION = "@SolidityFunction"
    PUBLICFUNCTION = "@PublicFunction"
    PRIVATEFUNCTION = "@PrivateFunction"
    PAYABLEFUNCTION = "@Payable"
    VIEWFUNCTION = "@View"
    PUREFUNCTION = "@Pure"
    MODIFIER = "@Modifier"
    EVENT = "@Event"
    STATE = "@State"
    CONSTRUCTOR = "@Constructor"
    BITCOINNETWORK = "@BitcoinNetwork"
    ETHEREUMNETWORK = "@EthereumNetwork"
    WALLET = "@Wallet"
    TRANSACTION = "@Transaction"
    DEFIPROTOCOL = "@DeFiProtocol"
    NFTCONTRACT = "@NFTContract"
    IPFSSTORAGE = "@IPFSStorage"
    WEB3SERVICE = "@Web3Service"
    
    # Performance & Optimization
    PERFORMANCEOPTIMIZED = "@PerformanceOptimized"
    AUTOOPTIMIZE = "@AutoOptimize"
    BENCHMARK = "@Benchmark"
    PARALLELPROCESSING = "@ParallelProcessing"
    MEMORYOPTIMIZED = "@MemoryOptimized"
    CACHEOPTIMIZED = "@CacheOptimized"
    MEMORYPOOL = "@MemoryPool"
    ZEROCOPY = "@ZeroCopy"
    JITOPTIMIZED = "@JITOptimized"
    INLINEHINT = "@InlineHint"
    VECTORIZED = "@Vectorized"
    UNROLLED = "@Unrolled"
    PARALLELFOR = "@ParallelFor"
    NUMA = "@NUMA"
    BRANCHOPTIMIZED = "@BranchOptimized"
    PREFETCHHINT = "@PrefetchHint"
    CPUOPTIMIZED = "@CPUOptimized"
    SIMD = "@SIMD"
    
    # Database & Persistence - Universal Support
    ENTITY_DB = "@Entity"
    TABLE = "@Table"
    COLUMN = "@Column"
    ID = "@Id"
    GENERATEDVALUE = "@GeneratedValue"
    ONETOMANY = "@OneToMany"
    MANYTOONE = "@ManyToOne"
    MANYTOMANY = "@ManyToMany"
    ONETOONE = "@OneToOne"
    JOINCOLUMN = "@JoinColumn"
    JOINTABLE = "@JoinTable"
    QUERY_DB = "@Query"
    NATIVEQUERY = "@NativeQuery"
    MODIFYING = "@Modifying"
    TRANSACTIONAL = "@Transactional"
    DATASOURCE = "@DataSource"
    
    # SQL Databases
    MYSQL = "@MySQL"
    POSTGRESQL = "@PostgreSQL"
    ORACLE = "@Oracle"
    SQLSERVER = "@SQLServer"
    SQLITE = "@SQLite"
    MARIADB = "@MariaDB"
    DB2 = "@DB2"
    HSQLDB = "@HSQLDB"
    H2DATABASE = "@H2Database"
    DERBY = "@Derby"
    FIREBIRD = "@Firebird"
    SYBASE = "@Sybase"
    INFORMIX = "@Informix"
    TERADATA = "@Teradata"
    SNOWFLAKE = "@Snowflake"
    BIGQUERY = "@BigQuery"
    REDSHIFT = "@Redshift"
    CLICKHOUSE = "@ClickHouse"
    VERTICA = "@Vertica"
    GREENPLUM = "@Greenplum"
    
    # NoSQL Databases
    MONGODB = "@MongoDB"
    CASSANDRA = "@Cassandra"
    DYNAMODB = "@DynamoDB"
    COUCHDB = "@CouchDB"
    COUCHBASE = "@Couchbase"
    RIAK = "@Riak"
    HBASE = "@HBase"
    ACCUMULO = "@Accumulo"
    ORIENTDB = "@OrientDB"
    ARANGODB = "@ArangoDB"
    NEO4J = "@Neo4j"
    JANUSGRAPH = "@JanusGraph"
    TIGERGRAPH = "@TigerGraph"
    DGRAPH = "@DGraph"
    AMAZONNEPTUNE = "@AmazonNeptune"
    
    # In-Memory & Cache Databases
    REDIS = "@Redis"
    MEMCACHED = "@Memcached"
    HAZELCAST = "@Hazelcast"
    EHCACHE = "@EhCache"
    CAFFEINE = "@Caffeine"
    IGNITE = "@Ignite"
    GRIDGAIN = "@GridGain"
    COHERENCE = "@Coherence"
    GEMFIRE = "@GemFire"
    INFINISPAN = "@Infinispan"
    
    # Time Series Databases
    INFLUXDB = "@InfluxDB"
    TIMESCALEDB = "@TimescaleDB"
    PROMETHEUS = "@Prometheus"
    GRAPHITE = "@Graphite"
    OPENTSDB = "@OpenTSDB"
    KAIROSDB = "@KairosDB"
    QUESTDB = "@QuestDB"
    VICTORIAMETRICS = "@VictoriaMetrics"
    
    # Search & Analytics
    ELASTICSEARCH = "@Elasticsearch"
    SOLR = "@Solr"
    LUCENE = "@Lucene"
    SPHINX = "@Sphinx"
    WHOOSH = "@Whoosh"
    XAPIAN = "@Xapian"
    
    # Vector & AI Databases
    PINECONE = "@Pinecone"
    WEAVIATE = "@Weaviate"
    MILVUS = "@Milvus"
    QDRANT = "@Qdrant"
    CHROMA = "@Chroma"
    FAISS = "@Faiss"
    ANNOY = "@Annoy"
    
    # Blockchain Databases
    BIGCHAINDB = "@BigchainDB"
    BLUZELLE = "@Bluzelle"
    
    # Multi-Model Databases
    COSMOSDB = "@CosmosDB"
    FAUNA = "@Fauna"
    SURREAL = "@SurrealDB"
    EDGEDB = "@EdgeDB"
    
    # Database Operations
    DAO = "@DAO"
    CRUD = "@CRUD"
    AGGREGATION = "@Aggregation"
    INDEXING = "@Indexing"
    SHARDING = "@Sharding"
    REPLICATION = "@Replication"
    PARTITION = "@Partition"
    BACKUP = "@Backup"
    MIGRATION = "@Migration"
    SCHEMA = "@Schema"
    CONSTRAINT = "@Constraint"
    TRIGGER = "@Trigger"
    PROCEDURE = "@StoredProcedure"
    FUNCTION_DB = "@DatabaseFunction"
    VIEW = "@View"
    MATERIALIZED_VIEW = "@MaterializedView"
    
    # Connection & Pool Management
    CONNECTIONPOOL = "@ConnectionPool"
    JDBC = "@JDBC"
    ODBC = "@ODBC"
    DBCP = "@DBCP"
    HIKARI = "@HikariCP"
    C3P0 = "@C3P0"
    TOMCATJDBC = "@TomcatJDBC"
    
    # ORM & Mapping
    JPA = "@JPA"
    HIBERNATE = "@Hibernate"
    MYBATIS = "@MyBatis"
    JOOQ = "@JOOQ"
    QUERYDSL = "@QueryDSL"
    SPRING_DATA = "@SpringData"
    MONGOTEMPLATE = "@MongoTemplate"
    CASSANDRATEMPLATE = "@CassandraTemplate"
    REDISTEMPLATE = "@RedisTemplate"
    JDBCTEMPLATE = "@JdbcTemplate"
    NAMEDPARAMETERJDBCTEMPLATE = "@NamedParameterJdbcTemplate"
    
    # Database Performance
    BATCH = "@Batch"
    BULK = "@Bulk"
    STREAMING = "@Streaming"
    PAGINATION = "@Pagination"
    LAZY_LOADING = "@LazyLoading"
    EAGER_LOADING = "@EagerLoading"
    CONNECTION_TIMEOUT = "@ConnectionTimeout"
    QUERY_TIMEOUT = "@QueryTimeout"
    FETCH_SIZE = "@FetchSize"
    RESULT_SET_TYPE = "@ResultSetType"
    
    # Database Security
    ENCRYPTED_DB = "@EncryptedDatabase"
    COLUMN_ENCRYPTION = "@ColumnEncryption"
    ROW_LEVEL_SECURITY = "@RowLevelSecurity"
    AUDIT_TRAIL = "@AuditTrail"
    DATA_CLASSIFICATION = "@DataClassification"
    GDPR_COMPLIANT = "@GDPRCompliant"
    
    # Database Monitoring
    QUERY_STATS = "@QueryStats"
    PERFORMANCE_SCHEMA = "@PerformanceSchema"
    SLOW_QUERY_LOG = "@SlowQueryLog"
    CONNECTION_MONITORING = "@ConnectionMonitoring"
    DEADLOCK_DETECTION = "@DeadlockDetection"
    
    # Validation & Serialization
    VALID = "@Valid"
    VALIDATED = "@Validated"
    NOTNULL = "@NotNull"
    NOTEMPTY = "@NotEmpty"
    NOTBLANK = "@NotBlank"
    SIZE = "@Size"
    MIN = "@Min"
    MAX = "@Max"
    EMAIL = "@Email"
    PATTERN = "@Pattern"
    JSONPROPERTY = "@JsonProperty"
    JSONIGNORE = "@JsonIgnore"
    XMLELEMENT = "@XmlElement"
    
    # Testing
    TEST = "@Test"
    BEFOREEACH = "@BeforeEach"
    AFTEREACH = "@AfterEach"
    BEFOREALL = "@BeforeAll"
    AFTERALL = "@AfterAll"
    MOCK = "@Mock"
    INJECTMOCKS = "@InjectMocks"
    PARAMETRIZEDTEST = "@ParametrizedTest"
    
    # Operators
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    MODULO = "%"
    POWER = "**"
    ASSIGN = "="
    PLUS_ASSIGN = "+="
    MINUS_ASSIGN = "-="
    MULTIPLY_ASSIGN = "*="
    DIVIDE_ASSIGN = "/="
    EQUAL = "=="
    NOT_EQUAL = "!="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_EQUAL = "<="
    GREATER_EQUAL = ">="
    LOGICAL_AND = "&&"
    LOGICAL_OR = "||"
    LOGICAL_NOT = "!"
    BITWISE_AND = "&"
    BITWISE_OR = "|"
    BITWISE_XOR = "^"
    BITWISE_NOT = "~"
    LEFT_SHIFT = "<<"
    RIGHT_SHIFT = ">>"
    ARROW = "->"
    FAT_ARROW = "=>"
    ELVIS = "?:"
    SAFE_CALL = "?."
    NULLISH_COALESCING = "??"
    
    # Punctuation
    SEMICOLON = ";"
    COMMA = ","
    DOT = "."
    COLON = ":"
    QUESTION = "?"
    EXCLAMATION = "!"
    HASH_SYMBOL = "#"
    DOLLAR = "$"
    AT = "@"
    AMPERSAND = "&"
    PIPE = "|"
    BACKSLASH = "\\"
    UNDERSCORE = "_"
    
    # Brackets
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    LEFT_BRACKET = "["
    RIGHT_BRACKET = "]"
    LEFT_ANGLE = "<"
    RIGHT_ANGLE = ">"
    
    # Special
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    EOF = "EOF"
    WHITESPACE = "WHITESPACE"
    COMMENT = "COMMENT"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    position: int

class NovaLangLexer:
    """Advanced lexer for NovaLang with complete feature support"""
    
    def __init__(self, text: str):
        self.text = text
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
        # Keywords mapping
        self.keywords = {
            # Basic keywords
            'class': TokenType.CLASS,
            'interface': TokenType.INTERFACE,
            'function': TokenType.FUNCTION,
            'let': TokenType.LET,
            'const': TokenType.CONST,
            'var': TokenType.VAR,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'return': TokenType.RETURN,
            'import': TokenType.IMPORT,
            'export': TokenType.EXPORT,
            'true': TokenType.TRUE,
            'false': TokenType.FALSE,
            'null': TokenType.NULL,
            'new': TokenType.NEW,
            'undefined': TokenType.UNDEFINED,
            
            # Visibility modifiers
            'public': TokenType.PUBLIC,
            'private': TokenType.PRIVATE,
            'protected': TokenType.PROTECTED,
            
            # Type system
            'type': TokenType.TYPE,
            'union': TokenType.UNION,
            'match': TokenType.MATCH,
            'when': TokenType.WHEN,
            'Optional': TokenType.OPTIONAL,
            'Result': TokenType.RESULT,
            'Some': TokenType.SOME,
            'None': TokenType.NONE,
            'Success': TokenType.SUCCESS,
            'Failure': TokenType.FAILURE,
            'sealed': TokenType.SEALED,
            'trait': TokenType.TRAIT,
            'impl': TokenType.IMPL,
            'extends': TokenType.EXTENDS,
            'implements': TokenType.IMPLEMENTS,
            'generic': TokenType.GENERIC,
            'where': TokenType.WHERE,
            
            # Reactive
            'Observable': TokenType.OBSERVABLE,
            'Publisher': TokenType.PUBLISHER,
            'Subscriber': TokenType.SUBSCRIBER,
            'Stream': TokenType.STREAM,
            'Flux': TokenType.FLUX,
            'Mono': TokenType.MONO,
            'await': TokenType.AWAIT,
        }
        
        # Annotation mapping
        self.annotations = {
            # Enterprise
            '@Component': TokenType.COMPONENT,
            '@Service': TokenType.SERVICE,
            '@Repository': TokenType.REPOSITORY,
            '@Controller': TokenType.CONTROLLER,
            '@Entity': TokenType.ENTITY,
            '@Configuration': TokenType.CONFIGURATION,
            '@Bean': TokenType.BEAN,
            '@Inject': TokenType.INJECT,
            '@Autowired': TokenType.AUTOWIRED,
            '@Value': TokenType.VALUE,
            '@Profile': TokenType.PROFILE,
            
            # Cloud-Native
            '@MicroService': TokenType.MICROSERVICE,
            '@LoadBalancer': TokenType.LOADBALANCER,
            '@CircuitBreaker': TokenType.CIRCUITBREAKER,
            '@ApiGateway': TokenType.APIGATEWAY,
            '@ServiceDiscovery': TokenType.SERVICEDISCOVERY,
            '@HealthCheck': TokenType.HEALTHCHECK,
            '@Metrics': TokenType.METRICS,
            '@Traced': TokenType.TRACED,
            '@Cached': TokenType.CACHED,
            '@RateLimit': TokenType.RATELIMIT,
            '@Timeout': TokenType.TIMEOUT,
            '@Retry': TokenType.RETRY,
            '@Fallback': TokenType.FALLBACK,
            '@Bulkhead': TokenType.BULKHEAD,
            
            # Kubernetes
            '@KubernetesDeployment': TokenType.KUBERNETESDEPLOYMENT,
            '@DockerImage': TokenType.DOCKERIMAGE,
            '@ConfigMap': TokenType.CONFIGMAP,
            '@Secret': TokenType.SECRET,
            '@Ingress': TokenType.INGRESS,
            '@PersistentVolume': TokenType.PERSISTENTVOLUME,
            '@CronJob': TokenType.CRONJOB,
            
            # APIs
            '@GraphQLSchema': TokenType.GRAPHQLSCHEMA,
            '@Query': TokenType.QUERY,
            '@Mutation': TokenType.MUTATION,
            '@Subscription': TokenType.SUBSCRIPTION,
            '@GrpcService': TokenType.GRPCSERVICE,
            '@RpcMethod': TokenType.RPCMETHOD,
            '@ServerStreaming': TokenType.SERVERSTREAMING,
            '@ClientStreaming': TokenType.CLIENTSTREAMING,
            '@BidirectionalStreaming': TokenType.BIDIRECTIONALSTREAMING,
            '@WebSocket': TokenType.WEBSOCKET,
            '@ServerSentEvents': TokenType.SSE,
            '@WebRTC': TokenType.WEBRTC,
            
            # Reactive
            '@Reactive': TokenType.REACTIVE,
            '@Async': TokenType.ASYNC,
            '@Backpressure': TokenType.BACKPRESSURE,
            
            # AI/ML
            '@MLModel': TokenType.MLMODEL,
            '@TensorFlowModel': TokenType.TENSORFLOWMODEL,
            '@PyTorchModel': TokenType.PYTORCHMODEL,
            '@AutoML': TokenType.AUTOML,
            '@Predict': TokenType.PREDICT,
            '@BatchPredict': TokenType.BATCHPREDICT,
            '@PreProcess': TokenType.PREPROCESSING,
            '@PostProcess': TokenType.POSTPROCESSING,
            '@Training': TokenType.TRAINING,
            '@InferenceMode': TokenType.INFERENCE,
            '@HuggingFaceModel': TokenType.HUGGINGFACEMODEL,
            '@NamedEntityRecognition': TokenType.NAMEDENTITYRECOGNITION,
            '@SentimentAnalysis': TokenType.SENTIMENTANALYSIS,
            '@TextGeneration': TokenType.TEXTGENERATION,
            '@ComputerVision': TokenType.COMPUTERVISION,
            '@YOLOModel': TokenType.YOLOMODEL,
            '@SegmentationModel': TokenType.SEGMENTATIONMODEL,
            '@FaceRecognition': TokenType.FACERECOGNITION,
            '@ReinforcementLearning': TokenType.REINFORCEMENTLEARNING,
            '@FederatedLearning': TokenType.FEDERATEDLEARNING,
            
            # Security
            '@Secured': TokenType.SECURED,
            '@PreAuthorize': TokenType.PREAUTHORIZE,
            '@PostAuthorize': TokenType.POSTAUTHORIZE,
            '@RolesAllowed': TokenType.ROLESALLOWED,
            '@OAuth2': TokenType.OAUTH2,
            '@WebAuthn': TokenType.WEBAUTHN,
            '@SAML2': TokenType.SAML2,
            '@JWT': TokenType.JWT,
            '@Encrypt': TokenType.ENCRYPT,
            '@Decrypt': TokenType.DECRYPT,
            '@Hash': TokenType.HASH,
            '@Sign': TokenType.SIGN,
            '@Verify': TokenType.VERIFY,
            '@AuditLog': TokenType.AUDITLOG,
            '@DataMasking': TokenType.DATAMASKING,
            '@ZeroTrustSecurity': TokenType.ZEROTRUSTSECURITY,
            '@MultiFactorAuth': TokenType.MULTIFACTOR,
            
            # Blockchain
            '@SmartContract': TokenType.SMARTCONTRACT,
            '@SolidityFunction': TokenType.SOLIDITYFUNCTION,
            '@PublicFunction': TokenType.PUBLICFUNCTION,
            '@PrivateFunction': TokenType.PRIVATEFUNCTION,
            '@Payable': TokenType.PAYABLEFUNCTION,
            '@View': TokenType.VIEWFUNCTION,
            '@Pure': TokenType.PUREFUNCTION,
            '@Modifier': TokenType.MODIFIER,
            '@Event': TokenType.EVENT,
            '@State': TokenType.STATE,
            '@Constructor': TokenType.CONSTRUCTOR,
            '@BitcoinNetwork': TokenType.BITCOINNETWORK,
            '@EthereumNetwork': TokenType.ETHEREUMNETWORK,
            '@Wallet': TokenType.WALLET,
            '@Transaction': TokenType.TRANSACTION,
            '@DeFiProtocol': TokenType.DEFIPROTOCOL,
            '@NFTContract': TokenType.NFTCONTRACT,
            '@IPFSStorage': TokenType.IPFSSTORAGE,
            '@Web3Service': TokenType.WEB3SERVICE,
            
            # Performance
            '@PerformanceOptimized': TokenType.PERFORMANCEOPTIMIZED,
            '@AutoOptimize': TokenType.AUTOOPTIMIZE,
            '@Benchmark': TokenType.BENCHMARK,
            '@Profile': TokenType.PROFILE,
            '@ParallelProcessing': TokenType.PARALLELPROCESSING,
            '@MemoryOptimized': TokenType.MEMORYOPTIMIZED,
            '@CacheOptimized': TokenType.CACHEOPTIMIZED,
            '@MemoryPool': TokenType.MEMORYPOOL,
            '@ZeroCopy': TokenType.ZEROCOPY,
            '@JITOptimized': TokenType.JITOPTIMIZED,
            '@InlineHint': TokenType.INLINEHINT,
            '@Vectorized': TokenType.VECTORIZED,
            '@Unrolled': TokenType.UNROLLED,
            '@ParallelFor': TokenType.PARALLELFOR,
            '@NUMA': TokenType.NUMA,
            '@BranchOptimized': TokenType.BRANCHOPTIMIZED,
            '@PrefetchHint': TokenType.PREFETCHHINT,
            '@CPUOptimized': TokenType.CPUOPTIMIZED,
            '@SIMD': TokenType.SIMD,
            
            # Database - Universal Support
            '@Table': TokenType.TABLE,
            '@Column': TokenType.COLUMN,
            '@Id': TokenType.ID,
            '@GeneratedValue': TokenType.GENERATEDVALUE,
            '@OneToMany': TokenType.ONETOMANY,
            '@ManyToOne': TokenType.MANYTOONE,
            '@ManyToMany': TokenType.MANYTOMANY,
            '@OneToOne': TokenType.ONETOONE,
            '@JoinColumn': TokenType.JOINCOLUMN,
            '@JoinTable': TokenType.JOINTABLE,
            '@NativeQuery': TokenType.NATIVEQUERY,
            '@Modifying': TokenType.MODIFYING,
            '@Transactional': TokenType.TRANSACTIONAL,
            '@DataSource': TokenType.DATASOURCE,
            '@Repository': TokenType.REPOSITORY,
            '@DAO': TokenType.DAO,
            '@CRUD': TokenType.CRUD,
            
            # SQL Databases
            '@MySQL': TokenType.MYSQL,
            '@PostgreSQL': TokenType.POSTGRESQL,
            '@Oracle': TokenType.ORACLE,
            '@SQLServer': TokenType.SQLSERVER,
            '@SQLite': TokenType.SQLITE,
            '@MariaDB': TokenType.MARIADB,
            '@DB2': TokenType.DB2,
            '@HSQLDB': TokenType.HSQLDB,
            '@H2Database': TokenType.H2DATABASE,
            '@Derby': TokenType.DERBY,
            '@Firebird': TokenType.FIREBIRD,
            '@Sybase': TokenType.SYBASE,
            '@Informix': TokenType.INFORMIX,
            '@Teradata': TokenType.TERADATA,
            '@Snowflake': TokenType.SNOWFLAKE,
            '@BigQuery': TokenType.BIGQUERY,
            '@Redshift': TokenType.REDSHIFT,
            '@ClickHouse': TokenType.CLICKHOUSE,
            '@Vertica': TokenType.VERTICA,
            '@Greenplum': TokenType.GREENPLUM,
            
            # NoSQL Databases
            '@MongoDB': TokenType.MONGODB,
            '@Cassandra': TokenType.CASSANDRA,
            '@DynamoDB': TokenType.DYNAMODB,
            '@CouchDB': TokenType.COUCHDB,
            '@Couchbase': TokenType.COUCHBASE,
            '@Riak': TokenType.RIAK,
            '@HBase': TokenType.HBASE,
            '@Accumulo': TokenType.ACCUMULO,
            '@OrientDB': TokenType.ORIENTDB,
            '@ArangoDB': TokenType.ARANGODB,
            '@Neo4j': TokenType.NEO4J,
            '@JanusGraph': TokenType.JANUSGRAPH,
            '@TigerGraph': TokenType.TIGERGRAPH,
            '@DGraph': TokenType.DGRAPH,
            '@AmazonNeptune': TokenType.AMAZONNEPTUNE,
            
            # In-Memory & Cache
            '@Redis': TokenType.REDIS,
            '@Memcached': TokenType.MEMCACHED,
            '@Hazelcast': TokenType.HAZELCAST,
            '@EhCache': TokenType.EHCACHE,
            '@Caffeine': TokenType.CAFFEINE,
            '@Ignite': TokenType.IGNITE,
            '@GridGain': TokenType.GRIDGAIN,
            '@Coherence': TokenType.COHERENCE,
            '@GemFire': TokenType.GEMFIRE,
            '@Infinispan': TokenType.INFINISPAN,
            
            # Time Series
            '@InfluxDB': TokenType.INFLUXDB,
            '@TimescaleDB': TokenType.TIMESCALEDB,
            '@Prometheus': TokenType.PROMETHEUS,
            '@Graphite': TokenType.GRAPHITE,
            '@OpenTSDB': TokenType.OPENTSDB,
            '@KairosDB': TokenType.KAIROSDB,
            '@QuestDB': TokenType.QUESTDB,
            '@VictoriaMetrics': TokenType.VICTORIAMETRICS,
            
            # Search & Analytics
            '@Elasticsearch': TokenType.ELASTICSEARCH,
            '@Solr': TokenType.SOLR,
            '@Lucene': TokenType.LUCENE,
            '@Sphinx': TokenType.SPHINX,
            '@Whoosh': TokenType.WHOOSH,
            '@Xapian': TokenType.XAPIAN,
            
            # Vector & AI Databases
            '@Pinecone': TokenType.PINECONE,
            '@Weaviate': TokenType.WEAVIATE,
            '@Milvus': TokenType.MILVUS,
            '@Qdrant': TokenType.QDRANT,
            '@Chroma': TokenType.CHROMA,
            '@Faiss': TokenType.FAISS,
            '@Annoy': TokenType.ANNOY,
            
            # Blockchain Databases
            '@BigchainDB': TokenType.BIGCHAINDB,
            '@Bluzelle': TokenType.BLUZELLE,
            
            # Multi-Model
            '@CosmosDB': TokenType.COSMOSDB,
            '@Fauna': TokenType.FAUNA,
            '@SurrealDB': TokenType.SURREAL,
            '@EdgeDB': TokenType.EDGEDB,
            
            # ORM & Mapping
            '@JPA': TokenType.JPA,
            '@Hibernate': TokenType.HIBERNATE,
            '@MyBatis': TokenType.MYBATIS,
            '@JOOQ': TokenType.JOOQ,
            '@QueryDSL': TokenType.QUERYDSL,
            '@SpringData': TokenType.SPRING_DATA,
            '@MongoTemplate': TokenType.MONGOTEMPLATE,
            '@CassandraTemplate': TokenType.CASSANDRATEMPLATE,
            '@RedisTemplate': TokenType.REDISTEMPLATE,
            '@JdbcTemplate': TokenType.JDBCTEMPLATE,
            '@NamedParameterJdbcTemplate': TokenType.NAMEDPARAMETERJDBCTEMPLATE,
            
            # Connection Management
            '@ConnectionPool': TokenType.CONNECTIONPOOL,
            '@JDBC': TokenType.JDBC,
            '@ODBC': TokenType.ODBC,
            '@DBCP': TokenType.DBCP,
            '@HikariCP': TokenType.HIKARI,
            '@C3P0': TokenType.C3P0,
            '@TomcatJDBC': TokenType.TOMCATJDBC,
            
            # Database Operations
            '@Aggregation': TokenType.AGGREGATION,
            '@Indexing': TokenType.INDEXING,
            '@Sharding': TokenType.SHARDING,
            '@Replication': TokenType.REPLICATION,
            '@Partition': TokenType.PARTITION,
            '@Backup': TokenType.BACKUP,
            '@Migration': TokenType.MIGRATION,
            '@Schema': TokenType.SCHEMA,
            '@Constraint': TokenType.CONSTRAINT,
            '@Trigger': TokenType.TRIGGER,
            '@StoredProcedure': TokenType.PROCEDURE,
            '@DatabaseFunction': TokenType.FUNCTION_DB,
            '@View': TokenType.VIEW,
            '@MaterializedView': TokenType.MATERIALIZED_VIEW,
            
            # Performance
            '@Batch': TokenType.BATCH,
            '@Bulk': TokenType.BULK,
            '@Streaming': TokenType.STREAMING,
            '@Pagination': TokenType.PAGINATION,
            '@LazyLoading': TokenType.LAZY_LOADING,
            '@EagerLoading': TokenType.EAGER_LOADING,
            '@ConnectionTimeout': TokenType.CONNECTION_TIMEOUT,
            '@QueryTimeout': TokenType.QUERY_TIMEOUT,
            '@FetchSize': TokenType.FETCH_SIZE,
            '@ResultSetType': TokenType.RESULT_SET_TYPE,
            
            # Security
            '@EncryptedDatabase': TokenType.ENCRYPTED_DB,
            '@ColumnEncryption': TokenType.COLUMN_ENCRYPTION,
            '@RowLevelSecurity': TokenType.ROW_LEVEL_SECURITY,
            '@AuditTrail': TokenType.AUDIT_TRAIL,
            '@DataClassification': TokenType.DATA_CLASSIFICATION,
            '@GDPRCompliant': TokenType.GDPR_COMPLIANT,
            
            # Monitoring
            '@QueryStats': TokenType.QUERY_STATS,
            '@PerformanceSchema': TokenType.PERFORMANCE_SCHEMA,
            '@SlowQueryLog': TokenType.SLOW_QUERY_LOG,
            '@ConnectionMonitoring': TokenType.CONNECTION_MONITORING,
            '@DeadlockDetection': TokenType.DEADLOCK_DETECTION,
            
            # Validation
            '@Valid': TokenType.VALID,
            '@Validated': TokenType.VALIDATED,
            '@NotNull': TokenType.NOTNULL,
            '@NotEmpty': TokenType.NOTEMPTY,
            '@NotBlank': TokenType.NOTBLANK,
            '@Size': TokenType.SIZE,
            '@Min': TokenType.MIN,
            '@Max': TokenType.MAX,
            '@Email': TokenType.EMAIL,
            '@Pattern': TokenType.PATTERN,
            '@JsonProperty': TokenType.JSONPROPERTY,
            '@JsonIgnore': TokenType.JSONIGNORE,
            '@XmlElement': TokenType.XMLELEMENT,
            
            # Testing
            '@Test': TokenType.TEST,
            '@BeforeEach': TokenType.BEFOREEACH,
            '@AfterEach': TokenType.AFTEREACH,
            '@BeforeAll': TokenType.BEFOREALL,
            '@AfterAll': TokenType.AFTERALL,
            '@Mock': TokenType.MOCK,
            '@InjectMocks': TokenType.INJECTMOCKS,
            '@ParametrizedTest': TokenType.PARAMETRIZEDTEST,
        }
    
    def current_char(self) -> Optional[str]:
        if self.position >= len(self.text):
            return None
        return self.text[self.position]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        peek_pos = self.position + offset
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]
    
    def advance(self):
        if self.position < len(self.text) and self.text[self.position] == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.position += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def read_number(self) -> str:
        num_str = ''
        has_dot = False
        
        while self.current_char() and (self.current_char().isdigit() or 
                                     (self.current_char() == '.' and not has_dot)):
            if self.current_char() == '.':
                has_dot = True
            num_str += self.current_char()
            self.advance()
        
        # Handle scientific notation
        if self.current_char() and self.current_char().lower() == 'e':
            num_str += self.current_char()
            self.advance()
            if self.current_char() and self.current_char() in '+-':
                num_str += self.current_char()
                self.advance()
            while self.current_char() and self.current_char().isdigit():
                num_str += self.current_char()
                self.advance()
        
        return num_str
    
    def read_string(self, quote_char: str) -> str:
        string_val = ''
        self.advance()  # Skip opening quote
        
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                escape_char = self.current_char()
                if escape_char == 'n':
                    string_val += '\n'
                elif escape_char == 't':
                    string_val += '\t'
                elif escape_char == 'r':
                    string_val += '\r'
                elif escape_char == '\\':
                    string_val += '\\'
                elif escape_char == quote_char:
                    string_val += quote_char
                else:
                    string_val += escape_char or ''
            else:
                string_val += self.current_char()
            self.advance()
        
        if self.current_char() == quote_char:
            self.advance()  # Skip closing quote
        
        return string_val
    
    def read_identifier(self) -> str:
        identifier = ''
        
        while (self.current_char() and 
               (self.current_char().isalnum() or self.current_char() in '_$')):
            identifier += self.current_char()
            self.advance()
        
        return identifier
    
    def read_annotation(self) -> str:
        annotation = '@'
        self.advance()  # Skip @
        
        while (self.current_char() and 
               (self.current_char().isalnum() or self.current_char() in '_')):
            annotation += self.current_char()
            self.advance()
        
        return annotation
    
    def skip_comment(self):
        if self.current_char() == '/' and self.peek_char() == '/':
            # Single line comment
            while self.current_char() and self.current_char() != '\n':
                self.advance()
        elif self.current_char() == '/' and self.peek_char() == '*':
            # Multi-line comment
            self.advance()  # Skip /
            self.advance()  # Skip *
            
            while self.current_char():
                if self.current_char() == '*' and self.peek_char() == '/':
                    self.advance()  # Skip *
                    self.advance()  # Skip /
                    break
                self.advance()
    
    def tokenize(self) -> List[Token]:
        while self.position < len(self.text):
            self.skip_whitespace()
            
            if not self.current_char():
                break
            
            start_line = self.line
            start_column = self.column
            start_position = self.position
            
            char = self.current_char()
            
            # Handle newlines
            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, char, start_line, start_column, start_position))
                self.advance()
                continue
            
            # Handle comments
            if char == '/' and (self.peek_char() == '/' or self.peek_char() == '*'):
                self.skip_comment()
                continue
            
            # Handle numbers
            if char.isdigit():
                number = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, number, start_line, start_column, start_position))
                continue
            
            # Handle strings
            if char in '"\'`':
                string_val = self.read_string(char)
                self.tokens.append(Token(TokenType.STRING, string_val, start_line, start_column, start_position))
                continue
            
            # Handle annotations
            if char == '@':
                annotation = self.read_annotation()
                token_type = self.annotations.get(annotation, TokenType.AT)
                if token_type == TokenType.AT:
                    self.tokens.append(Token(TokenType.AT, '@', start_line, start_column, start_position))
                    # Put back the identifier part
                    for i in range(len(annotation) - 1, 0, -1):
                        self.position -= 1
                        self.column -= 1
                else:
                    self.tokens.append(Token(token_type, annotation, start_line, start_column, start_position))
                continue
            
            # Handle identifiers and keywords
            if char.isalpha() or char == '_':
                identifier = self.read_identifier()
                token_type = self.keywords.get(identifier, TokenType.IDENTIFIER)
                self.tokens.append(Token(token_type, identifier, start_line, start_column, start_position))
                continue
            
            # Handle operators and punctuation
            two_char = char + (self.peek_char() or '')
            
            # Two-character operators
            if two_char in ['==', '!=', '<=', '>=', '&&', '||', '++', '--', 
                           '+=', '-=', '*=', '/=', '%=', '<<', '>>', '->', 
                           '=>', '?.', '??', '?:']:
                if two_char == '==':
                    token_type = TokenType.EQUAL
                elif two_char == '!=':
                    token_type = TokenType.NOT_EQUAL
                elif two_char == '<=':
                    token_type = TokenType.LESS_EQUAL
                elif two_char == '>=':
                    token_type = TokenType.GREATER_EQUAL
                elif two_char == '&&':
                    token_type = TokenType.LOGICAL_AND
                elif two_char == '||':
                    token_type = TokenType.LOGICAL_OR
                elif two_char == '+=':
                    token_type = TokenType.PLUS_ASSIGN
                elif two_char == '-=':
                    token_type = TokenType.MINUS_ASSIGN
                elif two_char == '*=':
                    token_type = TokenType.MULTIPLY_ASSIGN
                elif two_char == '/=':
                    token_type = TokenType.DIVIDE_ASSIGN
                elif two_char == '<<':
                    token_type = TokenType.LEFT_SHIFT
                elif two_char == '>>':
                    token_type = TokenType.RIGHT_SHIFT
                elif two_char == '->':
                    token_type = TokenType.ARROW
                elif two_char == '=>':
                    token_type = TokenType.FAT_ARROW
                elif two_char == '?.':
                    token_type = TokenType.SAFE_CALL
                elif two_char == '??':
                    token_type = TokenType.NULLISH_COALESCING
                elif two_char == '?:':
                    token_type = TokenType.ELVIS
                else:
                    token_type = TokenType.IDENTIFIER  # fallback
                
                self.tokens.append(Token(token_type, two_char, start_line, start_column, start_position))
                self.advance()
                self.advance()
                continue
            
            # Single character tokens
            single_char_tokens = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE,
                '%': TokenType.MODULO,
                '=': TokenType.ASSIGN,
                '<': TokenType.LESS_THAN,
                '>': TokenType.GREATER_THAN,
                '!': TokenType.LOGICAL_NOT,
                '&': TokenType.BITWISE_AND,
                '|': TokenType.BITWISE_OR,
                '^': TokenType.BITWISE_XOR,
                '~': TokenType.BITWISE_NOT,
                '(': TokenType.LEFT_PAREN,
                ')': TokenType.RIGHT_PAREN,
                '{': TokenType.LEFT_BRACE,
                '}': TokenType.RIGHT_BRACE,
                '[': TokenType.LEFT_BRACKET,
                ']': TokenType.RIGHT_BRACKET,
                ';': TokenType.SEMICOLON,
                ',': TokenType.COMMA,
                '.': TokenType.DOT,
                ':': TokenType.COLON,
                '?': TokenType.QUESTION,
                '#': TokenType.HASH_SYMBOL,
                '$': TokenType.DOLLAR,
                '\\': TokenType.BACKSLASH,
            }
            
            if char in single_char_tokens:
                self.tokens.append(Token(single_char_tokens[char], char, start_line, start_column, start_position))
                self.advance()
                continue
            
            # Unknown character
            self.advance()
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column, self.position))
        return self.tokens

if __name__ == "__main__":
    # Test the lexer
    test_code = '''
    @Component
    @Service
    @MLModel(framework: "tensorflow")
    class UserService {
        @Inject
        private userRepository: UserRepository
        
        @Predict
        async getRecommendations(user: User): List<Product> {
            let result = await model.predict(user.features())
            return result.topK(10)
        }
    }
    '''
    
    lexer = NovaLangLexer(test_code)
    tokens = lexer.tokenize()
    
    for token in tokens:
        if token.type != TokenType.NEWLINE and token.type != TokenType.EOF:
            print(f"{token.type.value:20} | {token.value:15} | Line {token.line}, Col {token.column}")