rootProject.name = "demo"

include(":orm_feasibility")
include(":junit_debug_rta")
include(":realtime_api_rtp")

pluginManagement {
    repositories {
        gradlePluginPortal()
    }

    plugins {
        id("org.jetbrains.kotlin.jvm") version "1.9.25"
        id("org.jetbrains.kotlin.plugin.spring") version "1.9.25"
        id("org.springframework.boot") version "3.4.4"
        id("io.spring.dependency-management") version "1.1.7"
        id("me.champeau.jmh") version ("0.7.3") apply false
    }
}
