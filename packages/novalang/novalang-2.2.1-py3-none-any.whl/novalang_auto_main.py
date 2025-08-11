#!/usr/bin/env python3
"""
NovaLang Auto-Main Generator
Automatically creates and injects the main application class like Spring Boot
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List

class NovaLangAutoMain:
    """Generates Spring Boot-like auto-configuration and main class"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.app_name = config.get('name', 'NovaLangApplication').replace('-', '').replace('_', '')
        self.features = config.get('features', [])
        self.databases = config.get('databases', [])
        
    def generate_auto_main(self) -> str:
        """Generate the main application class automatically"""
        
        # Determine annotations based on features
        annotations = ['@SpringBootApplication']
        
        if 'web' in self.features:
            annotations.append('@EnableWebMvc')
        if 'jpa' in self.features or self.databases:
            annotations.append('@EnableJpaRepositories')
        if 'security' in self.features:
            annotations.append('@EnableWebSecurity')
        if 'cache' in self.features:
            annotations.append('@EnableCaching')
        
        # Generate imports based on databases
        database_configs = self.generate_database_config()
        
        # Generate the main class with simplified syntax
        main_class = f'''// Auto-generated NovaLang Application
// This file is automatically created by NovaLang Framework
// Similar to Spring Boot's @SpringBootApplication

@Application
class {self.app_name}Application {{
    
    // Auto-generated REST endpoints
    @GetMapping("/")
    function home(): string {{
        return "🚀 Welcome to {self.config.get('name', 'NovaLang Application')}!";
    }}
    
    @GetMapping("/actuator/health")
    function health(): string {{
        return "UP";
    }}
    
    @GetMapping("/actuator/info")
    function info(): string {{
        return "{self.config.get('name', 'NovaLang Application')} v{self.config.get('version', '1.0.0')}";
    }}
    
    // Auto-generated main method - like Spring Boot
    function main(): void {{
        console.log("");
        console.log("🚀 NovaLang Framework v2.1.0");
        console.log("📦 Application: {self.config.get('name', 'NovaLang Application')}");
        console.log("🎯 Version: {self.config.get('version', '1.0.0')}");
        console.log("✅ Started {self.app_name}Application");
        console.log("🌐 Server running on http://localhost:8080");
        console.log("📡 REST endpoints registered");
        console.log("");
        console.log("📋 Available endpoints:");
        console.log("  GET  /                 - Application home");
        console.log("  GET  /actuator/health  - Health check");
        console.log("  GET  /actuator/info    - Application info");
        console.log("");
        console.log("💡 Application is ready to serve requests!");
    }}
}}'''
        
        return main_class
    
    def generate_auto_configuration(self) -> str:
        """Generate auto-configuration beans"""
        config_beans = []
        
        if 'web' in self.features:
            config_beans.append('''    @Bean
    function webConfig(): WebMvcConfigurer {
        console.log("🌐 Auto-configuring Web MVC...");
        return "WebMvcConfigurer";
    }''')
        
        if self.databases:
            config_beans.append('''    @Bean
    function dataSource(): DataSource {
        console.log("💾 Auto-configuring database connection...");
        return "DataSource";
    }''')
        
        if 'security' in self.features:
            config_beans.append('''    @Bean
    function securityConfig(): SecurityFilterChain {
        console.log("🔐 Auto-configuring security...");
        return "SecurityFilterChain";
    }''')
        
        return '\n\n'.join(config_beans) if config_beans else '    // No additional configuration needed'
    
    def generate_api_endpoints(self) -> str:
        """Generate default API endpoints"""
        return '''    // Auto-generated REST endpoints
    @GetMapping("/")
    function home(): string {
        return "🚀 Welcome to ''' + self.config.get('name', 'NovaLang Application') + '''!";
    }
    
    @GetMapping("/actuator/health")
    function health(): object {
        return {
            "status": "UP",
            "application": "''' + self.config.get('name', 'NovaLang Application') + '''",
            "version": "''' + self.config.get('version', '1.0.0') + '''",
            "framework": "NovaLang 2.1.0"
        };
    }
    
    @GetMapping("/actuator/info")
    function info(): object {
        return {
            "app": {
                "name": "''' + self.config.get('name', 'NovaLang Application') + '''",
                "description": "''' + self.config.get('description', 'NovaLang Application') + '''",
                "version": "''' + self.config.get('version', '1.0.0') + '''"
            },
            "features": ''' + str(self.features).replace("'", '"') + ''',
            "databases": ''' + str(self.databases).replace("'", '"') + '''
        };
    }'''
    
    def generate_database_config(self) -> str:
        """Generate database configuration"""
        if not self.databases:
            return ""
        
        db_config = []
        for db in self.databases:
            if db == 'mysql':
                db_config.append('''    @Configuration
    @EnableJpaRepositories
    function mysqlConfig(): JpaRepository {
        console.log("🐬 Auto-configuring MySQL database...");
        return new MySQLJpaRepository();
    }''')
            elif db == 'postgresql':
                db_config.append('''    @Configuration
    function postgresConfig(): JpaRepository {
        console.log("🐘 Auto-configuring PostgreSQL database...");
        return new PostgreSQLJpaRepository();
    }''')
            elif db == 'mongodb':
                db_config.append('''    @Configuration
    function mongoConfig(): MongoRepository {
        console.log("🍃 Auto-configuring MongoDB database...");
        return new MongoDBRepository();
    }''')
        
        return '\n\n'.join(db_config)
    
    def generate_startup_banner(self) -> str:
        """Generate Spring Boot-like startup banner"""
        return f'''console.log("");
        console.log("  _   _                 _                    ");
        console.log(" | \\\\ | | _____   ____ _| |    __ _ _ __   __ _ ");
        console.log(" |  \\\\| |/ _ \\\\ \\\\ / / _` | |   / _` | '_ \\\\ / _` |");
        console.log(" | |\\\\  | (_) \\\\ V / (_| | |__| (_| | | | | (_| |");
        console.log(" |_| \\\\_|\\\\___/ \\\\_/ \\\\__,_|_____\\\\__,_|_| |_|\\\\__, |");
        console.log("                                        |___/ ");
        console.log("");
        console.log("🚀 NovaLang Framework v2.1.0");
        console.log("📦 Application: {self.config.get('name', 'NovaLang Application')}");
        console.log("🎯 Version: {self.config.get('version', '1.0.0')}");'''
    
    def generate_startup_logs(self) -> str:
        """Generate startup logs"""
        logs = [
            f'console.log("✅ Started {self.app_name}Application");',
            'console.log("🌐 Server running on http://localhost:8080");'
        ]
        
        if self.databases:
            logs.append('console.log("💾 Database connections established");')
        if 'security' in self.features:
            logs.append('console.log("🔐 Security configuration loaded");')
        if 'web' in self.features:
            logs.append('console.log("📡 REST endpoints registered");')
        
        logs.extend([
            'console.log("");',
            'console.log("📋 Available endpoints:");',
            'console.log("  GET  /                 - Application home");',
            'console.log("  GET  /actuator/health  - Health check");',
            'console.log("  GET  /actuator/info    - Application info");',
            'console.log("");',
            'console.log("💡 Application is ready to serve requests!");'
        ])
        
        return '\n        '.join(logs)
    
    def generate_auto_entities(self) -> str:
        """Generate sample entities if JPA is enabled"""
        if 'jpa' not in self.features and not self.databases:
            return ""
        
        return '''
// Auto-generated sample entities
@Entity
@Table(name: "sample_users")
class SampleUser {
    @Id
    @GeneratedValue(strategy: GenerationType.IDENTITY)
    public id: long;
    
    @Column(nullable: false)
    public name: string;
    
    @Column(unique: true)
    public email: string;
    
    function constructor(name: string, email: string) {
        this.name = name;
        this.email = email;
    }
}'''
    
    def generate_auto_repositories(self) -> str:
        """Generate sample repositories if JPA is enabled"""
        if 'jpa' not in self.features and not self.databases:
            return ""
        
        return '''
// Auto-generated repositories
@Repository
interface SampleUserRepository extends JpaRepository<SampleUser, Long> {
    function findByEmail(email: string): SampleUser;
    function findByNameContaining(name: string): SampleUser[];
}'''
    
    def generate_auto_services(self) -> str:
        """Generate sample services"""
        if 'jpa' not in self.features and not self.databases:
            return ""
        
        return '''
// Auto-generated services
@Service
@Component
class SampleUserService {
    
    @Autowired
    private userRepository: SampleUserRepository;
    
    function findAll(): SampleUser[] {
        console.log("📋 Fetching users from auto-configured database...");
        return userRepository.findAll();
    }
    
    function save(user: SampleUser): SampleUser {
        console.log("💾 Saving user: " + user.name);
        return userRepository.save(user);
    }
}'''

def generate_auto_main_file(project_root: Path) -> Path:
    """Generate the auto-main file for a NovaLang project"""
    
    # Load configuration
    config_file = project_root / "nova.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {"name": "NovaLangApplication", "features": ["web"]}
    
    # Generate auto-main
    auto_main = NovaLangAutoMain(config)
    main_content = auto_main.generate_auto_main()
    
    # Write auto-main file
    auto_main_file = project_root / "NovaLangAutoApplication.nova"
    with open(auto_main_file, 'w', encoding='utf-8') as f:
        f.write(main_content)
    
    return auto_main_file

if __name__ == "__main__":
    # Test the auto-main generator
    test_config = {
        "name": "novalang-ecommerce-demo",
        "version": "1.0.0",
        "features": ["web", "jpa", "security"],
        "databases": ["mysql"]
    }
    
    auto_main = NovaLangAutoMain(test_config)
    print("🚀 NovaLang Auto-Main Generator")
    print("=" * 50)
    print(auto_main.generate_auto_main())
