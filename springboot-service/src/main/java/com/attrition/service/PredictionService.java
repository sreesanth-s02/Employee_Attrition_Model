package com.attrition.service;

import com.attrition.dto.EmployeeInput;
import com.attrition.exception.PredictionServiceException;
import com.attrition.exception.UpstreamValidationException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Service
public class PredictionService {

    private final RestTemplate restTemplate;

    @Value("${python.service.url}")
    private String pythonServiceUrl;

    public PredictionService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public Map callPythonPrediction(EmployeeInput input) {
        Map<String, Object> requestBody = Map.of(
                "Age", input.getAge(),
                "MonthlyIncome", input.getMonthlyIncome(),
                "Department", input.getDepartment(),
                "JobRole", input.getJobRole(),
                "OverTime", input.getOverTime(),
                "DistanceFromHome", input.getDistanceFromHome(),
                "MaritalStatus", input.getMaritalStatus(),
                "Gender", input.getGender(),
                "TotalWorkingYears", input.getTotalWorkingYears(),
                "YearsAtCompany", input.getYearsAtCompany()
        );

        try {
            return restTemplate.postForObject(pythonServiceUrl, requestBody, Map.class);

        } catch (HttpClientErrorException e) {
            // Flask responded with a 4xx -- meaning it reached Flask fine,
            // but Flask rejected the data itself (its own validation caught
            // something). This is a client error (bad input), not a service
            // outage, so it should map to 400, not 503.
            throw new UpstreamValidationException(
                    "The prediction service rejected this input: " + e.getResponseBodyAsString(), e
            );

        } catch (RestClientException e) {
            // Covers: connection refused (Flask not running), timeouts,
            // 5xx from Flask, or malformed responses. This really is
            // "the service is unavailable."
            throw new PredictionServiceException(
                    "Could not get a prediction from the ML service. Is it running?", e
            );
        }
    }
}