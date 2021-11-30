Feature: The recommendation store service back-end
  As a service provider
  I need a RESTful catalog service
  so that I can keep track of all the recommendations

  Background:
    Given the following recommendations
      | product_origin | product_target | relation | dislike | is_deleted |
      | 1              | 2              | 1        | 0       | 0          |
      | 2              | 3              | 2        | 1       | 0          |
      | 9              | 10             | 3        | 2       | 1          |

  Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Recommendation RESTful Service" in the title
    And I should not see "404 Not Found"

  Scenario: Create a Recommendation
    When I visit the "Home Page"
    And I set the "product_origin" to "3"
    And I set the "product_target" to "4"
    And I select "Cross-Sell" in the "relation" dropdown
    And I press the "Create" button
    Then I should see the message "Create Success"
    When I copy the "id" field
    And I press the "Clear" button
    Then the "id" field should be empty
    And the "product_origin" field should be empty
    And the "product_target" field should be empty
    And the "relation" field should be empty
    When I paste the "id" field
    And I press the "Retrieve" button
    Then I should see "3" in the "product_origin" field
    And I should see "4" in the "product_target" field
    And I should see "Cross-Sell" in the "relation" dropdown

  Scenario: Update a Recommendation
    When I visit the "Home Page"
    And I set the "product_origin" to "1"
    And I select "Cross-Sell" in the "relation" dropdown
    And I press the "Search" button
    Then I should see "1" in the "product_origin" field
    And I should see "2" in the "product_target" field
    And I should see "Cross-Sell" in the "relation" dropdown
    When I select "Up-Sell" in the "relation" dropdown
    And I press the "Update" button
    Then I should see the message "Update Success"
    When I copy the "id" field
    And I press the "Clear" button
    And I paste the "id" field
    And I press the "Retrieve" button
    Then I should see "1" in the "product_origin" field
    And I should see "2" in the "product_target" field
    And I should see "Up-Sell" in the "relation" dropdown
    When I press the "Clear" button
    And I press the "Search" button
    Then I should not see "Cross-Sell" in the results

  Scenario: List all Recommendations
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "Cross-Sell" in the results
    And I should see "Up-Sell" in the results
    And I should not see "Accessory" in the results

