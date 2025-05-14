# FastAPI Project

This is a FastAPI project that provides a RESTful API for managing items. It includes CRUD operations and is structured for scalability and maintainability.

## Installation

1. Clone the repository:

   ``` git
   git clone <repository-url>
   cd fastapi-project
   ```

2. Create a virtual environment:

   ``` git
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:

     ``` git
     venv\Scripts\activate
     ```

   - On macOS/Linux:

     ``` git
     source venv/bin/activate
     ```

4. Install the dependencies:

   ``` git
   pip install -r requirements.txt
   ```

## Usage

To run the FastAPI application, execute the following command:

``` git
python -m uvicorn app.main:app --reload
```

You can access the API documentation at `http://127.0.0.1:8000/docs`.

## Testing

To run the tests, use the following command:

``` git
pytest
```

## License

This project is licensed under the MIT License.
