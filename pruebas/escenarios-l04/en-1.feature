# language: en
Feature: The path of the order

  Rule: It is canceled as long as the order has not left the warehouse

    Scenario: Delivered × cancels · what already arrived is not canceled
      Given Marta has an order that is delivered
      When she cancels the order
      Then the store tells her that the order has already left the warehouse; it can no longer be canceled
      And the order stays delivered
