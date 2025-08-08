Contributing
============

Thank you for your interest in contributing to edaflow! This project aims to provide 
comprehensive, educational EDA tools for data scientists and analysts.

🛠️ Development Setup
--------------------

1. **Fork the Repository**::

    git clone https://github.com/YOUR_USERNAME/edaflow.git
    cd edaflow

2. **Create Virtual Environment**::

    python -m venv edaflow_env
    source edaflow_env/bin/activate  # On Windows: edaflow_env\Scripts\activate

3. **Install in Development Mode**::

    pip install -e .
    pip install -r requirements.txt

4. **Install Development Dependencies**::

    pip install pytest pytest-cov

🧪 Testing
----------

Run the test suite before submitting contributions::

    pytest tests/

Run tests with coverage::

    pytest --cov=edaflow tests/

🎯 Contribution Areas
---------------------

**New EDA Functions**
  * Statistical analysis functions
  * Visualization enhancements
  * Data quality assessment tools
  * Advanced pattern detection

**Documentation Improvements**
  * Function docstrings
  * Tutorial examples
  * Best practices guides
  * Educational content

**Code Quality**
  * Performance optimizations
  * Error handling improvements
  * Type hints
  * Code refactoring

**Testing**
  * Unit test coverage
  * Edge case testing
  * Integration tests
  * Performance benchmarks

📝 Coding Standards
-------------------

**Function Design**
  * Follow the established naming pattern: ``verb_object()``
  * Include comprehensive docstrings with parameters and examples
  * Provide educational context in function descriptions
  * Return both processed data and visualizations where appropriate

**Code Style**
  * Follow PEP 8 Python style guidelines
  * Use descriptive variable names
  * Include inline comments for complex logic
  * Maintain consistency with existing code patterns

**Documentation**
  * Write clear, educational docstrings
  * Include practical examples in docstrings
  * Update README.md for new features
  * Add changelog entries for all changes

🔄 Pull Request Process
-----------------------

1. **Create Feature Branch**::

    git checkout -b feature/your-feature-name

2. **Make Your Changes**
   * Write clean, well-documented code
   * Add appropriate tests
   * Update documentation

3. **Test Your Changes**::

    pytest tests/
    # Ensure all tests pass

4. **Commit Changes**::

    git add .
    git commit -m "Add: Brief description of your changes"

5. **Push Branch**::

    git push origin feature/your-feature-name

6. **Submit Pull Request**
   * Provide clear description of changes
   * Reference any related issues
   * Include screenshots for visualizations

📋 Pull Request Checklist
--------------------------

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] Changelog entry added
- [ ] Function includes educational docstring
- [ ] No breaking changes (or clearly documented)

🐛 Bug Reports
--------------

When reporting bugs, please include:

**Environment Information**
  * Python version
  * edaflow version
  * Operating system
  * Package versions (pandas, matplotlib, etc.)

**Bug Description**
  * Clear description of the issue
  * Steps to reproduce
  * Expected vs actual behavior
  * Error messages/tracebacks

**Example Code**::

    # Minimal code example that reproduces the bug
    import edaflow
    import pandas as pd
    
    # Your code here...

💡 Feature Requests
-------------------

We welcome feature requests! Please include:

* **Use Case**: Describe the EDA scenario this would help with
* **Proposed Solution**: How you envision the feature working
* **Educational Value**: How this would help users learn EDA concepts
* **Examples**: Provide examples of when this would be useful

📚 Documentation Contributions
------------------------------

Documentation improvements are highly valued:

* **API Documentation**: Enhance function docstrings
* **Tutorials**: Create educational examples
* **Best Practices**: Share EDA insights and techniques
* **README Updates**: Improve project description and examples

🎓 Educational Focus
--------------------

edaflow has an educational mission. When contributing:

* **Explain the Why**: Help users understand EDA concepts
* **Provide Context**: Explain when and why to use functions
* **Include Examples**: Show practical applications
* **Reference Theory**: Link to statistical concepts when relevant

🤝 Code of Conduct
------------------

This project follows a simple code of conduct:

* **Be Respectful**: Treat all contributors with respect
* **Be Collaborative**: Work together to improve the project
* **Be Educational**: Help others learn and grow
* **Be Patient**: Remember that contributors have different skill levels

🆘 Getting Help
---------------

Need help with your contribution?

* **GitHub Issues**: Ask questions or discuss ideas
* **Documentation**: Check existing docs and examples
* **Code Review**: Maintainers will provide feedback on pull requests

📧 Contact
----------

* **GitHub Issues**: Primary communication channel
* **Email**: For private inquiries (check GitHub profile)
* **Discussions**: Use GitHub Discussions for general questions

Thank you for helping make edaflow better for the data science community! 🚀

---

*Last updated: January 2024*
