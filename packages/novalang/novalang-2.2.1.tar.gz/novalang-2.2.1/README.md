# NovaLang 🚀 - Universal Programming Language with Complete Database Support

[![PyPI version](https://badge.fury.io/py/novalang.svg)](https://badge.fury.io/py/novalang)
[![Python Support](https://img.shields.io/pypi/pyversions/novalang.svg)](https://pypi.org/project/novalang/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/novalang.svg)](https://pypi.org/project/novalang/)

**NovaLang** is the world's most comprehensive programming language with **universal database support** and **enhanced parser** for Spring Boot-style development. Supporting **70+ database types** from SQL to NoSQL, Graph to Vector databases, and everything in between.

## 🎉 **NEW in v2.2.0: Enhanced Parser & AUTO_MYSQL_BACKEND**

- ✅ **Fixed Parser Issues**: All syntax now compiles successfully
- ✅ **Spring Boot-Style Syntax**: Create backends with familiar patterns  
- ✅ **AUTO_MYSQL_BACKEND**: Complete guide for automatic MySQL setup
- ✅ **Hybrid Parser**: Supports both basic and advanced syntax
- ✅ **Zero Build Errors**: Robust error handling and recovery

## 🌟 Key Features

### 🗄️ **Universal Database Support (70+ Databases)**
- **SQL Databases**: MySQL, PostgreSQL, Oracle, SQL Server, SQLite, MariaDB, DB2, and 15+ more
- **NoSQL Databases**: MongoDB, Cassandra, DynamoDB, CouchDB, HBase, and 10+ more  
- **Graph Databases**: Neo4j, ArangoDB, JanusGraph, TigerGraph, Amazon Neptune
- **Time Series**: InfluxDB, TimescaleDB, Prometheus, Graphite, QuestDB
- **Search Engines**: Elasticsearch, Solr, Lucene, Sphinx
- **Vector/AI Databases**: Pinecone, Weaviate, Milvus, Qdrant, Chroma, Faiss
- **Cache/In-Memory**: Redis, Memcached, Hazelcast, Caffeine, Ignite
- **Blockchain Databases**: BigchainDB, Bluzelle
- **Multi-Model**: CosmosDB, Fauna, SurrealDB, EdgeDB

### 🏗️ **Enterprise Features**
- **Multi-Target Compilation**: Java/JVM, TypeScript, and more
- **Advanced Type System**: Generics, Unions, Optional types, Result types
- **Microservices**: Service discovery, load balancing, circuit breakers
- **Cloud-Native**: Kubernetes deployment, Docker integration
- **AI/ML Integration**: TensorFlow, PyTorch, HuggingFace models
- **Blockchain Support**: Smart contracts, DeFi protocols, NFTs
- **Security**: OAuth2, JWT, WebAuthn, SAML2, encryption

### 🛠️ **Development Tools**
- **CLI Tool**: Complete project lifecycle management
- **Advanced Parser**: Full AST generation with error recovery
- **Code Generation**: Multi-target backend compilation
- **Project Templates**: Ready-to-use enterprise project structures

## 🚀 Quick Start

### Installation

```bash
# Install NovaLang
pip install novalang

# Install with database drivers
pip install novalang[database]

# Install development tools
pip install novalang[dev]

# Install everything
pip install novalang[all]
```

### Your First NovaLang Program

```nova
// Universal Database Example
@MySQL
@PostgreSQL
@MongoDB
@Redis
@Service
class UserService {
    @Autowired
    @MySQL
    private mysqlRepo: MySQLUserRepository
    
    @Autowired
    @MongoDB
    private mongoRepo: MongoUserRepository
    
    @Autowired
    @Redis
    private cache: RedisTemplate
    
    @CRUD
    @Transactional
    public createUser(user: User): Result<User> {
        // Save to MySQL
        let savedUser = mysqlRepo.save(user)
        
        // Index in MongoDB for search
        mongoRepo.index(savedUser)
        
        // Cache in Redis
        cache.set(f"user:{savedUser.id}", savedUser, ttl: 3600)
        
        return Success(savedUser)
    }
    
    @Query
    @Cached
    public searchUsers(query: String): List<User> {
        return mongoRepo.search(query)
    }
}
```

### CLI Usage

```bash
# Create new project
nova init my-project --template enterprise

# Build project
nova build

# Run project
nova run

# Test project
nova test

# Deploy to cloud
nova deploy --target kubernetes
```

## 📊 Database Examples

### SQL Databases
```nova
@MySQL
@Entity
@Table(name: "users")
class User {
    @Id
    @GeneratedValue
    private id: Long
    
    @Column(unique: true)
    private email: String
    
    @OneToMany
    private orders: List<Order>
}
```

### NoSQL Databases
```nova
@MongoDB
@Document(collection: "products")
class Product {
    @Id
    private id: String
    
    @Field("name")
    @Indexed
    private name: String
    
    @Field("tags")
    private tags: List<String>
}
```

### Graph Databases
```nova
@Neo4j
@Node("Person")
class Person {
    @Id
    private id: String
    
    @Property("name")
    private name: String
    
    @Relationship(type: "KNOWS", direction: "OUTGOING")
    private friends: List<Person>
}
```

### Time Series Databases
```nova
@InfluxDB
@Measurement("sensor_data")
class SensorReading {
    @Time
    private timestamp: Instant
    
    @Tag("sensor_id")
    private sensorId: String
    
    @Field("temperature")
    private temperature: Double
}
```

### Vector Databases (AI/ML)
```nova
@Pinecone
@VectorIndex(dimension: 768)
class DocumentEmbedding {
    @Id
    private id: String
    
    @Vector
    private embedding: Float[]
    
    @Metadata
    private content: String
}
```

## 🏗️ Architecture

NovaLang follows a modular architecture:

```
NovaLang
├── Lexer (70+ database annotations)
├── Parser (Advanced AST generation)
├── Compiler (Multi-target code generation)
├── Runtime (Universal database connectivity)
└── CLI (Project lifecycle management)
```

## 🌐 Multi-Target Compilation

NovaLang compiles to multiple targets:

### Java/JVM
```bash
nova compile --target java
# Generates enterprise Java with Spring Boot integration
```

### TypeScript
```bash
nova compile --target typescript  
# Generates TypeScript with Node.js/Express integration
```

## 🔧 Database Configuration

NovaLang automatically configures database connections:

```nova
// application.nova
@Configuration
class DatabaseConfig {
    @MySQL
    @DataSource
    private mysql: DataSource = {
        url: "jdbc:mysql://localhost:3306/mydb",
        username: "${DB_USER}",
        password: "${DB_PASSWORD}"
    }
    
    @MongoDB  
    @MongoTemplate
    private mongo: MongoTemplate = {
        uri: "mongodb://localhost:27017/mydb"
    }
    
    @Redis
    @RedisTemplate
    private redis: RedisTemplate = {
        host: "localhost",
        port: 6379
    }
}
```

## 🚀 Deployment

### Kubernetes
```bash
nova deploy --target kubernetes --namespace production
```

### Docker
```bash
nova build --containerize
docker run novalang/my-app
```

### Cloud Platforms
```bash
nova deploy --target aws-lambda
nova deploy --target azure-functions
nova deploy --target google-cloud-run
```

## 📈 Performance

NovaLang is optimized for performance:

- **JIT Compilation**: Runtime optimization
- **Connection Pooling**: Efficient database connections  
- **Caching**: Multi-level caching strategies
- **Parallel Processing**: Concurrent database operations
- **Memory Optimization**: Zero-copy operations where possible

## 🧪 Testing

```nova
@Test
class UserServiceTest {
    @Mock
    private userRepository: UserRepository
    
    @InjectMocks  
    private userService: UserService
    
    @Test
    public testCreateUser() {
        // Given
        let user = User(email: "test@example.com")
        
        // When
        let result = userService.createUser(user)
        
        // Then
        assert result.isSuccess()
        assert result.get().id != null
    }
}
```

## 📚 Documentation

- **[Language Reference](docs/language-reference.md)**: Complete language syntax
- **[Database Guide](docs/database-guide.md)**: Database integration examples  
- **[API Documentation](docs/api-reference.md)**: Complete API reference
- **[Examples](examples/)**: Real-world examples and tutorials

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

NovaLang is released under the [MIT License](LICENSE).

## 🏆 Why NovaLang?

| Feature | NovaLang | Java | Python | TypeScript |
|---------|----------|------|--------|------------|
| Database Types | 70+ | 20+ | 30+ | 25+ |
| Multi-Target | ✅ | ❌ | ❌ | ❌ |
| Type Safety | ✅ | ✅ | ❌ | ✅ |
| Enterprise Ready | ✅ | ✅ | ❌ | ❌ |
| AI/ML Integration | ✅ | ❌ | ✅ | ❌ |
| Blockchain Support | ✅ | ❌ | ❌ | ❌ |
| Cloud Native | ✅ | ❌ | ❌ | ❌ |

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=martinmaboya/novalang&type=Date)](https://star-history.com/#martinmaboya/novalang&Date)

---

**Made with ❤️ by [Martin Maboya](https://github.com/martinmaboya)**

**NovaLang - One Language, All Databases, Every Platform** 🚀
