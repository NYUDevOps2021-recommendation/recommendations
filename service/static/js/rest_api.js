$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        if (!res.is_deleted) {
            $("#id").val(res.id);
            $("#product_origin").val(res.product_origin);
            $("#product_target").val(res.product_target);
            $("#relation").val(res.relation);
            $("#dislike").val(res.dislike);
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#id").val("");
        $("#product_origin").val("");
        $("#product_target").val("");
        $("#relation").val("");
        $("#dislike").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Recommendation
    // ****************************************

    $("#create-btn").click(function () {

        var product_origin = $("#product_origin").val();
        var product_target = $("#product_target").val();
        var relation = $("#relation").val();

        var data = {
            "product_origin": Number(product_origin),
            "product_target": Number(product_target),
            "relation": Number(relation),
            "dislike": 0,
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/recommendations",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Create Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Pet
    // ****************************************

    $("#update-btn").click(function () {

        var id = $("#id").val();
        var product_origin = $("#product_origin").val();
        var product_target = $("#product_target").val();
        var relation = $("#relation").val();

        var data = {
            "product_origin": Number(product_origin),
            "product_target": Number(product_target),
            "relation": Number(relation),
            "dislike": 0,
        };

        var ajax = $.ajax({
            type: "PUT",
            url: "/recommendations/" + id,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_form_data(res)
            flash_message("Update Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Recommendation
    // ****************************************

    $("#retrieve-btn").click(function () {

        var id = $("#id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/recommendations/" + id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())

            update_form_data(res)
            flash_message("Retrieve Success")
        });

        ajax.fail(function (res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Recommendation
    // ****************************************

    $("#delete-btn").click(function () {

        var id = $("#id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/recommendations/" + id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            clear_form_data()
            flash_message("Recommendation has been Deleted!")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Dislike a Recommendation
    // ****************************************

    $("#dislike-btn").click(function () {

        var id = $("#id").val();

        var ajax = $.ajax({
            type: "PUT",
            url: "/recommendations/" + id + "/dislike",
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            flash_message("Dislike Success")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a Recommendation
    // ****************************************

    $("#search-btn").click(function () {

        var product_origin = $("#product_origin").val();
        var product_target = $("#product_target").val();
        var relation = $("#relation").val();

        if (product_target) {
            flash_message("Target Product needs to be empty when using Search")
            return
        }

        var queryString = ""

        if (product_origin) {
            queryString += 'product-id=' + product_origin
        }
        if (relation) {
            if (queryString.length > 0) {
                queryString += '&relation=' + relation
            } else {
                queryString += 'relation=' + relation
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/recommendations?" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            //alert(res.toSource())
            $("#search_results").empty();
            var table = '<table class="table-striped"><thead><tr>'
            table += '<th class="col-md-1">ID</th>'
            table += '<th class="col-md-4">Origin Product</th>'
            table += '<th class="col-md-4">Target Product</th>'
            table += '<th class="col-md-2">Relation</th>'
            table += '<th class="col-md-1">Dislike</th></tr></thead><tbody>'
            var firstRecommendation = ""
            for (var i = 0; i < res.length; i++) {
                var recommendation = res[i];
                if (recommendation.is_deleted) continue

                if (i == 0) {
                    firstRecommendation = recommendation
                }

                if (recommendation.relation == "1")
                    recommendation.relation = "Cross-Sell"
                else if (recommendation.relation == "2")
                    recommendation.relation = "Up-Sell"
                else if (recommendation.relation == "3")
                    recommendation.relation = "Accessory"
                table += "<tr><td style='padding-left: 15px; padding-right: 15px;'>" + recommendation.id +
                    "</td><td style='padding-left: 15px; padding-right: 15px;'>" + recommendation.product_origin +
                    "</td><td style='padding-left: 15px; padding-right: 15px;'>" + recommendation.product_target +
                    "</td><td style='padding-left: 15px; padding-right: 15px;'>" + recommendation.relation +
                    "</td><td style='padding-left: 15px; padding-right: 15px;'>" + recommendation.dislike + "</td></tr>"
                if (recommendation.relation == "Cross-Sell")
                    recommendation.relation = "1"
                else if (recommendation.relation == "Up-Sell")
                    recommendation.relation = "2"
                else if (recommendation.relation == "Accessory")
                    recommendation.relation = "3"
            }
            table += '</tbody></table>'
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstRecommendation != "") {
                update_form_data(firstRecommendation)
            }

            flash_message($("Search Success"))
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Reset
    // ****************************************

    $("#reset-btn").click(function () {

        var ajax = $.ajax({
            type: "DELETE",
            url: "/recommendations/reset",
            contentType: "application/json",
            data: '',
        })

        ajax.done(function (res) {
            flash_message("Reset Success")
        });

        ajax.fail(function (res) {
            flash_message("Server error!")
        });
    });

})
