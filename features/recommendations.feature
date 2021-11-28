Feature: The store service back-end
  As a service provider
  I need a RESTful catalog service
  so that I can keep track of all the recommendations
  
Background:
  Given the following recommendations
        | id | product_origin | product_target | relation | dislike | is_deleted |
        | 1  |       1        |       2        |     1    |    0    |      0     |
        | 2  |       2        |       3        |     2    |    1    |      0     |
        | 3  |       9        |       10       |     3    |    2    |      1     |
        
Scenario: The server is running
  When I visit the "Home Page"
  Then I should see "Recommendation RESTful Service" in the title
  And I should not see "404 Not Found"
  
 Scenario: Update a Recommendation
    When I visit the "Home Page"
    And I set the "id" to "1"
    And I press the "Search" button
    Then I should see "1" in the "id" field
    And I should see "1" in the "product_origin" field
    And I should see "2" in the "product_target" field
    And I should see "1" in the "relation" field
    When I change "relation" to "2"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Clear" button
    And I paste in the "id" field
    And I press the "Retrieve" button
    Then I should see "2" in the "relation" field
