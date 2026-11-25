# language: en
Feature: The path of the order

  Rule: It is canceled as long as the order has not left the warehouse

    Scenario: Paid × cancels · it is canceled and what was charged is refunded
      Given Marta has an order that is paid
      When she cancels the order
      Then the order becomes canceled
      And they refund $432.00 to her card

    Scenario: In warehouse × cancels · it can still be done
      Given Marta has an order that is in warehouse
      When she cancels the order
      Then the order becomes canceled
      And they refund $432.00 to her card

    Scenario: Shipped × cancels · it already left the warehouse
      Given Marta has an order that is shipped
      When she cancels the order
      Then the store tells her that the order has already left the warehouse; it can no longer be canceled
      And the order stays shipped

  Rule: An order is paid only once

    Scenario: Canceled × pays · what is canceled is not charged
      Given Marta has an order that is canceled
      When she tries to pay the order
      Then the store tells her that this order can no longer be paid: it is «canceled»
      And the order stays canceled
