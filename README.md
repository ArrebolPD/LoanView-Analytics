## 📈 LoanView Analytics: Interactive Visualization Platform (Django + D3.js)

This project is a sophisticated web application that integrates the **Django** framework (Python) with the **D3.js** library to provide powerful and interactive visualization of processed loan data.

### 🌟 Project Overview

The core purpose of this application is to transform processed financial data into meaningful visual insights. It utilizes a full-stack approach:

1.  **Backend (Django):** Handles the data ingestion, serving, and web application logic.
2.  **Visualization (D3.js):** Renders complex, dynamic, and interactive charts based on the processed loan data.

This platform, **LoanView Analytics**, serves as a powerful dashboard for analyzing trends and patterns within lending data.

### ✨ Key Features

* **Financial Data Visualization:** Focuses on visualizing **processed loan data** from the `Loan_Data_Processed.csv` file.
* **Full-Stack Integration:** Demonstrates a clean separation of concerns with a Django backend (`manage.py`, `db.sqlite3`) and D3.js frontend logic.
* **Dedicated Applications:** Includes the `d3app` and the project folder (`DV115`), suggesting modular and well-structured application components.
* **Embedded Visualization:** The core visualization is embedded within the `templates/d3app/visualization.html` file, which fetches data served by Django views.
* **Processed Data:** The use of `Loan_Data_Processed.csv` indicates the data has been cleaned or transformed prior to loading into the system.

### 🛠️ Technologies Used

* **Backend:** Python, **Django**
* **Frontend:** HTML5, CSS, JavaScript, **D3.js**
* **Database:** SQLite (`db.sqlite3`)
* **Data Source:** Processed CSV file (`Loan_Data_Processed.csv`)

### 🚀 Getting Started

Follow these instructions to set up and run the project locally.

1.  **Clone the repository:**
    ```bash
    git clone [LINK_TO_YOUR_REPOSITORY] 
    # Use the appropriate clone link for your current DV-115 project
    ```
2.  **Navigate to the project directory:**
    ```bash
    cd DV-115
    ```
3.  **Setup Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate     # On Windows
    ```
4.  **Install Dependencies:** (Ensure you install Django and any other necessary packages)
    ```bash
    pip install django
    # If a requirements.txt file exists, use: pip install -r requirements.txt
    ```
5.  **Initialize Database (if needed):**
    ```bash
    python manage.py migrate
    ```
6.  **Run the Django Server:**
    ```bash
    python manage.py runserver
    ```
7.  **Access the Application:** Open your browser and navigate to the appropriate visualization URL (typically `http://127.0.0.1:8000/` or a specific path defined in the Django settings).

### 📂 Repository Structure

The visualizations are organized within the following file structure:

### 📂 Repository Structure

The visualizations are organized within the following file structure:

```
DV-115/
├── DV115/                   # Main Django Project folder (settings/urls/wsgi)
├── d3app/                   # Core Django Application for visualization logic
├── templates/
│   └── d3app/
│       └── visualization.html # HTML template embedding the D3.js visualizations
├── .gitattributes           # Git configuration file
├── Loan_Data_Processed.csv  # Processed data file used for visualization
├── db.sqlite3               # SQLite Database (for persistent data storage)
└── manage.py                # Django's command-line utility
```
### 🤝 Contributing

Contributions, issues, and feature requests are welcome!

### 📄 License

Distributed under the **MIT License**.

### 📬 Contact

Project Link: [https://github.com/ArrebolPD/DV-115](https://github.com/ArrebolPD/LoanView-Analytics)
