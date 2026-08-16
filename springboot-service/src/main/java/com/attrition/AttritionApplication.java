package com.attrition;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.client.RestTemplate;

@SpringBootApplication
public class AttritionApplication {

    public static void main(String[] args) {
        SpringApplication.run(AttritionApplication.class, args);
    }

    // RestTemplate is the tool Spring gives you to make HTTP calls
    // to other services (here, our Python Flask API).
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
