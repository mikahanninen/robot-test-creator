*** Settings ***
Documentation  Created from sheet suite1 of tests.xlsx

*** Variables ***
@{LIST_1}    S    M    L

*** Test Cases ***
Adding To Shopping Cart
    Open Shop Page
    Open Product Page    blue shirt
    Add To Shopping Cart     5
    Validate Shopping Cart Contents    blue shirt    5
Check Product Details
    Open Shop Page
    Open Product Page    blue shirt
    Validate Available Sizes    ${LIST_1}

*** Keywords ***
Open Shop Page
	No Operation
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
Validate Available Sizes
	[Arguments]    ${arg1}
	Log    ${arg1}
