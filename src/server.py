import http.server
import socketserver

# Define the port you want to use (e.g., 8000)
PORT = 8000

# Create a SimpleHTTPRequestHandler
Handler = http.server.SimpleHTTPRequestHandler

# Start the HTTP server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Server started at port", PORT)
    try:
        # Open the HTML file in a web browser
        import webbrowser
        webbrowser.open(f'http://localhost:{PORT}/login.php', new=2)

        # Serve the content
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped")
