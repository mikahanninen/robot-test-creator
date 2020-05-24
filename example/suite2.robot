*** Settings ***
Documentation  Created from sheet suite2 of tests.xlsx

*** Test Cases ***
Checking Available Flights
    Open Flights Page
    Check Flights To    Dublin
    Check Flights To    New York

*** Keywords ***
Open Flights Page
	No Operation
Check Flights To
	[Arguments]    ${arg1}
	Log    ${arg1}
