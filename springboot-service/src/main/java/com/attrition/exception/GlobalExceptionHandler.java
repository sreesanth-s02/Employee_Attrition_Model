package com.attrition.exception;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

// @RestControllerAdvice makes this class a global "safety net" -- Spring
// routes ANY exception thrown from ANY controller through the matching
// @ExceptionHandler method here, instead of letting it become a raw 500.
@RestControllerAdvice
public class GlobalExceptionHandler {

    // Triggered automatically when @Valid finds a rule violation
    // in EmployeeInput (e.g. age too low, invalid department string).
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidationErrors(MethodArgumentNotValidException ex) {
        Map<String, String> fieldErrors = new HashMap<>();
        ex.getBindingResult().getFieldErrors().forEach(error ->
                fieldErrors.put(error.getField(), error.getDefaultMessage())
        );

        Map<String, Object> body = new HashMap<>();
        body.put("timestamp", Instant.now().toString());
        body.put("status", 400);
        body.put("error", "Validation failed");
        body.put("fieldErrors", fieldErrors);

        return ResponseEntity.badRequest().body(body);
    }

    // Triggered when Flask received the request but rejected the data
    // itself (its own validation caught something) -- a client error,
    // not a service outage.
    @ExceptionHandler(UpstreamValidationException.class)
    public ResponseEntity<Map<String, Object>> handleUpstreamValidation(UpstreamValidationException ex) {
        Map<String, Object> body = new HashMap<>();
        body.put("timestamp", Instant.now().toString());
        body.put("status", 400);
        body.put("error", "Invalid input");
        body.put("message", ex.getMessage());

        return ResponseEntity.badRequest().body(body);
    }

    // Triggered when PredictionService can't reach or gets an error
    // from the Python service (Flask down, timeout, bad response, etc.)
    @ExceptionHandler(PredictionServiceException.class)
    public ResponseEntity<Map<String, Object>> handlePredictionServiceError(PredictionServiceException ex) {
        Map<String, Object> body = new HashMap<>();
        body.put("timestamp", Instant.now().toString());
        body.put("status", 503);
        body.put("error", "Prediction service unavailable");
        body.put("message", ex.getMessage());

        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(body);
    }

    // Catch-all safety net for anything unexpected we didn't plan for
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleUnexpectedError(Exception ex) {
        Map<String, Object> body = new HashMap<>();
        body.put("timestamp", Instant.now().toString());
        body.put("status", 500);
        body.put("error", "Unexpected server error");
        body.put("message", ex.getMessage());

        return ResponseEntity.internalServerError().body(body);
    }
}