plugins {
    id("org.jetbrains.kotlin.jvm")
    id("org.jetbrains.kotlin.plugin.spring")
    id("org.springframework.boot")
    id("io.spring.dependency-management")
    id("me.champeau.jmh") apply false
}

group = "sandbox"
version = "0.0.1-SNAPSHOT"

allprojects {
    repositories {
        mavenCentral()
    }
}

subprojects {
    apply(plugin = "org.jetbrains.kotlin.jvm")
    apply(plugin = "org.jetbrains.kotlin.plugin.spring")
    apply(plugin = "org.springframework.boot")
    apply(plugin = "io.spring.dependency-management")

    kotlin {
        compilerOptions {
            freeCompilerArgs.addAll("-Xjsr305=strict")
        }
    }

    java {
        toolchain {
            languageVersion = JavaLanguageVersion.of(21)
        }
    }

    dependencyManagement {
        imports {
            mavenBom("org.testcontainers:testcontainers-bom:1.20.6")
        }
        dependencies {
            dependency("io.github.oshai:kotlin-logging-jvm:7.0.3")
            dependency("com.mysql:mysql-connector-j:9.2.0")
        }
    }

    dependencies {
        implementation("io.github.oshai:kotlin-logging-jvm")
        implementation("org.jetbrains.kotlin:kotlin-reflect")
        developmentOnly("org.springframework.boot:spring-boot-devtools")
        developmentOnly("org.springframework.boot:spring-boot-docker-compose")
        testImplementation("org.springframework.boot:spring-boot-starter-test")
        testImplementation("org.jetbrains.kotlin:kotlin-test-junit5")
        testRuntimeOnly("org.junit.platform:junit-platform-launcher")
    }
}

subprojects {
    // if JMH Plugin enabled


    tasks.withType<Test> {
        useJUnitPlatform()
    }
}


