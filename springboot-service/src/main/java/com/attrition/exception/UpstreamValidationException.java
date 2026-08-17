package com.attrition.exception;

// Thrown when the Python service reaches successfully but rejects
// the input as invalid (a 4xx response) -- distinct from
// PredictionServiceException, which means Flask was unreachable.
public class UpstreamValidationException extends RuntimeException {
    public UpstreamValidationException(String message, Throwable cause) {
        super(message, cause);
    }
}