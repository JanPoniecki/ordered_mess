# Storage Scanner

A Django-based application for scanning and organizing storage items using (or not) Google Cloud Vision API.

## Features

- Scan items using camera or upload images
- Automatic text and object detection using Google Cloud Vision API
- Organize items into rooms and containers
- Search functionality for items
- Docker-based deployment

## Prerequisites

- Docker and Docker Compose
- Google Cloud Platform account with Vision API enabled (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/JanPoniecki/ordered_mess.git
cd storage-scanner
```

2. Create a Google Cloud service account and download credentials (optional):
   - Go to Google Cloud Console
   - Create a new project or select an existing one
   - Enable the Cloud Vision API
   - Create a service account and download the JSON key file
   - Rename the downloaded file to `google_credentials.json` and place it in the 'storage_scanner' folder

3. open sample.env file
   - set you ip address
   - set your port (8000 is default)
   - set USE_GOOGLE_VISION to 1 if you want to use google vision
   - save as .env

4. Build and start the containers:
```bash
docker-compose up -d
```

## Usage

1. Access the application at `https://<your ip address>`

2. Create rooms and containers:
   - Go to "Add Room" to create a new room
   - Go to "Add Container" to create containers within rooms

3. Scan items:
   - Use the camera or upload an image
   - The application will automatically detect text and objects
   - Assign the item to a container
   - Add or modify labels as needed

4. Search and browse:
   - Use the search bar to find items by name or content
   - Browse items by room or container
   - View item details and modify information

## Security Notes

- Never commit `google_credentials.json` to version control
- Keep your SSL certificates secure
- Regularly update dependencies
- Use strong passwords for the database and admin accounts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your chosen license] 