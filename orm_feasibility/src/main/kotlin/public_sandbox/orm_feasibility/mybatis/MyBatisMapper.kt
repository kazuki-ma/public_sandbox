package public_sandbox.orm_feasibility.mybatis

import io.github.oshai.kotlinlogging.KLogger
import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.ibatis.annotations.Mapper
import org.apache.ibatis.annotations.Select
import org.junit.jupiter.api.Test
import org.mybatis.spring.boot.test.autoconfigure.AutoConfigureMybatis
import org.springframework.boot.SpringApplication
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.context.ConfigurableApplicationContext
import public_sandbox.orm_feasibility.mybatis._test_containers.TestContainers

@Mapper
interface MyBatisMapper {
    @Select("SELECT 1")
    fun selectOne(): Int
}

@AutoConfigureMybatis
@SpringBootApplication
open class MybatisApplication {

}

class Benchmark {
    val log: KLogger = KotlinLogging.logger {}

    @Test
    fun benchmark() {
        val container = TestContainers.testContainer()
        val jdbcUrl = container.jdbcUrl

        val ctx: ConfigurableApplicationContext =
            SpringApplication.run(MybatisApplication::class.java, "--spring.datasource.url=jdbc:${jdbcUrl}")

        val mapper = ctx.getBean(MyBatisMapper::class.java)

        log.info { mapper.selectOne() }
    }
}