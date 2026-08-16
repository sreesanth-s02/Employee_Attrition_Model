package com.attrition.dto;

// This is the "shape" of the JSON the user sends in.
// Matches the 10 essential fields your Python service expects.
public class EmployeeInput {

    private int age;
    private double monthlyIncome;
    private String department;
    private String jobRole;
    private String overTime;
    private int distanceFromHome;
    private String maritalStatus;
    private String gender;
    private int totalWorkingYears;
    private int yearsAtCompany;

    public EmployeeInput() {
        // Spring needs a no-argument constructor to build this
        // object automatically from incoming JSON.
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
