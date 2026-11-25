# language: en
Feature: The purchase summary, by pairs

  Scenario: Row 7 · $3,330.00, no coupon, Marta, English
    Given Marta has no coupon applied
    And she has products worth $3,330.00 in her cart
    When she chooses how to pay
    Then the interest-free installments option appears
