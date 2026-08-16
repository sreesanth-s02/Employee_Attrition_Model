package com.attrition.controller;

import com.attrition.dto.EmployeeInput;
import com.attrition.service.PredictionService;
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

    // Spring calls this method automatically whenever a POST request
    // hits /api/predict — this is the "framework calls you" idea in action.
    @PostMapping("/api/predict")
    public Map predict(@RequestBody EmployeeInput input) {
        return predictionService.callPythonPrediction(input);
    }
}
