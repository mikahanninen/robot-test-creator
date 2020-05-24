*** Settings ***
Documentation  Created from sheet suite2 of tests.xlsx

*** Test Cases ***
Checking Available Flights
    Open Product Page    blue shirt
    Add To Shopping Cart     5
    Validate Shopping Cart Contents    blue shirt    5

*** Keywords ***
Open Product Page
	[Arguments]    ${arg1}
	Log    ${arg1}
Add To Shopping Cart 
	[Arguments]    ${arg1}
	Log    ${arg1}
Validate Shopping Cart Contents
	[Arguments]    ${arg1}    ${arg2}
	Log    ${arg1}
	Log    ${arg2}
