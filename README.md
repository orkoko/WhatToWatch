# WhatToWatch

This is a web application that exposes the best things to watch this year. It helps you discover top-rated movies and anime from the last year, allowing you to filter by genres.

## How to Use

Follow these steps to set up and run the application:

### 1. Clone the Repository

Clone this repository to your local machine:

```bash
git clone <repository_url>
cd WhatToWatch
```

### 2. Backend Setup

1.  **Install Requirements:**
    Navigate to the root directory and install the Python dependencies. It is recommended to use a virtual environment.

    ```bash
    pip install -r backend/requirements.txt
    ```

2.  **Configuration:**
    You need to set up your API keys.
    *   Navigate to `backend/config/`.
    *   Copy `config_template.py` to a new file named `config.py`.
    *   Open `backend/config/config.py` and replace the placeholders with your actual API keys:
        *   `TMDB_API_KEY`: Get this from [The Movie Database (TMDB)](https://www.themoviedb.org/documentation/api).
        *   `GOOGLE_API_KEY`: (If used) Get this from Google Cloud Console.

3.  **Run the Backend:**
    From the root directory of the project, run the server:

    ```bash
    python -m backend.server
    ```
    
    Alternatively, if you are in the `backend` directory:
    ```bash
    uvicorn server:app --reload
    ```

    The backend API will be available at `http://localhost:8000`.

### 3. Frontend Setup

1.  **Install Dependencies:**
    Navigate to the `frontend` directory and install the Node.js dependencies:

    ```bash
    cd frontend
    npm install
    ```

2.  **Run the Frontend:**
    Start the React development server:

    ```bash
    npm start
    ```

    The application should open automatically in your browser at `http://localhost:3000`.

### 4. Enjoy!

Make sure both the backend and frontend servers are running. You can now browse the best movies and anime of the year!
