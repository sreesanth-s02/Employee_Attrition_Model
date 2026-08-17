package com.attrition.controller;

import com.attrition.dto.EmployeeInput;
import com.attrition.service.PredictionService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class PredictionController {

    private final PredictionService predictionService;

    public PredictionController(PredictionService predictionService) {
        this.predictionService = predictionService;
    }

    // @Valid tells Spring: run every validation rule defined in EmployeeInput
    // BEFORE this method body executes. If any rule fails, Spring throws
    // MethodArgumentNotValidException automatically -- this method never runs,
    // and GlobalExceptionHandler catches it and returns a clean 400 response.
    @PostMapping("/api/predict")
    public Map predict(@Valid @RequestBody EmployeeInput input) {
        return predictionService.callPythonPrediction(input);
    }
}