# Shared Library Approach in Microservices  

## Why Use a Shared Library?  

In a microservices architecture, multiple services often need **common functionalities** such as logging, error handling, authentication, and utility functions. Instead of duplicating code across services, we use a **shared library** to:  

**Reduce Code Duplication** : Avoid repeating the same logic in every service.  
**Ensure Consistency** : Standardized utilities across all services.  
**Simplify Maintenance** : Fix issues or update features in one place.  
**Improve Scalability** : Microservices remain lightweight and focused.  
**Enhance Deployment** : Easier to manage updates and dependencies.  


## Installation  

To install the shared library in your microservices, run:  

```sh
pip install shared-utils
```

Or specify it in your `requirements.txt`:  

```
shared-utils>=1.0.0
```

## Usage  

Inside any microservice, import and use the shared utilities:  

```python
from shared_utils.logging import setup_logger

logger = setup_logger(__name__)
logger.info("Shared utilities are working!")
```

## Updating `shared_utils`
If a new feature or bug fix is added to `shared_utils`, follow these steps:

1. **Modify the code**: Implement your changes in `shared_utils`.
2. **Update version**: Change the version in `setup.py` (e.g., `1.0.1` to `1.0.2`).
3. **Build the package**:

   ```sh
   python setup.py sdist bdist_wheel
   ```
4. **Publish to PyPI**:

   ```sh
   twine upload dist/*
   ```
5. **Upgrade in services**:

   ```sh
   pip install --upgrade shared-utils
   ```

## Versioning  

We follow **Semantic Versioning (SemVer)**:  

- **MAJOR** – Breaking changes.  
- **MINOR** – New features (backward compatible).  
- **PATCH** – Bug fixes and improvements.  

## release history
**[pypi](https://pypi.org/project/shared-utils-ems/)**