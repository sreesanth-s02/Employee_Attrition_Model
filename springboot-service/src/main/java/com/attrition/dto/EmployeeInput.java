package com.attrition.dto;

import jakarta.validation.constraints.*;

// Bean Validation annotations here define the rules. Spring checks these
// automatically when the controller method is annotated with @Valid --
// you never call this validation logic yourself.
public class EmployeeInput {

    @Min(value = 18, message = "Age must be at least 18")
    @Max(value = 65, message = "Age must be at most 65")
    private int age;

    @Positive(message = "Monthly income must be a positive number")
    private double monthlyIncome;

    @NotBlank(message = "Department is required")
    @Pattern(
        regexp = "Human Resources|Research & Development|Sales",
        message = "Department must be one of: Human Resources, Research & Development, Sales"
    )
    private String department;

    @NotBlank(message = "Job role is required")
    @Pattern(
        regexp = "Healthcare Representative|Human Resources|Laboratory Technician|Manager|" +
                 "Manufacturing Director|Research Director|Research Scientist|" +
                 "Sales Executive|Sales Representative",
        message = "Job role must be a valid role from the accepted list"
    )
    private String jobRole;

    @NotBlank(message = "OverTime is required")
    @Pattern(regexp = "Yes|No", message = "OverTime must be 'Yes' or 'No'")
    private String overTime;

    @Min(value = 0, message = "Distance from home cannot be negative")
    @Max(value = 100, message = "Distance from home seems unrealistic (max 100)")
    private int distanceFromHome;

    @NotBlank(message = "Marital status is required")
    @Pattern(
        regexp = "Divorced|Married|Single",
        message = "Marital status must be one of: Divorced, Married, Single"
    )
    private String maritalStatus;

    @NotBlank(message = "Gender is required")
    @Pattern(regexp = "Female|Male", message = "Gender must be 'Female' or 'Male'")
    private String gender;

    @Min(value = 0, message = "Total working years cannot be negative")
    @Max(value = 50, message = "Total working years seems unrealistic (max 50)")
    private int totalWorkingYears;

    @Min(value = 0, message = "Years at company cannot be negative")
    @Max(value = 50, message = "Years at company seems unrealistic (max 50)")
    private int yearsAtCompany;

    public EmployeeInput() {
    }

    public int getAge() { return age; }
    public void setAge(int age) { this.age = age; }

    public double getMonthlyIncome() { return monthlyIncome; }
    public void setMonthlyIncome(double monthlyIncome) { this.monthlyIncome = monthlyIncome; }

    public String getDepartment() { return department; }
    public void setDepartment(String department) { this.department = department; }

    public String getJobRole() { return jobRole; }
    public void setJobRole(String jobRole) { this.jobRole = jobRole; }

    public String getOverTime() { return overTime; }
    public void setOverTime(String overTime) { this.overTime = overTime; }

    public int getDistanceFromHome() { return distanceFromHome; }
    public void setDistanceFromHome(int distanceFromHome) { this.distanceFromHome = distanceFromHome; }

    public String getMaritalStatus() { return maritalStatus; }
    public void setMaritalStatus(String maritalStatus) { this.maritalStatus = maritalStatus; }

    public String getGender() { return gender; }
    public void setGender(String gender) { this.gender = gender; }

    public int getTotalWorkingYears() { return totalWorkingYears; }
    public void setTotalWorkingYears(int totalWorkingYears) { this.totalWorkingYears = totalWorkingYears; }

    public int getYearsAtCompany() { return yearsAtCompany; }
    public void setYearsAtCompany(int yearsAtCompany) { this.yearsAtCompany = yearsAtCompany; }
}