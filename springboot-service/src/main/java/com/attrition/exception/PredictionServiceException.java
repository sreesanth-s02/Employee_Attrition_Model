package com.attrition.exception;

// Thrown when the call to the Python Flask service fails --
// either because it's down, unreachable, or returned an error.
public class PredictionServiceException extends RuntimeException {
    public PredictionServiceException(String message, Throwable cause) {
        super(message, cause);
    }
}