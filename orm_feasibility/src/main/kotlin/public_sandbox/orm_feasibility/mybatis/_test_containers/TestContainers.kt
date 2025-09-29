package public_sandbox.orm_feasibility.mybatis._test_containers

import org.testcontainers.containers.MySQLContainer
import org.testcontainers.utility.DockerImageName

class TestContainers {
    companion object {
        private val container: MySQLContainer<*> = MySQLContainer(DockerImageName.parse("mysql:9.3.0"))
            .withEnv("MYSQL_ALLOW_EMPTY_PASSWORD", "true")
            .withReuse(true)
            .apply {
                start()
            }

        fun testContainer(): MySQLContainer<*> {
            return container
        }
    }
}