package com.attrition.service;

import com.attrition.dto.EmployeeInput;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Service
public class PredictionService {

    private final RestTemplate restTemplate;

    // Reads python.service.url from application.properties
    @Value("${python.service.url}")
    private String pythonServiceUrl;

    public PredictionService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public Map callPythonPrediction(EmployeeInput input) {
        // Build the JSON body matching what the Flask /predict endpoint expects
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

        // POST the JSON to the Python service and get the response back as a Map
        return restTemplate.postForObject(pythonServiceUrl, requestBody, Map.class);
    }
}
