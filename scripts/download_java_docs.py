"""script para descargar documentación java real"""
import requests
from pathlib import Path
import time

def download_spring_docs():
    """descargar documentación básica de spring"""
    docs_dir = Path("data/raw/spring_docs")
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # contenido de docu de spring esto es simulado para demoo
    spring_docs = {
        "spring_boot_getting_started.txt": """
Spring Boot Getting Started Guide

Spring Boot makes it easy to create stand-alone, production-grade Spring based applications that you can "just run".

We take an opinionated view of the Spring platform and third-party libraries so you can get started with minimum fuss. Most Spring Boot applications need minimal Spring configuration.

Features:
- Create stand-alone Spring applications
- Embed Tomcat, Jetty or Undertow directly (no need to deploy WAR files)
- Provide opinionated 'starter' dependencies to simplify your build configuration
- Automatically configure Spring and 3rd party libraries whenever possible
- Provide production-ready features such as metrics, health checks, and externalized configuration
- Absolutely no code generation and no requirement for XML configuration

System Requirements:
Spring Boot 3.1.5 requires Java 17 and is compatible up to and including Java 21. Spring Framework 6.0.13 or above is also required.

Maven 3.6.3 or later
Gradle 7.5 or later
        """,
        
        "spring_web_mvc.txt": """
Spring Web MVC Framework

Spring Web MVC is the original web framework built on the Servlet API and has been included in the Spring Framework from the very beginning. The formal name, "Spring Web MVC," comes from the name of its source module (spring-webmvc), but it is more commonly known as "Spring MVC".

DispatcherServlet:
Like many other web frameworks, Spring MVC is designed around the front controller pattern where a central Servlet, the DispatcherServlet, provides a shared algorithm for request processing, while actual work is performed by configurable delegate components.

Controller Methods:
@Controller classes use @RequestMapping annotations to express request mappings, request input, exception handling, and more.

@RestController:
@RestController is a composed annotation that is itself meta-annotated with @Controller and @ResponseBody to indicate a controller whose every method inherits the type-level @ResponseBody annotation.

Request Mapping:
You can use the @RequestMapping annotation to map requests to controllers methods. It has various attributes to match by URL, HTTP method, request parameters, headers, and media types.
        """,
        
        "spring_data_jpa.txt": """
Spring Data JPA Reference

Spring Data JPA, part of the larger Spring Data family, makes it easy to easily implement JPA based repositories. This module deals with enhanced support for JPA based data access layers.

Key Features:
- Sophisticated support for building repositories based on Spring and JPA
- Support for QueryDSL predicates and thus type-safe JPA queries
- Transparent auditing of domain class
- Pagination support, dynamic query execution, ability to integrate custom data access code
- Validation of @Query annotated queries at bootstrap time
- Support for XML based entity mapping
- JavaConfig based repository configuration by introducing @EnableJpaRepositories

Repository Interface:
The central interface in the Spring Data repository abstraction is Repository. It takes the domain class to manage as well as the ID type of the domain class as type arguments.

@Entity
public class User {
    @Id
    @GeneratedValue
    private Long id;
    private String firstname;
    private String lastname;
    private String email;
}

public interface UserRepository extends JpaRepository<User, Long> {
    List<User> findByLastname(String lastname);
    List<User> findByFirstnameAndLastname(String firstname, String lastname);
}
        """,
        
        "spring_security.txt": """
Spring Security Reference

Spring Security is a framework that focuses on providing both authentication and authorization to Java applications. Like all Spring projects, the real power of Spring Security is found in how easily it can be extended to meet custom requirements.

Authentication:
Authentication is how we verify the identity of who is trying to access a particular resource. A common way to authenticate users is by requiring the user to enter a username and password.

Authorization:
Authorization refers to the process of determining whether a user has proper permission to perform a particular action or read particular data.

Basic Configuration:
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public UserDetailsService userDetailsService() {
        InMemoryUserDetailsManager manager = new InMemoryUserDetailsManager();
        manager.createUser(User.withDefaultPasswordEncoder()
            .username("user")
            .password("password")
            .roles("USER")
            .build());
        return manager;
    }
}

Method Security:
Spring Security provides comprehensive support for method-level security through the use of annotations like @PreAuthorize, @PostAuthorize, @Secured, and others.
        """,
        
        "microservices_with_spring.txt": """
Microservices with Spring Boot and Spring Cloud

Microservices architecture is an approach to developing a single application as a suite of small services, each running in its own process and communicating with lightweight mechanisms.

Spring Cloud:
Spring Cloud provides tools for developers to quickly build some of the common patterns in distributed systems (e.g. configuration management, service discovery, circuit breakers, intelligent routing, micro-proxy, control bus, one-time tokens, global locks, leadership election, distributed sessions, cluster state).

Service Discovery:
Service discovery is one of the key tenets of a microservice-based architecture. Netflix Eureka is a REST-based service that is primarily used in the AWS cloud for locating services.

@EnableEurekaServer
@SpringBootApplication
public class EurekaServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(EurekaServerApplication.class, args);
    }
}

Configuration Management:
Spring Cloud Config provides server-side and client-side support for externalized configuration in a distributed system.

Circuit Breaker:
The circuit breaker pattern prevents cascading failures in distributed systems by monitoring for failures and automatically switching to a fallback mechanism.

@Component
public class BookService {
    
    @HystrixCommand(fallbackMethod = "reliable")
    public String readingList() {
        URI uri = URI.create("http://bookrecommendation-service/recommended");
        return this.restTemplate.getForObject(uri, String.class);
    }
    
    public String reliable() {
        return "Cloud Native Java (O'Reilly)";
    }
}
        """
    }
    
    print("Descargando documentación de Spring...")
    for filename, content in spring_docs.items():
        file_path = docs_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"Creado: {filename}")
        time.sleep(0.1)  # pequeña pausa
    
    print(f"Descargados {len(spring_docs)} documentos en {docs_dir}")
    return docs_dir

if __name__ == "__main__":
    download_spring_docs()
