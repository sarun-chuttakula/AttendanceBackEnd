<?php
if ($_SERVER["REQUEST_METHOD"] === "POST") {
    // Define the Flask server URL
    $flaskServerUrl = "http://localhost:4000";

    // Prepare the login data
    $loginData = array(
        "email" => $_POST["email"],
        "password" => $_POST["password"]
    );

    // Set the HTTP request headers
    $headers = array(
        "Content-Type: application/json"
    );

    // Create a new cURL resource
    $ch = curl_init();

    // Set the cURL options
    curl_setopt($ch, CURLOPT_URL, $flaskServerUrl . "/login");
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($loginData));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

    // Execute the cURL request and store the response
    $response = curl_exec($ch);

    // Close cURL resource
    curl_close($ch);

    // Parse the JSON response
    $responseData = json_decode($response, true);

    // Check if the login was successful
    if (isset($responseData["access_token"])) {
        // Redirect to the dashboard or perform other actions
        header("Location: dashboard.php");
        exit;
    } else {
        // Handle login error
        echo '<p style="color: red;">Invalid email or password. Please try again.</p>';
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
</head>
<body>
    <h1>Login</h1>
    <form method="post" action="login.php">
        <label for="email">Email:</label>
        <input type="email" id="email" name="email" required /><br /><br />

        <label for="password">Password:</label>
        <input type="password" id="password" name="password" required /><br /><br />

        <button type="submit">Login</button>
    </form>
</body>
</html>
